#!/usr/bin/env python3
"""TJ-027.1: on-machine deploy agent — stable + preview channels, rollback, resume reconciliation.

Runs on the OPERATOR's machine (not in CI). It polls GHCR channel tags,
deploys the public WEB image only, and never touches the sealed API image:
the sealed backend is operator-managed, verified by trusted-machine offline
sealed acceptance, and delivered through a private channel. This agent can
only place a public web container on the same Docker network as that sealed
API container, so a preview web container proxies /api/ to the same sealed
API — the preview channel cannot bypass sealed acceptance by construction.

Channel model
-------------
- stable: branch ``main``, channel tag ``channel-main``. It accepts ONLY the
  image the ``channel-main`` tag points to. Any request to deploy a
  per-SHA tag, another channel's tag, or any other reference to stable is
  refused and audit-logged. Stable never shares a container name or a host
  port with any preview.
- preview: branch slug -> channel tag ``channel-<slug>`` (slug rules mirror
  .github/workflows/deploy-pipeline.yml). Each preview gets its own
  loopback host port and its own container name, on the same network as the
  sealed API. Previews never deploy to stable and never overwrite each
  other.

Resume is not deployment
------------------------
The CI ``resume-preview`` job only visits the machine's published URL to
resume an idle-paused machine. It deploys nothing. After resume, this
agent's ``reconcile`` pass aligns each channel to its channel tag's latest
image, deploys only changed channels, and is idempotent and re-runnable.
CI green, image pushed, and wake/resume success are NEVER deployment:
only this agent's health-gated deploy, recorded in the deployment log and
the SHA evidence file, counts.

Rollback
--------
Each channel keeps its last healthy (SHA, digest). The agent NEVER deletes
or prunes the last healthy image, so rollback never depends on GHCR being
reachable: on a health failure it rebuilds from the local last-healthy
image and re-verifies health. If no last healthy image exists, or the
rollback re-verification fails, the channel is marked degraded — never
faked healthy.

Capacity
--------
Preview instances are capped by TIANJI_PREVIEW_LIMIT (default 3). Over the
cap, a new preview is refused and logged; existing previews are never
evicted and stable is never touched. This agent does NOT claim full
multi-branch auto-deploy: real capacity must be measured on the machine.

Health gate (mirrors scripts/health_check.py frontend/home contract)
---------------------------------------------------------------------
HTTP 200 + no leak markers + a frontend root element. Leak markers are
the same set health_check.py uses. The full smoke suite (module assets,
gateway /api/ capabilities) stays in health_check.py; the agent gate is
the deploy-time subset the task requires.

Configuration is entirely by environment variable (see Config.from_env).
No secret is ever read from the repository or CI: the optional GHCR
read-only token comes only from the machine's environment.

Usage (on the operator machine, from the repo checkout):
    python scripts/deploy_agent.py reconcile   # one pass (post-resume)
    python scripts/deploy_agent.py poll        # loop forever
    python scripts/deploy_agent.py status      # print channel states

Exit codes for reconcile: 0 when every channel ends healthy or unchanged;
1 when any channel ends failed/degraded, was refused, or rolled back
(operator attention required).
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

IMAGE_REPO_DEFAULT = "ghcr.io/hellomrduan/tianji-web"
NETWORK_DEFAULT = "tianji-private-net"
STABLE_CHANNEL = "channel-main"
STABLE_CONTAINER = "tianji-web-stable"
LEAK_MARKERS = ("traceback", "tianji-private", "private-knowledge", "/root/", "/home/")
SHA_TAG_RE = re.compile(r"^[0-9a-f]{40}$")


def utcnow():
    return datetime.now(timezone.utc).isoformat()


def slugify_branch(branch):
    """Mirror deploy-pipeline.yml channel slug rules exactly."""
    slug = branch.lower()
    slug = re.sub(r"[^a-z0-9_.-]+", "-", slug)
    slug = re.sub(r"^[^a-z0-9_]+", "", slug)
    slug = re.sub(r"[-._]+$", "", slug)
    return slug


def channel_for_branch(branch):
    slug = slugify_branch(branch)
    if not slug:
        raise ValueError("branch %r produces an empty channel slug" % branch)
    return "channel-" + slug


def is_stable_channel(channel):
    return channel == STABLE_CHANNEL


def parse_channel_tag(tag):
    """Return ('stable', None) / ('preview', slug) / None for other tags."""
    if tag == STABLE_CHANNEL:
        return ("stable", None)
    if tag.startswith("channel-") and len(tag) > len("channel-"):
        return ("preview", tag[len("channel-"):])
    return None


def preview_container_name(slug):
    return "tianji-web-preview-" + slug


class Config:
    """Operator configuration, entirely from environment variables."""

    def __init__(self, state_dir, network, stable_port, api_port,
                 preview_port_start, preview_port_end, preview_limit,
                 poll_interval, health_timeout, health_interval,
                 image_repo, ghcr_token, manage_stable=True):
        self.state_dir = Path(state_dir)
        self.network = network
        self.stable_port = stable_port
        self.api_port = api_port
        self.preview_port_start = preview_port_start
        self.preview_port_end = preview_port_end
        self.preview_limit = preview_limit
        self.poll_interval = poll_interval
        self.health_timeout = health_timeout
        self.health_interval = health_interval
        self.image_repo = image_repo
        self.ghcr_token = ghcr_token
        # When false, the agent never touches stable (for operators whose
        # stable service stays compose-managed) and only reconciles previews.
        self.manage_stable = manage_stable

    @classmethod
    def from_env(cls, environ=None):
        env = environ if environ is not None else os.environ
        return cls(
            state_dir=env.get("TIANJI_DEPLOY_STATE_DIR", "tianji-deploy-state"),
            network=env.get("TIANJI_DEPLOY_NETWORK", NETWORK_DEFAULT),
            stable_port=int(env.get("TIANJI_DEPLOY_STABLE_PORT", "8080")),
            api_port=int(env.get("TIANJI_DEPLOY_API_PORT", "8000")),
            preview_port_start=int(env.get("TIANJI_PREVIEW_PORT_START", "18200")),
            preview_port_end=int(env.get("TIANJI_PREVIEW_PORT_END", "18299")),
            preview_limit=int(env.get("TIANJI_PREVIEW_LIMIT", "3")),
            poll_interval=int(env.get("TIANJI_DEPLOY_POLL_INTERVAL", "60")),
            health_timeout=float(env.get("TIANJI_DEPLOY_HEALTH_TIMEOUT", "60")),
            health_interval=float(env.get("TIANJI_DEPLOY_HEALTH_INTERVAL", "2")),
            image_repo=env.get("TIANJI_DEPLOY_IMAGE_REPO", IMAGE_REPO_DEFAULT),
            ghcr_token=env.get("GHCR_TOKEN") or None,
            manage_stable=env.get("TIANJI_DEPLOY_MANAGE_STABLE", "1") not in ("0", "false", "no"),
        )

    @property
    def state_file(self):
        return self.state_dir / "channels.json"

    @property
    def log_file(self):
        return self.state_dir / "deploy.log.jsonl"

    @property
    def evidence_file(self):
        return self.state_dir / "evidence.jsonl"


class ImageRef:
    """An image identity: digest is authoritative; sha is the git commit
    SHA when it could be honestly resolved from a per-SHA tag, else None.
    Never fabricate a SHA from a digest."""

    def __init__(self, digest, sha=None):
        self.digest = digest
        self.sha = sha

    def pinned_for(self, repo):
        return "%s@%s" % (repo, self.digest)


class RegistryClient:
    """GHCR registry API client (public pulls need no token; an optional
    read-only token comes only from the machine environment)."""

    def __init__(self, image_repo, token=None, opener=None):
        self.image_repo = image_repo
        # image_repo looks like ghcr.io/hellomrduan/tianji-web
        _, _, self.path = image_repo.partition("/")
        self.token = token
        self.opener = opener or urllib.request.urlopen

    def _request(self, url, accept):
        req = urllib.request.Request(url, headers={"Accept": accept})
        if self.token:
            req.add_header("Authorization", "Bearer " + self.token)
        with self.opener(req, timeout=30) as response:
            return response.headers, response.read()

    def get_digest(self, tag):
        url = "https://ghcr.io/v2/%s/manifests/%s" % (self.path, tag)
        headers, _ = self._request(url, (
            "application/vnd.oci.image.manifest.v1+json,"
            "application/vnd.docker.distribution.manifest.v2+json"))
        digest = headers.get("Docker-Content-Digest")
        if not digest:
            raise ValueError("registry did not return a digest for tag %s" % tag)
        return digest

    def list_tags(self):
        tags = []
        url = "https://ghcr.io/v2/%s/tags/list?n=100" % self.path
        while url:
            req = urllib.request.Request(url, headers={
                "Accept": "application/json"})
            if self.token:
                req.add_header("Authorization", "Bearer " + self.token)
            with self.opener(req, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
                tags.extend(payload.get("tags") or [])
                link = response.headers.get("Link", "")
                nxt = None
                for part in link.split(","):
                    if 'rel="next"' in part:
                        nxt = part.split(";")[0].strip().strip("<>")
                url = nxt
        return tags

    def resolve_channel(self, channel_tag):
        """Resolve a channel tag to (digest, sha-or-None). The SHA is found
        honestly: a per-SHA tag whose digest equals the channel digest."""
        digest = self.get_digest(channel_tag)
        sha = None
        try:
            for tag in self.list_tags():
                if not SHA_TAG_RE.match(tag):
                    continue
                try:
                    if self.get_digest(tag) == digest:
                        sha = tag
                        break
                except (OSError, ValueError):
                    continue
        except (OSError, ValueError):
            # Tag listing is best-effort: the digest stays authoritative.
            pass
        return ImageRef(digest=digest, sha=sha)


class DockerClient:
    """Thin docker CLI wrapper. NOTE: this class has no image-remove or
    image-prune operation by design — the last healthy image is never
    deleted, so rollback never depends on GHCR reachability."""

    def __init__(self, runner=None):
        self.runner = runner or self._default_runner

    @staticmethod
    def _default_runner(args):
        return subprocess.run(args, capture_output=True, text=True, timeout=120)

    def _run(self, args):
        return self.runner(args)

    def pull(self, ref):
        result = self._run(["docker", "pull", ref])
        return result.returncode == 0, (result.stdout + result.stderr).strip()

    def image_exists(self, ref):
        result = self._run(["docker", "image", "inspect", ref])
        return result.returncode == 0

    def container_status(self, name):
        result = self._run(["docker", "inspect", name])
        if result.returncode != 0:
            return None
        try:
            data = json.loads(result.stdout)
        except ValueError:
            return None
        if not data:
            return None
        state = data[0].get("State") or {}
        return {
            "running": bool(state.get("Running")),
            "status": state.get("Status"),
            "health": (state.get("Health") or {}).get("Status"),
        }

    def list_containers(self):
        """Return [{name, ports}] for running containers (port mappings as
        'ip:host_port->container_port' strings when parseable)."""
        result = self._run(["docker", "ps", "--format", "{{.Names}} {{.Ports}}"])
        out = []
        if result.returncode != 0:
            return out
        for line in result.stdout.splitlines():
            parts = line.split(None, 1)
            if not parts:
                continue
            ports = parts[1] if len(parts) > 1 else ""
            out.append({"name": parts[0], "ports": ports})
        return out

    def run_container(self, name, image_ref, host_port, network):
        result = self._run([
            "docker", "run", "-d",
            "--name", name,
            "--network", network,
            "--publish", "127.0.0.1:%d:8080" % host_port,
            "--restart", "unless-stopped",
            image_ref,
        ])
        return result.returncode == 0, (result.stdout + result.stderr).strip()

    def remove_container(self, name):
        result = self._run(["docker", "rm", "-f", name])
        return result.returncode == 0

    def observe_api_container(self):
        """Read-only observation of the sealed API container, if present on
        this machine. Returns {name, image} or None. The agent never
        manages the API container; this is version reporting only."""
        for entry in self.list_containers():
            if "tianji-api" in entry["name"]:
                result = self._run(["docker", "inspect", entry["name"]])
                if result.returncode != 0:
                    return {"name": entry["name"], "image": None}
                try:
                    data = json.loads(result.stdout)
                    image = (data[0].get("Config") or {}).get("Image")
                except (ValueError, IndexError):
                    image = None
                return {"name": entry["name"], "image": image}
        return None


class HttpClient:
    """Minimal HTTP GET client (urllib, stdlib only)."""

    def __init__(self, opener=None):
        self.opener = opener or urllib.request.urlopen

    def get(self, url, timeout=10):
        try:
            with self.opener(url, timeout=timeout) as response:
                body = response.read(2 * 1024 * 1024 + 1)
                return response.status, body, response.headers.get("Content-Type", "")
        except urllib.error.HTTPError as exc:
            return exc.code, b"", ""
        except OSError:
            return None, b"", ""


class _RootParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.has_root = False

    def handle_starttag(self, tag, attrs):
        if tag == "div" and dict(attrs).get("id") == "root":
            self.has_root = True


def parse_host_ports(ports_string):
    """Parse `docker ps` Ports output into a set of host ports."""
    ports = set()
    for mapping in (ports_string or "").split(","):
        mapping = mapping.strip()
        if "->" not in mapping:
            continue
        left = mapping.split("->")[0]
        if ":" in left:
            try:
                ports.add(int(left.rsplit(":", 1)[1]))
            except ValueError:
                continue
    return ports


def frontend_health_ok(base_url, http_client):
    """Deploy-time health gate: HTTP 200 + no leak markers + frontend root.
    Mirrors scripts/health_check.py frontend/home contract (subset)."""
    status, body, ctype = http_client.get(base_url.rstrip("/") + "/")
    if status != 200:
        return False, "HTTP %s" % status
    if "text/html" not in (ctype or "").lower():
        return False, "frontend did not serve HTML"
    text = body.decode("utf-8", errors="replace")
    lowered = text.lower()
    if any(marker in lowered for marker in LEAK_MARKERS):
        return False, "private/internal marker in response"
    parser = _RootParser()
    parser.feed(text)
    if not parser.has_root:
        return False, "missing app root"
    return True, "OK"


class DeployAgent:
    """Channel reconciler. All external effects go through the injected
    registry/docker/http clients so tests can mock them completely."""

    def __init__(self, config, registry=None, docker=None, http_client=None):
        self.config = config
        self.registry = registry or RegistryClient(config.image_repo, config.ghcr_token)
        self.docker = docker or DockerClient()
        self.http = http_client or HttpClient()
        self.config.state_dir.mkdir(parents=True, exist_ok=True)
        self.state = self._load_state()

    # -- state, log, evidence -------------------------------------------

    def _load_state(self):
        if not self.config.state_file.exists():
            return {"channels": {}}
        try:
            data = json.loads(self.config.state_file.read_text(encoding="utf-8"))
            if isinstance(data, dict) and isinstance(data.get("channels"), dict):
                return data
        except (OSError, ValueError):
            pass
        return {"channels": {}}

    def _save_state(self):
        tmp = self.config.state_file.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.state, indent=2, sort_keys=True),
                       encoding="utf-8")
        os.replace(tmp, self.config.state_file)

    def _log(self, channel, action, sha, digest, outcome, detail=""):
        record = {
            "ts": utcnow(), "channel": channel, "action": action,
            "sha": sha, "digest": digest, "outcome": outcome, "detail": detail,
        }
        with open(self.config.log_file, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, sort_keys=True) + "\n")
        return record

    def _evidence(self, channel, sha, digest, image_ref, outcome):
        record = {
            "ts": utcnow(), "channel": channel, "sha": sha, "digest": digest,
            "image": image_ref, "outcome": outcome,
        }
        with open(self.config.evidence_file, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, sort_keys=True) + "\n")
        return record

    # -- channel helpers --------------------------------------------------

    def _channel_state(self, channel):
        return self.state["channels"].get(channel)

    def _used_ports(self):
        used = {self.config.stable_port, self.config.api_port}
        for entry in self.state["channels"].values():
            if entry.get("port"):
                used.add(entry["port"])
        for entry in self.docker.list_containers():
            used |= parse_host_ports(entry["ports"])
        return used

    def allocate_port(self):
        used = self._used_ports()
        port = self.config.preview_port_start
        while port <= self.config.preview_port_end:
            if port not in used:
                return port
            port += 1
        return None

    def _container_name(self, channel):
        if is_stable_channel(channel):
            return STABLE_CONTAINER
        parsed = parse_channel_tag(channel)
        return preview_container_name(parsed[1]) if parsed else None

    def _port_for(self, channel):
        if is_stable_channel(channel):
            return self.config.stable_port
        entry = self._channel_state(channel)
        if entry and entry.get("port"):
            return entry["port"]
        return self.allocate_port()

    # -- health gate -------------------------------------------------------

    def _wait_healthy(self, channel, port):
        deadline = time.time() + self.config.health_timeout
        last_detail = "timeout"
        while time.time() < deadline:
            status = self.docker.container_status(self._container_name(channel))
            if status is None:
                return False, "container missing"
            if not status["running"]:
                return False, "container not running (%s)" % status["status"]
            if status["health"] == "unhealthy":
                return False, "container unhealthy"
            ok, detail = frontend_health_ok(
                "http://127.0.0.1:%d" % port, self.http)
            if ok:
                return True, "OK"
            last_detail = detail
            time.sleep(self.config.health_interval)
        return False, last_detail

    # -- deploy / rollback ---------------------------------------------------

    def deploy(self, channel, target, target_tag):
        """Deploy target ImageRef to channel. target_tag must be the
        channel's own channel tag; anything else is refused (this is the
        stable-protection and cross-channel-isolation mechanism)."""
        parsed = parse_channel_tag(channel)
        if parsed is None:
            self._log(channel, "refuse", target.sha, target.digest,
                      "refused", "not a channel tag")
            return "refused"
        expected_tag = channel  # the channel tag IS the channel identity
        if target_tag != expected_tag:
            self._log(channel, "refuse", target.sha, target.digest,
                      "refused",
                      "target tag %s does not match channel %s"
                      % (target_tag, channel))
            return "refused"
        kind = parsed[0]
        entry = self._channel_state(channel)
        if kind == "preview" and entry is None:
            active = sum(1 for e in self.state["channels"].values()
                         if e.get("kind") == "preview")
            if active >= self.config.preview_limit:
                self._log(channel, "refuse", target.sha, target.digest,
                          "capacity_refused",
                          "preview limit %d reached; refusing new preview, "
                          "existing previews untouched, stable untouched"
                          % self.config.preview_limit)
                return "capacity_refused"
        port = self._port_for(channel)
        if port is None:
            self._log(channel, "refuse", target.sha, target.digest,
                      "port_exhausted",
                      "no free preview port in %d-%d"
                      % (self.config.preview_port_start,
                         self.config.preview_port_end))
            return "port_exhausted"
        container = self._container_name(channel)
        image_ref = target.pinned_for(self.config.image_repo)

        # Fail fast if another container squats the target port: never
        # destroy a healthy deployment to fight for a port.
        for live in self.docker.list_containers():
            if live["name"] != container and port in parse_host_ports(live["ports"]):
                self._log(channel, "deploy", target.sha, target.digest,
                          "failed",
                          "port %d held by container %s" % (port, live["name"]))
                return "failed"

        # Pull first: a pull failure must leave the old container running.
        ok, detail = self.docker.pull(image_ref)
        if not ok:
            self._log(channel, "deploy", target.sha, target.digest,
                      "failed", "pull failed: %s" % detail)
            return "failed"
        old = self.docker.container_status(container)
        if old is not None:
            self.docker.remove_container(container)
        ok, detail = self.docker.run_container(container, image_ref, port,
                                                self.config.network)
        if not ok:
            self._log(channel, "deploy", target.sha, target.digest,
                      "failed", "container start failed: %s" % detail)
            return self._rollback(channel, entry, port)
        healthy, detail = self._wait_healthy(channel, port)
        if healthy:
            new_entry = {
                "kind": kind,
                "slug": parsed[1],
                "sha": target.sha,
                "digest": target.digest,
                "healthy": True,
                "updated_at": utcnow(),
                "last_healthy_sha": target.sha,
                "last_healthy_digest": target.digest,
                "port": port,
                "container": container,
            }
            self.state["channels"][channel] = new_entry
            self._save_state()
            self._log(channel, "deploy", target.sha, target.digest,
                      "healthy", "health gate passed")
            self._evidence(channel, target.sha, target.digest, image_ref,
                           "deployed")
            return "deployed"
        self._log(channel, "deploy", target.sha, target.digest,
                  "failed", "health gate failed: %s" % detail)
        return self._rollback(channel, entry, port)

    def _rollback(self, channel, entry, port):
        """Rebuild from the local last-healthy image. Never pulls: rollback
        must not depend on GHCR reachability, and the last-healthy image is
        never deleted by this agent."""
        container = self._container_name(channel)
        if entry is None or not entry.get("last_healthy_digest"):
            self._log(channel, "rollback", None, None, "failed",
                      "no last healthy image; channel left degraded")
            if entry is not None:
                entry["healthy"] = False
                self._save_state()
            return "degraded"
        digest = entry["last_healthy_digest"]
        image_ref = "%s@%s" % (self.config.image_repo, digest)
        if not self.docker.image_exists(image_ref):
            self._log(channel, "rollback", entry.get("last_healthy_sha"),
                      digest, "failed",
                      "last healthy image missing locally; refusing to pull")
            entry["healthy"] = False
            self._save_state()
            return "degraded"
        self.docker.remove_container(container)
        ok, detail = self.docker.run_container(container, image_ref, port,
                                                self.config.network)
        if not ok:
            self._log(channel, "rollback", entry.get("last_healthy_sha"),
                      digest, "failed", "container start failed: %s" % detail)
            entry["healthy"] = False
            self._save_state()
            return "degraded"
        healthy, detail = self._wait_healthy(channel, port)
        if healthy:
            entry["healthy"] = True
            entry["updated_at"] = utcnow()
            entry["sha"] = entry.get("last_healthy_sha")
            entry["digest"] = digest
            self._save_state()
            self._log(channel, "rollback", entry.get("last_healthy_sha"),
                      digest, "rolled_back", "health gate passed on rollback")
            self._evidence(channel, entry.get("last_healthy_sha"), digest,
                           image_ref, "rolled_back")
            return "rolled_back"
        self._log(channel, "rollback", entry.get("last_healthy_sha"), digest,
                  "failed", "rollback health gate failed: %s" % detail)
        entry["healthy"] = False
        self._save_state()
        return "degraded"

    # -- reconcile ------------------------------------------------------------

    def reconcile_channel(self, channel):
        """One channel, one pass. Returns an outcome string."""
        try:
            target = self.registry.resolve_channel(channel)
        except (OSError, ValueError) as exc:
            self._log(channel, "resolve", None, None, "failed", str(exc))
            return "failed"
        entry = self._channel_state(channel)
        if (entry is not None and entry.get("healthy")
                and entry.get("digest") == target.digest):
            # Unchanged only if the container is actually running: a
            # crashed or stopped container must be revived (this is what
            # makes post-resume reconciliation self-healing).
            status = self.docker.container_status(self._container_name(channel))
            if status is not None and status["running"]:
                self._log(channel, "reconcile", target.sha, target.digest,
                          "unchanged", "already at target digest and running")
                return "unchanged"
            self._log(channel, "reconcile", target.sha, target.digest,
                      "revive", "state matches target but container not running")
        return self.deploy(channel, target, channel)

    def reconcile_all(self):
        """Discover channel tags, then align each channel. Stable first.
        Returns {channel: outcome}."""
        outcomes = {}
        try:
            tags = self.registry.list_tags()
        except (OSError, ValueError) as exc:
            self._log("agent", "discover", None, None, "failed", str(exc))
            return {"agent": "failed"}
        channels = [t for t in tags if parse_channel_tag(t) is not None]
        if not self.config.manage_stable:
            self._log(STABLE_CHANNEL, "reconcile", None, None, "skipped",
                      "stable management disabled by operator "
                      "(TIANJI_DEPLOY_MANAGE_STABLE=0)")
            outcomes[STABLE_CHANNEL] = "skipped"
        elif STABLE_CHANNEL not in channels:
            self._log(STABLE_CHANNEL, "discover", None, None, "failed",
                      "channel-main tag missing; stable left untouched")
            outcomes[STABLE_CHANNEL] = "failed"
        else:
            outcomes[STABLE_CHANNEL] = self.reconcile_channel(STABLE_CHANNEL)
        for channel in sorted(channels):
            if channel == STABLE_CHANNEL:
                continue
            outcomes[channel] = self.reconcile_channel(channel)
        # Known previews whose channel tag vanished are left running and
        # logged, never auto-deleted (operator prunes manually).
        known = set(self.state["channels"])
        for channel in sorted(known - set(channels)):
            self._log(channel, "reconcile", None, None, "stale",
                      "channel tag vanished; preview left running")
            outcomes[channel] = "stale"
        return outcomes

    def status(self):
        api = self.docker.observe_api_container()
        return {
            "channels": self.state["channels"],
            "backend_observed": api,
            "backend_note": ("sealed API is operator-managed; this agent "
                             "only observes its container image when present "
                             "on this machine and never deploys it"),
        }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="TJ-027.1 on-machine deploy agent (public web only).")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("reconcile", help="one reconcile pass (post-resume)")
    sub.add_parser("poll", help="loop reconcile forever")
    sub.add_parser("status", help="print channel states as JSON")
    args = parser.parse_args(argv)
    config = Config.from_env()
    agent = DeployAgent(config)
    if args.command == "status":
        print(json.dumps(agent.status(), indent=2, sort_keys=True))
        return 0
    if args.command == "reconcile":
        outcomes = agent.reconcile_all()
        print(json.dumps(outcomes, indent=2, sort_keys=True))
        bad = {"failed", "degraded", "refused", "capacity_refused",
               "port_exhausted", "rolled_back"}
        return 1 if any(o in bad for o in outcomes.values()) else 0
    # poll
    try:
        while True:
            try:
                outcomes = agent.reconcile_all()
                print(json.dumps(outcomes, sort_keys=True))
            except Exception as exc:  # never crash the daemon on one bad pass
                agent._log("agent", "poll", None, None, "failed", str(exc))
            time.sleep(config.poll_interval)
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    sys.exit(main())
