"""TJ-027.1: deploy agent unit + simulation tests.

Unit tests use injected fakes for registry/docker/HTTP: no docker daemon,
no network, no real machine. The SimulationTests class drives a full
reconcile loop against fakes — it is explicitly a SIMULATION and its pass
is NOT real-machine acceptance. Real-machine acceptance (dev-branch push
-> preview update with stable unchanged; main push -> stable update with
previews unaffected; induced failure -> auto-rollback with traceable logs)
must still run on the operator machine and return SHA/digest evidence.
"""
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import deploy_agent
from deploy_agent import (
    Config, DeployAgent, ImageRef, RegistryClient,
    channel_for_branch, frontend_health_ok, is_stable_channel,
    parse_channel_tag, slugify_branch,
)

REPO = "ghcr.io/hellomrduan/tianji-web"
SHA_A = "a" * 40
SHA_B = "b" * 40
SHA_C = "c" * 40
DIGEST_A = "sha256:aaaa"
DIGEST_B = "sha256:bbbb"
DIGEST_C = "sha256:cccc"
HEALTHY_HTML = b'<html><head></head><body><div id="root"></div></body></html>'


def ref(digest, sha):
    return ImageRef(digest=digest, sha=sha)


class FakeRegistry:
    def __init__(self, tags):
        self.tags = dict(tags)
        self.calls = []

    def get_digest(self, tag):
        self.calls.append(("get_digest", tag))
        if tag not in self.tags:
            raise ValueError("tag missing: %s" % tag)
        return self.tags[tag].digest

    def list_tags(self):
        self.calls.append(("list_tags",))
        return sorted(self.tags)

    def resolve_channel(self, channel_tag):
        self.calls.append(("resolve_channel", channel_tag))
        if channel_tag not in self.tags:
            raise ValueError("tag missing: %s" % channel_tag)
        return self.tags[channel_tag]


class FakeDocker:
    def __init__(self):
        self.containers = {}
        self.images = set()
        self.commands = []
        self.pull_fail = set()
        self.run_fail = set()
        self.api = None

    def pull(self, image_ref):
        self.commands.append(["pull", image_ref])
        if image_ref in self.pull_fail:
            return False, "pull failed (fake)"
        self.images.add(image_ref)
        return True, ""

    def image_exists(self, image_ref):
        self.commands.append(["image_exists", image_ref])
        return image_ref in self.images

    def container_status(self, name):
        entry = self.containers.get(name)
        if entry is None:
            return None
        return {"running": entry["running"],
                "status": "running" if entry["running"] else "exited",
                "health": entry.get("health")}

    def list_containers(self):
        out = []
        for name, entry in self.containers.items():
            if not entry["running"]:
                continue
            ports = ""
            if entry.get("port"):
                ports = "127.0.0.1:%d->8080/tcp" % entry["port"]
            out.append({"name": name, "ports": ports})
        return out

    def run_container(self, name, image_ref, host_port, network):
        self.commands.append(["run", name, image_ref, str(host_port), network])
        if name in self.run_fail:
            return False, "run failed (fake)"
        self.containers[name] = {"running": True, "health": None,
                                 "image": image_ref, "port": host_port}
        return True, "fake-id"

    def remove_container(self, name):
        self.commands.append(["rm", name])
        self.containers.pop(name, None)
        return True

    def observe_api_container(self):
        return self.api


class FakeHttp:
    """Health outcomes follow the image currently on the port when a docker
    fake is attached; routes override per port for gate unit tests."""

    def __init__(self, docker=None):
        self.docker = docker
        self.routes = {}
        self.fail_images = set()

    def get(self, url, timeout=10):
        match = re.search(r":(\d+)", url)
        port = int(match.group(1)) if match else None
        if port in self.routes:
            return self.routes[port]
        if self.docker is not None:
            for entry in self.docker.containers.values():
                if entry.get("port") == port and entry["running"]:
                    if entry["image"] in self.fail_images:
                        return 500, b"error", "text/plain"
                    break
        return 200, HEALTHY_HTML, "text/html"


def make_agent(tmp, tags, env_extra=None, docker=None, http_client=None):
    env = {
        "TIANJI_DEPLOY_STATE_DIR": str(tmp),
        "TIANJI_DEPLOY_HEALTH_TIMEOUT": "1",
        "TIANJI_DEPLOY_HEALTH_INTERVAL": "0.01",
        "TIANJI_DEPLOY_POLL_INTERVAL": "60",
    }
    if env_extra:
        env.update(env_extra)
    config = Config.from_env(env)
    registry = FakeRegistry(tags)
    docker = docker or FakeDocker()
    http_client = http_client or FakeHttp(docker)
    agent = DeployAgent(config, registry=registry, docker=docker,
                        http_client=http_client)
    return agent, registry, docker, http_client


def read_jsonl(path):
    if not Path(path).exists():
        return []
    return [json.loads(line) for line in Path(path).read_text().splitlines()
            if line.strip()]


class ChannelTests(unittest.TestCase):
    def test_slugify_mirrors_pipeline(self):
        self.assertEqual(slugify_branch("main"), "main")
        self.assertEqual(slugify_branch("Feature/Foo_Bar"), "feature-foo_bar")
        self.assertEqual(slugify_branch("UPPER"), "upper")
        self.assertEqual(slugify_branch("a..b--"), "a..b")

    def test_channel_for_branch(self):
        self.assertEqual(channel_for_branch("main"), "channel-main")
        self.assertEqual(channel_for_branch("feature/x"), "channel-feature-x")

    def test_channel_for_branch_empty_raises(self):
        with self.assertRaises(ValueError):
            channel_for_branch("///")

    def test_parse_channel_tag(self):
        self.assertEqual(parse_channel_tag("channel-main"), ("stable", None))
        self.assertEqual(parse_channel_tag("channel-foo"), ("preview", "foo"))
        self.assertIsNone(parse_channel_tag("channel-"))
        self.assertIsNone(parse_channel_tag("latest"))
        self.assertIsNone(parse_channel_tag("a" * 40))

    def test_is_stable_channel(self):
        self.assertTrue(is_stable_channel("channel-main"))
        self.assertFalse(is_stable_channel("channel-foo"))


class StableProtectionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def test_stable_refuses_per_sha_tag(self):
        agent, _, docker, _ = make_agent(
            self.tmp.name, {"channel-main": ref(DIGEST_A, SHA_A)})
        outcome = agent.deploy("channel-main", ref(DIGEST_B, SHA_B), SHA_B)
        self.assertEqual(outcome, "refused")
        self.assertFalse(any(c[0] == "run" and c[1] == "tianji-web-stable"
                             for c in docker.commands))
        logs = read_jsonl(agent.config.log_file)
        self.assertTrue(any(r["outcome"] == "refused" for r in logs))

    def test_stable_refuses_other_channel_tag(self):
        agent, _, docker, _ = make_agent(
            self.tmp.name, {"channel-main": ref(DIGEST_A, SHA_A)})
        outcome = agent.deploy("channel-main", ref(DIGEST_B, SHA_B), "channel-foo")
        self.assertEqual(outcome, "refused")
        self.assertNotIn("tianji-web-stable", docker.containers)

    def test_preview_refuses_other_channel_tag(self):
        agent, _, docker, _ = make_agent(
            self.tmp.name, {"channel-foo": ref(DIGEST_A, SHA_A)})
        outcome = agent.deploy("channel-foo", ref(DIGEST_B, SHA_B), "channel-bar")
        self.assertEqual(outcome, "refused")
        self.assertNotIn("tianji-web-preview-foo", docker.containers)

    def test_stable_accepts_own_channel_tag(self):
        agent, _, docker, _ = make_agent(
            self.tmp.name, {"channel-main": ref(DIGEST_A, SHA_A)})
        outcome = agent.deploy("channel-main", ref(DIGEST_A, SHA_A), "channel-main")
        self.assertEqual(outcome, "deployed")
        entry = docker.containers["tianji-web-stable"]
        self.assertEqual(entry["port"], 8080)
        state = agent.state["channels"]["channel-main"]
        self.assertEqual(state["sha"], SHA_A)
        self.assertEqual(state["digest"], DIGEST_A)
        self.assertTrue(state["healthy"])

    def test_preview_accepts_own_channel_tag(self):
        agent, _, docker, _ = make_agent(
            self.tmp.name, {"channel-foo": ref(DIGEST_A, SHA_A)})
        outcome = agent.deploy("channel-foo", ref(DIGEST_A, SHA_A), "channel-foo")
        self.assertEqual(outcome, "deployed")
        entry = docker.containers["tianji-web-preview-foo"]
        self.assertEqual(entry["port"], 18200)
        self.assertNotEqual(entry["port"], 8080)


class PortTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def test_preview_first_free_port(self):
        agent, _, docker, _ = make_agent(
            self.tmp.name, {"channel-foo": ref(DIGEST_A, SHA_A),
                            "channel-bar": ref(DIGEST_B, SHA_B)})
        agent.deploy("channel-foo", ref(DIGEST_A, SHA_A), "channel-foo")
        agent.deploy("channel-bar", ref(DIGEST_B, SHA_B), "channel-bar")
        self.assertEqual(docker.containers["tianji-web-preview-foo"]["port"], 18200)
        self.assertEqual(docker.containers["tianji-web-preview-bar"]["port"], 18201)

    def test_preview_never_takes_stable_or_api_port(self):
        agent, _, docker, _ = make_agent(
            self.tmp.name, {"channel-foo": ref(DIGEST_A, SHA_A)},
            env_extra={"TIANJI_DEPLOY_STABLE_PORT": "8001",
                       "TIANJI_PREVIEW_PORT_START": "8000",
                       "TIANJI_PREVIEW_PORT_END": "8002"})
        agent.deploy("channel-foo", ref(DIGEST_A, SHA_A), "channel-foo")
        # 8000 is the API port, 8001 is stable: first free must be 8002.
        self.assertEqual(docker.containers["tianji-web-preview-foo"]["port"], 8002)

    def test_port_conflict_aborts_before_destroying_old(self):
        agent, _, docker, _ = make_agent(
            self.tmp.name, {"channel-foo": ref(DIGEST_A, SHA_A)})
        agent.deploy("channel-foo", ref(DIGEST_A, SHA_A), "channel-foo")
        # A squatter grabs the preview's port from outside the agent.
        docker.containers["squatter"] = {"running": True, "health": None,
                                         "image": "other:latest", "port": 18200}
        # Move the agent's container off the port in the fake so the
        # squatter is the only holder, then stop it to simulate the
        # conflict: actually keep the agent container AND the squatter
        # both mapped — the agent must refuse before removing its own.
        outcome = agent.deploy("channel-foo", ref(DIGEST_B, SHA_B), "channel-foo")
        self.assertEqual(outcome, "failed")
        self.assertIn("tianji-web-preview-foo", docker.containers)
        self.assertEqual(docker.containers["tianji-web-preview-foo"]["image"],
                         "%s@%s" % (REPO, DIGEST_A))


class CapacityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def _seed_previews(self, agent, count):
        for i in range(count):
            slug = "p%d" % i
            agent.state["channels"]["channel-" + slug] = {
                "kind": "preview", "slug": slug, "sha": SHA_A,
                "digest": DIGEST_A, "healthy": True, "updated_at": "t",
                "last_healthy_sha": SHA_A, "last_healthy_digest": DIGEST_A,
                "port": 18200 + i, "container": "tianji-web-preview-" + slug,
            }
        agent._save_state()

    def test_capacity_refusal(self):
        agent, _, docker, _ = make_agent(
            self.tmp.name, {"channel-new": ref(DIGEST_B, SHA_B)})
        self._seed_previews(agent, 3)
        outcome = agent.deploy("channel-new", ref(DIGEST_B, SHA_B), "channel-new")
        self.assertEqual(outcome, "capacity_refused")
        self.assertNotIn("tianji-web-preview-new", docker.containers)
        logs = read_jsonl(agent.config.log_file)
        self.assertTrue(any(r["outcome"] == "capacity_refused" for r in logs))

    def test_capacity_counts_only_previews(self):
        agent, _, docker, _ = make_agent(
            self.tmp.name, {"channel-new": ref(DIGEST_B, SHA_B)})
        agent.state["channels"]["channel-main"] = {
            "kind": "stable", "slug": None, "sha": SHA_A, "digest": DIGEST_A,
            "healthy": True, "updated_at": "t", "last_healthy_sha": SHA_A,
            "last_healthy_digest": DIGEST_A, "port": 8080,
            "container": "tianji-web-stable",
        }
        self._seed_previews(agent, 2)
        outcome = agent.deploy("channel-new", ref(DIGEST_B, SHA_B), "channel-new")
        self.assertEqual(outcome, "deployed")

    def test_port_exhaustion_refusal(self):
        agent, _, docker, _ = make_agent(
            self.tmp.name, {"channel-foo": ref(DIGEST_A, SHA_A)},
            env_extra={"TIANJI_PREVIEW_PORT_START": "18200",
                       "TIANJI_PREVIEW_PORT_END": "18200",
                       "TIANJI_PREVIEW_LIMIT": "10"})
        docker.containers["squatter"] = {"running": True, "health": None,
                                         "image": "other:latest", "port": 18200}
        outcome = agent.deploy("channel-foo", ref(DIGEST_A, SHA_A), "channel-foo")
        self.assertEqual(outcome, "port_exhausted")


class RollbackTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def _seed_healthy_preview(self, agent, docker):
        agent.state["channels"]["channel-foo"] = {
            "kind": "preview", "slug": "foo", "sha": SHA_A, "digest": DIGEST_A,
            "healthy": True, "updated_at": "t", "last_healthy_sha": SHA_A,
            "last_healthy_digest": DIGEST_A, "port": 18200,
            "container": "tianji-web-preview-foo",
        }
        agent._save_state()
        docker.containers["tianji-web-preview-foo"] = {
            "running": True, "health": None,
            "image": "%s@%s" % (REPO, DIGEST_A), "port": 18200}
        docker.images.add("%s@%s" % (REPO, DIGEST_A))

    def test_rollback_on_health_failure(self):
        agent, _, docker, http_client = make_agent(
            self.tmp.name, {"channel-foo": ref(DIGEST_B, SHA_B)})
        self._seed_healthy_preview(agent, docker)
        http_client.fail_images.add("%s@%s" % (REPO, DIGEST_B))
        outcome = agent.deploy("channel-foo", ref(DIGEST_B, SHA_B), "channel-foo")
        self.assertEqual(outcome, "rolled_back")
        state = agent.state["channels"]["channel-foo"]
        self.assertTrue(state["healthy"])
        self.assertEqual(state["digest"], DIGEST_A)
        self.assertEqual(state["sha"], SHA_A)
        # Rollback never pulls: no pull for the old image in this deploy.
        pulls = [c[1] for c in docker.commands if c[0] == "pull"]
        self.assertNotIn("%s@%s" % (REPO, DIGEST_A), pulls)
        logs = read_jsonl(agent.config.log_file)
        self.assertTrue(any(r["outcome"] == "rolled_back" for r in logs))

    def test_rollback_image_missing_degraded(self):
        agent, _, docker, http_client = make_agent(
            self.tmp.name, {"channel-foo": ref(DIGEST_B, SHA_B)})
        self._seed_healthy_preview(agent, docker)
        docker.images.discard("%s@%s" % (REPO, DIGEST_A))
        http_client.fail_images.add("%s@%s" % (REPO, DIGEST_B))
        outcome = agent.deploy("channel-foo", ref(DIGEST_B, SHA_B), "channel-foo")
        self.assertEqual(outcome, "degraded")
        # No pull is issued for the missing rollback image.
        pulls = [c[1] for c in docker.commands if c[0] == "pull"]
        self.assertNotIn("%s@%s" % (REPO, DIGEST_A), pulls)
        self.assertFalse(agent.state["channels"]["channel-foo"]["healthy"])

    def test_no_history_failure_degraded(self):
        agent, _, docker, http_client = make_agent(
            self.tmp.name, {"channel-foo": ref(DIGEST_B, SHA_B)})
        http_client.fail_images.add("%s@%s" % (REPO, DIGEST_B))
        outcome = agent.deploy("channel-foo", ref(DIGEST_B, SHA_B), "channel-foo")
        self.assertEqual(outcome, "degraded")
        self.assertNotIn("channel-foo", agent.state["channels"])

    def test_no_prune_or_rmi_anywhere(self):
        agent, _, docker, http_client = make_agent(
            self.tmp.name, {"channel-foo": ref(DIGEST_B, SHA_B)})
        self._seed_healthy_preview(agent, docker)
        http_client.fail_images.add("%s@%s" % (REPO, DIGEST_B))
        agent.deploy("channel-foo", ref(DIGEST_B, SHA_B), "channel-foo")
        tokens = [token for cmd in docker.commands for token in cmd]
        self.assertNotIn("rmi", tokens)
        self.assertNotIn("prune", tokens)


class ReconcileTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def test_reconcile_unchanged_noop(self):
        agent, _, docker, _ = make_agent(
            self.tmp.name, {"channel-main": ref(DIGEST_A, SHA_A)})
        agent.deploy("channel-main", ref(DIGEST_A, SHA_A), "channel-main")
        before = list(docker.commands)
        outcome = agent.reconcile_channel("channel-main")
        self.assertEqual(outcome, "unchanged")
        self.assertEqual(docker.commands, before)

    def test_reconcile_revives_stopped_container(self):
        agent, _, docker, _ = make_agent(
            self.tmp.name, {"channel-main": ref(DIGEST_A, SHA_A)})
        agent.deploy("channel-main", ref(DIGEST_A, SHA_A), "channel-main")
        docker.containers["tianji-web-stable"]["running"] = False
        outcome = agent.reconcile_channel("channel-main")
        self.assertEqual(outcome, "deployed")
        self.assertTrue(docker.containers["tianji-web-stable"]["running"])

    def test_reconcile_only_changed(self):
        agent, _, docker, _ = make_agent(
            self.tmp.name, {"channel-main": ref(DIGEST_A, SHA_A),
                            "channel-foo": ref(DIGEST_A, SHA_A),
                            "channel-bar": ref(DIGEST_A, SHA_A)})
        agent.reconcile_all()
        docker.commands.clear()
        agent.registry.tags["channel-foo"] = ref(DIGEST_B, SHA_B)
        outcomes = agent.reconcile_all()
        self.assertEqual(outcomes["channel-foo"], "deployed")
        self.assertEqual(outcomes["channel-bar"], "unchanged")
        self.assertEqual(outcomes["channel-main"], "unchanged")
        runs = [c for c in docker.commands if c[0] == "run"]
        self.assertEqual(len(runs), 1)
        self.assertEqual(runs[0][1], "tianji-web-preview-foo")

    def test_reconcile_stable_missing_tag(self):
        agent, _, docker, _ = make_agent(
            self.tmp.name, {"channel-foo": ref(DIGEST_A, SHA_A)})
        outcomes = agent.reconcile_all()
        self.assertEqual(outcomes["channel-main"], "failed")
        self.assertNotIn("tianji-web-stable", docker.containers)

    def test_reconcile_stale_preview_left_running(self):
        agent, _, docker, _ = make_agent(
            self.tmp.name, {"channel-main": ref(DIGEST_A, SHA_A),
                            "channel-foo": ref(DIGEST_A, SHA_A)})
        agent.reconcile_all()
        del agent.registry.tags["channel-foo"]
        outcomes = agent.reconcile_all()
        self.assertEqual(outcomes["channel-foo"], "stale")
        self.assertIn("tianji-web-preview-foo", docker.containers)

    def test_pull_failure_keeps_old(self):
        agent, _, docker, _ = make_agent(
            self.tmp.name, {"channel-foo": ref(DIGEST_A, SHA_A)})
        agent.deploy("channel-foo", ref(DIGEST_A, SHA_A), "channel-foo")
        docker.pull_fail.add("%s@%s" % (REPO, DIGEST_B))
        outcome = agent.deploy("channel-foo", ref(DIGEST_B, SHA_B), "channel-foo")
        self.assertEqual(outcome, "failed")
        entry = docker.containers["tianji-web-preview-foo"]
        self.assertTrue(entry["running"])
        self.assertEqual(entry["image"], "%s@%s" % (REPO, DIGEST_A))
        self.assertEqual(agent.state["channels"]["channel-foo"]["digest"], DIGEST_A)

    def test_manage_stable_disabled_skips_stable(self):
        agent, _, docker, _ = make_agent(
            self.tmp.name, {"channel-main": ref(DIGEST_A, SHA_A),
                            "channel-foo": ref(DIGEST_A, SHA_A)},
            env_extra={"TIANJI_DEPLOY_MANAGE_STABLE": "0"})
        outcomes = agent.reconcile_all()
        self.assertEqual(outcomes["channel-main"], "skipped")
        self.assertEqual(outcomes["channel-foo"], "deployed")
        self.assertNotIn("tianji-web-stable", docker.containers)


class HealthGateTests(unittest.TestCase):
    def test_health_ok(self):
        http_client = FakeHttp()
        ok, _ = frontend_health_ok("http://127.0.0.1:18200", http_client)
        self.assertTrue(ok)

    def test_health_non200_fails(self):
        http_client = FakeHttp()
        http_client.routes[18200] = (500, b"error", "text/plain")
        ok, _ = frontend_health_ok("http://127.0.0.1:18200", http_client)
        self.assertFalse(ok)

    def test_health_leak_fails(self):
        http_client = FakeHttp()
        http_client.routes[18200] = (
            200, b"<html><div id=\"root\"></div>tianji-private</html>", "text/html")
        ok, _ = frontend_health_ok("http://127.0.0.1:18200", http_client)
        self.assertFalse(ok)

    def test_health_no_root_fails(self):
        http_client = FakeHttp()
        http_client.routes[18200] = (200, b"<html><body>hi</body></html>", "text/html")
        ok, _ = frontend_health_ok("http://127.0.0.1:18200", http_client)
        self.assertFalse(ok)


class LogEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def test_log_and_evidence_format(self):
        agent, _, _, _ = make_agent(
            self.tmp.name, {"channel-main": ref(DIGEST_A, SHA_A)})
        agent.deploy("channel-main", ref(DIGEST_A, SHA_A), "channel-main")
        logs = read_jsonl(agent.config.log_file)
        self.assertTrue(logs)
        for record in logs:
            for key in ("ts", "channel", "action", "sha", "digest", "outcome"):
                self.assertIn(key, record)
        evidence = read_jsonl(agent.config.evidence_file)
        deployed = [r for r in evidence if r["outcome"] == "deployed"]
        self.assertEqual(len(deployed), 1)
        self.assertEqual(deployed[0]["image"], "%s@%s" % (REPO, DIGEST_A))
        state = json.loads(agent.config.state_file.read_text())
        entry = state["channels"]["channel-main"]
        for key in ("sha", "digest", "healthy", "updated_at",
                    "last_healthy_sha", "last_healthy_digest", "port", "container"):
            self.assertIn(key, entry)

    def test_status_reports_observed_backend(self):
        agent, _, docker, _ = make_agent(
            self.tmp.name, {"channel-main": ref(DIGEST_A, SHA_A)})
        docker.api = {"name": "tianji-api", "image": "sealed-api@sha256:xxxx"}
        status = agent.status()
        self.assertEqual(status["backend_observed"]["name"], "tianji-api")
        self.assertIn("operator-managed", status["backend_note"])


class FakeResponse:
    def __init__(self, headers, body):
        self.headers = headers
        self._body = body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def read(self):
        return self._body


class FakeOpener:
    """Canned GHCR registry: manifest requests return a digest header,
    tag-list requests return JSON."""

    def __init__(self, digests):
        self.digests = digests

    def __call__(self, request, timeout=None):
        url = request.full_url
        if "/tags/list" in url:
            body = json.dumps({"tags": sorted(self.digests)}).encode("utf-8")
            return FakeResponse({}, body)
        tag = url.rsplit("/manifests/", 1)[1]
        if tag not in self.digests:
            raise ValueError("tag missing: %s" % tag)
        return FakeResponse({"Docker-Content-Digest": self.digests[tag]}, b"")


class RegistryResolveTests(unittest.TestCase):
    def test_resolve_channel_finds_sha(self):
        digests = {"channel-main": DIGEST_A, SHA_A: DIGEST_A,
                   "channel-foo": DIGEST_B}
        client = RegistryClient(REPO, opener=FakeOpener(digests))
        found = client.resolve_channel("channel-main")
        self.assertEqual(found.digest, DIGEST_A)
        self.assertEqual(found.sha, SHA_A)

    def test_resolve_channel_sha_none_when_unmatched(self):
        digests = {"channel-main": DIGEST_A, SHA_A: DIGEST_C}
        client = RegistryClient(REPO, opener=FakeOpener(digests))
        found = client.resolve_channel("channel-main")
        self.assertEqual(found.digest, DIGEST_A)
        self.assertIsNone(found.sha)


class SimulationTests(unittest.TestCase):
    """SIMULATION: fake registry + fake docker + fake HTTP driving a full
    reconcile loop, including health-failure -> auto-rollback. Passing
    here proves agent logic only; it is NOT real-machine acceptance."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def test_full_loop_with_rollback(self):
        agent, registry, docker, http_client = make_agent(
            self.tmp.name, {
                "channel-main": ref(DIGEST_A, SHA_A),
                "channel-foo": ref(DIGEST_B, SHA_B),
                "channel-bar": ref(DIGEST_C, SHA_C),
            })
        outcomes = agent.reconcile_all()
        self.assertEqual(outcomes, {"channel-main": "deployed",
                                    "channel-foo": "deployed",
                                    "channel-bar": "deployed"})
        # A new foo image arrives but fails health: auto-rollback to B.
        registry.tags["channel-foo"] = ref("sha256:dddd", "d" * 40)
        http_client.fail_images.add("%s@sha256:dddd" % REPO)
        outcomes = agent.reconcile_all()
        self.assertEqual(outcomes["channel-foo"], "rolled_back")
        self.assertEqual(outcomes["channel-main"], "unchanged")
        self.assertEqual(outcomes["channel-bar"], "unchanged")
        state = agent.state["channels"]["channel-foo"]
        self.assertTrue(state["healthy"])
        self.assertEqual(state["digest"], DIGEST_B)
        logs = read_jsonl(agent.config.log_file)
        self.assertTrue(any(r["action"] == "deploy" and r["outcome"] == "failed"
                            for r in logs))
        self.assertTrue(any(r["outcome"] == "rolled_back" for r in logs))


class PipelineGuardTests(unittest.TestCase):
    """Static guards for .github/workflows/deploy-pipeline.yml: the
    resume-preview job exists and targets non-main only, the main wake
    job is untouched, and no new deploy secret was introduced. Skips
    when run outside a full checkout (same pattern as test_deploy_config)."""

    @classmethod
    def setUpClass(cls):
        path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "deploy-pipeline.yml"
        if not path.is_file():
            raise unittest.SkipTest("deploy-pipeline.yml not present")
        cls.text = path.read_text(encoding="utf-8")

    def test_resume_preview_job_targets_non_main_only(self):
        self.assertIn("resume-preview:", self.text)
        self.assertIn("github.ref != 'refs/heads/main'", self.text)

    def test_main_wake_job_untouched(self):
        self.assertIn("github.ref == 'refs/heads/main'", self.text)
        self.assertIn("wake-machine", self.text)

    def test_no_new_deploy_secrets(self):
        secrets = set(re.findall(r"secrets\.([A-Za-z0-9_]+)", self.text))
        self.assertEqual(secrets, {"GITHUB_TOKEN"})

    def test_agent_source_has_no_hardcoded_secret_literals(self):
        path = Path(__file__).resolve().parents[1] / "scripts" / "deploy_agent.py"
        if not path.is_file():
            raise unittest.SkipTest("deploy_agent.py not present")
        text = path.read_text(encoding="utf-8")
        for banned in ("sk-", "ADMIN_READ_TOKEN"):
            self.assertNotIn(banned, text)


if __name__ == "__main__":
    unittest.main()
