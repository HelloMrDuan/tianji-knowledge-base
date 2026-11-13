"""TJ-005.1/TJ-005.3: tests for scripts/recovery_drill.py.

All fixtures are synthetic temp dirs plus a real local HTTP stub
service (http.server): no trusted machine, no docker, no sealed
data, no network. The drill under test never touches the live
service and writes only into the scratch dir.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import recovery_drill as rd
from scripts import backup_verification as bv

HAVE_GIT = shutil.which("git") is not None


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _manifest(rows):
    return {
        "schema_version": "private-data-snapshot-v2",
        "areas": ["canonical"],
        "file_count": len(rows),
        "total_bytes": sum(r["bytes"] for r in rows),
        "files": rows,
    }


def _write_snapshot(root: Path, files: dict[str, bytes]) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    rows = []
    for rel, data in sorted(files.items()):
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        rows.append({"path": rel, "bytes": len(data), "sha256": _sha(data)})
    (root / "private-data-manifest.json").write_text(
        json.dumps(_manifest(rows), indent=2), encoding="utf-8")
    return root


def _log_line(**fields):
    row = {"project": "tianji", "channel": "prerelease", "branch": "main",
           "sha": "a" * 40, "image": "", "port": "8080",
           "result": "DEPLOYED", "detail": "", "ts": "2026-11-12T00:00:00+00:00"}
    row.update(fields)
    return json.dumps(row, ensure_ascii=False)


class StubService:
    """A real local HTTP service mimicking the rolled-back backend.

    Serves /health (rag_ready flag) and the bazi execute probe
    (pillars flag). Flags are settable per test to force gate
    failures.
    """

    def __init__(self, rag_ready=True, pillars=True):
        self.rag_ready = rag_ready
        self.pillars = pillars
        self._server = None
        self._thread = None

    def __enter__(self):
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_GET(self):
                if self.path == "/health":
                    body = {"status": "ok", "engine": "ready",
                            "rag_ready": outer.rag_ready,
                            "domains": ["bazi"]}
                    self._send(200, body)
                else:
                    self._send(404, {"detail": "Not Found"})

            def do_POST(self):
                if self.path == "/api/v1/public/execute":
                    length = int(self.headers.get("Content-Length", "0") or 0)
                    self.rfile.read(length)
                    if outer.pillars:
                        body = {"result": {"pillars": [
                            {"label": "year", "ganzhi": "庚午"}]}}
                    else:
                        body = {"result": {"status": "ok"}}
                    self._send(200, body)
                else:
                    self._send(404, {"detail": "Not Found"})

            def _send(self, status, body):
                raw = json.dumps(body).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

        self._server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self._thread = threading.Thread(target=self._server.serve_forever,
                                        daemon=True)
        self._thread.start()
        return self

    def __exit__(self, *exc):
        self._server.shutdown()
        self._server.server_close()
        return False

    @property
    def url(self):
        return "http://127.0.0.1:%d" % self._server.server_address[1]


class RecoveryDrillFixture(unittest.TestCase):
    """Build a synthetic deployment base + scratch dir."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="tj0053-drill-"))
        self.base = self.tmp / "platform-deploy"
        self.scratch = self.tmp / "scratch"
        self._build_base()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _build_base(self):
        # Live snapshot + one rotation backup (identical content).
        files = {"data/canonical/a.json": b'{"k": 1}',
                 "data/canonical/b.json": b'{"k": 2}'}
        _write_snapshot(self.base / "secure" / "tianji-knowledge", files)
        _write_snapshot(self.base / "secure" / "tianji-knowledge-pre-2026-11-11",
                        files)
        # deploys.log: an earlier DEPLOYED pair, then the current pair.
        evid = self.base / "deployment-evidence" / "tj-core-01"
        evid.mkdir(parents=True)
        self.prev_sha = "a" * 40
        self.cur_sha = "b" * 40
        lines = [
            _log_line(sha=self.prev_sha, result="DEPLOYED",
                      image="tianji-api:cicd-prerelease-aaaaaaaa",
                      detail="health+bazi ok; port 8080; "
                             "web=ghcr.io/hellomrduan/tianji-web:" + self.prev_sha
                             + "; pin=" + "c" * 64,
                      ts="2026-11-12T00:00:00+00:00"),
            _log_line(sha=self.cur_sha, result="DEPLOYED",
                      image="tianji-api:cicd-prerelease-bbbbbbbb",
                      detail="health+bazi ok; port 8080; "
                             "web=ghcr.io/hellomrduan/tianji-web:" + self.cur_sha
                             + "; pin=" + "d" * 64,
                      ts="2026-11-12T00:01:00+00:00"),
        ]
        (evid / "deploys.log").write_text("\n".join(lines) + "\n",
                                           encoding="utf-8")
        state = self.base / "cicd" / "state"
        state.mkdir(parents=True)
        (state / "tianji-prerelease.sha").write_text(self.cur_sha,
                                                     encoding="utf-8")
        (state / "tianji-prerelease.api-image").write_text(
            "tianji-api:cicd-prerelease-bbbbbbbb", encoding="utf-8")
        (state / "tianji-prerelease.web-image").write_text(
            "ghcr.io/hellomrduan/tianji-web:" + self.cur_sha,
            encoding="utf-8")

    def _pair_file(self, api, web):
        path = self.tmp / "pair.json"
        path.write_text(json.dumps({"api": api, "web": web}),
                        encoding="utf-8")
        return "file:%s" % path

    def _tree_fingerprint(self, root):
        out = []
        for path in sorted(root.rglob("*")):
            if path.is_file():
                out.append((str(path.relative_to(root)),
                            path.stat().st_size, _sha(path.read_bytes())))
        return out

    def _run(self, **kwargs):
        # The health gate polls up to 40 x 2s on failure; shrink the
        # poll for the failure-path tests so they stay fast.
        with patch.object(rd, "HEALTH_ATTEMPTS", 2), \
                patch.object(rd, "HEALTH_INTERVAL_S", 0.01):
            return rd.run_drill(self.base, self.scratch, **kwargs)

    def test_happy_path_passes_and_writes_evidence(self):
        with StubService() as service:
            provider = self._pair_file(
                "tianji-api:cicd-prerelease-aaaaaaaa",
                "ghcr.io/hellomrduan/tianji-web:" + self.prev_sha)
            evidence = self._run(source="backup", api_url=service.url,
                                 image_provider=provider)
        self.assertEqual(evidence["result"], "PASS")
        self.assertEqual([s["status"] for s in evidence["steps"]],
                         ["pass", "pass", "pass"])
        self.assertEqual([s["name"] for s in evidence["steps"]],
                         ["restore", "rollback", "health_gate"])
        # The rollback pair is the PREVIOUS deployed pair, not current.
        self.assertEqual(evidence["rollback_pair"]["sha"], self.prev_sha)
        self.assertEqual(evidence["rollback_pair"]["api"],
                         "tianji-api:cicd-prerelease-aaaaaaaa")
        # Evidence is machine-readable and on disk.
        on_disk = json.loads(
            (self.scratch / "drill-evidence.json").read_text(
                encoding="utf-8"))
        self.assertEqual(on_disk, evidence)
        self.assertEqual(on_disk["restored_manifest"]["file_count"], 2)
        self.assertEqual(on_disk["restored_manifest"]["total_bytes"], 16)
        self.assertTrue(on_disk["restored_manifest_sha256"])
        self.assertTrue(on_disk["started_at"] and on_disk["finished_at"])
        # The rollback env file is the deploy agent's exact format.
        env = (self.scratch / "rollback.env").read_text(encoding="utf-8")
        self.assertEqual(
            env, "TIANJI_PRIVATE_API_IMAGE=tianji-api:cicd-prerelease-aaaaaaaa\n"
                 "TIANJI_PUBLIC_WEB_IMAGE=ghcr.io/hellomrduan/tianji-web:"
                 + self.prev_sha + "\nTIANJI_HOST_PORT=8080\n")
        # The restored copy is byte-identical to the source backup.
        src_manifest = (self.base / "secure"
                        / "tianji-knowledge-pre-2026-11-11"
                        / "private-data-manifest.json").read_bytes()
        restored_manifest = (self.scratch / "restored"
                             / "private-data-manifest.json").read_bytes()
        self.assertEqual(restored_manifest, src_manifest)

    def test_drill_does_not_modify_the_base(self):
        before = self._tree_fingerprint(self.base)
        with StubService() as service:
            provider = self._pair_file(
                "tianji-api:cicd-prerelease-aaaaaaaa",
                "ghcr.io/hellomrduan/tianji-web:" + self.prev_sha)
            self._run(source="backup", api_url=service.url,
                      image_provider=provider)
        self.assertEqual(before, self._tree_fingerprint(self.base))

    def test_restore_from_live_snapshot(self):
        with StubService() as service:
            provider = self._pair_file(
                "tianji-api:cicd-prerelease-aaaaaaaa",
                "ghcr.io/hellomrduan/tianji-web:" + self.prev_sha)
            evidence = self._run(source="live", api_url=service.url,
                                 image_provider=provider)
        self.assertEqual(evidence["result"], "PASS")
        self.assertIn("live snapshot", evidence["steps"][0]["detail"])

    def test_restore_catches_corrupted_backup(self):
        target = (self.base / "secure" / "tianji-knowledge-pre-2026-11-11"
                  / "data" / "canonical" / "a.json")
        data = bytearray(target.read_bytes())
        data[0] ^= 0xFF
        target.write_bytes(bytes(data))
        with StubService() as service:
            provider = self._pair_file(
                "tianji-api:cicd-prerelease-aaaaaaaa",
                "ghcr.io/hellomrduan/tianji-web:" + self.prev_sha)
            evidence = self._run(source="backup", api_url=service.url,
                                 image_provider=provider)
        self.assertEqual(evidence["result"], "FAIL")
        restore = evidence["steps"][0]
        self.assertEqual(restore["name"], "restore")
        self.assertEqual(restore["status"], "fail")
        self.assertIn("SHA256 mismatch", restore["detail"])

    def test_restore_fails_with_no_rotation_backup(self):
        shutil.rmtree(self.base / "secure" / "tianji-knowledge-pre-2026-11-11")
        with StubService() as service:
            provider = self._pair_file(
                "tianji-api:cicd-prerelease-aaaaaaaa",
                "ghcr.io/hellomrduan/tianji-web:" + self.prev_sha)
            evidence = self._run(source="backup", api_url=service.url,
                                 image_provider=provider)
        self.assertEqual(evidence["result"], "FAIL")
        self.assertEqual(evidence["steps"][0]["status"], "fail")
        self.assertIn("no tianji-knowledge-pre-", evidence["steps"][0]["detail"])

    def test_rollback_falls_back_to_protected_pair(self):
        # Only the current SHA ever deployed: no earlier pair exists.
        evid = self.base / "deployment-evidence" / "tj-core-01" / "deploys.log"
        lines = [_log_line(sha=self.cur_sha, result="DEPLOYED",
                           image="tianji-api:cicd-prerelease-bbbbbbbb",
                           detail="health+bazi ok; port 8080; web="
                                  "ghcr.io/hellomrduan/tianji-web:"
                                  + self.cur_sha,
                           ts="2026-11-12T00:01:00+00:00")]
        evid.write_text("\n".join(lines) + "\n", encoding="utf-8")
        with StubService() as service:
            provider = self._pair_file(bv.PROTECTED_API, bv.PROTECTED_WEB)
            evidence = self._run(source="backup", api_url=service.url,
                                 image_provider=provider)
        self.assertEqual(evidence["result"], "PASS")
        self.assertEqual(evidence["rollback_pair"]["api"], bv.PROTECTED_API)
        self.assertEqual(evidence["rollback_pair"]["web"], bv.PROTECTED_WEB)

    def test_health_gate_fails_when_rag_not_ready(self):
        with StubService(rag_ready=False) as service:
            provider = self._pair_file(
                "tianji-api:cicd-prerelease-aaaaaaaa",
                "ghcr.io/hellomrduan/tianji-web:" + self.prev_sha)
            evidence = self._run(source="backup", api_url=service.url,
                                 image_provider=provider)
        self.assertEqual(evidence["result"], "FAIL")
        gate = evidence["steps"][2]
        self.assertEqual(gate["name"], "health_gate")
        self.assertEqual(gate["status"], "fail")
        self.assertIn("rag_ready", gate["detail"])

    def test_health_gate_fails_when_images_do_not_match(self):
        with StubService() as service:
            # The running pair is the CURRENT pair, not the rollback pair.
            provider = self._pair_file(
                "tianji-api:cicd-prerelease-bbbbbbbb",
                "ghcr.io/hellomrduan/tianji-web:" + self.cur_sha)
            evidence = self._run(source="backup", api_url=service.url,
                                 image_provider=provider)
        self.assertEqual(evidence["result"], "FAIL")
        gate = evidence["steps"][2]
        self.assertEqual(gate["status"], "fail")
        self.assertIn("!= rollback pair", gate["detail"])

    def test_health_gate_fails_when_execute_has_no_pillars(self):
        with StubService(pillars=False) as service:
            provider = self._pair_file(
                "tianji-api:cicd-prerelease-aaaaaaaa",
                "ghcr.io/hellomrduan/tianji-web:" + self.prev_sha)
            evidence = self._run(source="backup", api_url=service.url,
                                 image_provider=provider)
        self.assertEqual(evidence["result"], "FAIL")
        gate = evidence["steps"][2]
        self.assertEqual(gate["status"], "fail")
        self.assertIn("bazi execute probe", gate["detail"])

    def test_health_gate_fails_when_service_unreachable(self):
        provider = self._pair_file(
            "tianji-api:cicd-prerelease-aaaaaaaa",
            "ghcr.io/hellomrduan/tianji-web:" + self.prev_sha)
        evidence = self._run(source="backup",
                             api_url="http://127.0.0.1:1",
                             image_provider=provider)
        self.assertEqual(evidence["result"], "FAIL")
        self.assertEqual(evidence["steps"][2]["status"], "fail")

    def test_health_gate_fails_when_image_provider_file_missing(self):
        with StubService() as service:
            evidence = self._run(source="backup", api_url=service.url,
                                 image_provider="file:%s"
                                 % (self.tmp / "no-such-pair.json"))
        self.assertEqual(evidence["result"], "FAIL")
        gate = evidence["steps"][2]
        self.assertEqual(gate["status"], "fail")
        self.assertIn("image-provider file missing", gate["detail"])

    def test_health_gate_fails_when_image_provider_file_unreadable(self):
        bad = self.tmp / "bad-pair.json"
        bad.write_text("{not json", encoding="utf-8")
        with StubService() as service:
            evidence = self._run(source="backup", api_url=service.url,
                                 image_provider="file:%s" % bad)
        self.assertEqual(evidence["result"], "FAIL")
        gate = evidence["steps"][2]
        self.assertEqual(gate["status"], "fail")
        self.assertIn("image-provider file unreadable", gate["detail"])

    def test_health_gate_fails_when_image_provider_file_lacks_api_web(self):
        partial = self.tmp / "partial-pair.json"
        partial.write_text(json.dumps({"api": "tianji-api:x"}),
                           encoding="utf-8")
        with StubService() as service:
            evidence = self._run(source="backup", api_url=service.url,
                                 image_provider="file:%s" % partial)
        self.assertEqual(evidence["result"], "FAIL")
        gate = evidence["steps"][2]
        self.assertEqual(gate["status"], "fail")
        self.assertIn("lacks api/web", gate["detail"])

    def test_health_gate_fails_when_image_provider_spec_unknown(self):
        with StubService() as service:
            evidence = self._run(source="backup", api_url=service.url,
                                 image_provider="bogus-spec")
        self.assertEqual(evidence["result"], "FAIL")
        gate = evidence["steps"][2]
        self.assertEqual(gate["status"], "fail")
        self.assertIn("unknown image-provider spec", gate["detail"])

    def test_health_gate_fails_when_docker_unavailable(self):
        # No docker binary: the image-identity sub-check cannot run.
        with StubService() as service, \
                patch.object(rd.shutil, "which", return_value=None):
            evidence = self._run(source="backup", api_url=service.url,
                                 image_provider="docker")
        self.assertEqual(evidence["result"], "FAIL")
        gate = evidence["steps"][2]
        self.assertEqual(gate["status"], "fail")
        self.assertIn("docker inspect unavailable", gate["detail"])

    def test_restore_fails_when_live_source_missing(self):
        shutil.rmtree(self.base / "secure" / "tianji-knowledge")
        with StubService() as service:
            provider = self._pair_file(
                "tianji-api:cicd-prerelease-aaaaaaaa",
                "ghcr.io/hellomrduan/tianji-web:" + self.prev_sha)
            evidence = self._run(source="live", api_url=service.url,
                                 image_provider=provider)
        self.assertEqual(evidence["result"], "FAIL")
        restore = evidence["steps"][0]
        self.assertEqual(restore["status"], "fail")
        self.assertIn("source dir missing", restore["detail"])

    def test_restore_fails_when_manifest_unreadable(self):
        manifest = (self.base / "secure"
                    / "tianji-knowledge-pre-2026-11-11"
                    / "private-data-manifest.json")
        manifest.write_text("{not json", encoding="utf-8")
        with StubService() as service:
            provider = self._pair_file(
                "tianji-api:cicd-prerelease-aaaaaaaa",
                "ghcr.io/hellomrduan/tianji-web:" + self.prev_sha)
            evidence = self._run(source="backup", api_url=service.url,
                                 image_provider=provider)
        self.assertEqual(evidence["result"], "FAIL")
        restore = evidence["steps"][0]
        self.assertEqual(restore["status"], "fail")
        self.assertIn("manifest unreadable", restore["detail"])

    def test_restore_fails_when_manifest_not_self_consistent(self):
        manifest_path = (self.base / "secure"
                         / "tianji-knowledge-pre-2026-11-11"
                         / "private-data-manifest.json")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["file_count"] = 99
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        with StubService() as service:
            provider = self._pair_file(
                "tianji-api:cicd-prerelease-aaaaaaaa",
                "ghcr.io/hellomrduan/tianji-web:" + self.prev_sha)
            evidence = self._run(source="backup", api_url=service.url,
                                 image_provider=provider)
        self.assertEqual(evidence["result"], "FAIL")
        restore = evidence["steps"][0]
        self.assertEqual(restore["status"], "fail")
        self.assertIn("not self-consistent", restore["detail"])

    def test_rollback_falls_back_when_deploys_log_malformed(self):
        evid = self.base / "deployment-evidence" / "tj-core-01" / "deploys.log"
        evid.write_text("{not json}\n{\"also\": \"broken\"}\n",
                        encoding="utf-8")
        with StubService() as service:
            provider = self._pair_file(bv.PROTECTED_API, bv.PROTECTED_WEB)
            evidence = self._run(source="backup", api_url=service.url,
                                 image_provider=provider)
        self.assertEqual(evidence["result"], "PASS")
        self.assertEqual(evidence["rollback_pair"]["api"], bv.PROTECTED_API)
        self.assertEqual(evidence["rollback_pair"]["web"], bv.PROTECTED_WEB)

    def test_rollback_falls_back_when_deployed_entry_lacks_web_token(self):
        evid = self.base / "deployment-evidence" / "tj-core-01" / "deploys.log"
        lines = [
            _log_line(sha=self.prev_sha, result="DEPLOYED",
                      image="tianji-api:cicd-prerelease-aaaaaaaa",
                      detail="health+bazi ok; no web token here",
                      ts="2026-11-12T00:00:00+00:00"),
            _log_line(sha=self.cur_sha, result="DEPLOYED",
                      image="tianji-api:cicd-prerelease-bbbbbbbb",
                      detail="health+bazi ok; port 8080; "
                             "web=ghcr.io/hellomrduan/tianji-web:"
                             + self.cur_sha,
                      ts="2026-11-12T00:01:00+00:00"),
        ]
        evid.write_text("\n".join(lines) + "\n", encoding="utf-8")
        with StubService() as service:
            provider = self._pair_file(bv.PROTECTED_API, bv.PROTECTED_WEB)
            evidence = self._run(source="backup", api_url=service.url,
                                 image_provider=provider)
        self.assertEqual(evidence["result"], "PASS")
        self.assertEqual(evidence["rollback_pair"]["api"], bv.PROTECTED_API)

    def test_rollback_falls_back_when_deployed_entry_lacks_image(self):
        evid = self.base / "deployment-evidence" / "tj-core-01" / "deploys.log"
        lines = [
            _log_line(sha=self.prev_sha, result="DEPLOYED",
                      image="",
                      detail="health+bazi ok; port 8080; "
                             "web=ghcr.io/hellomrduan/tianji-web:"
                             + self.prev_sha,
                      ts="2026-11-12T00:00:00+00:00"),
            _log_line(sha=self.cur_sha, result="DEPLOYED",
                      image="tianji-api:cicd-prerelease-bbbbbbbb",
                      detail="health+bazi ok; port 8080; "
                             "web=ghcr.io/hellomrduan/tianji-web:"
                             + self.cur_sha,
                      ts="2026-11-12T00:01:00+00:00"),
        ]
        evid.write_text("\n".join(lines) + "\n", encoding="utf-8")
        with StubService() as service:
            provider = self._pair_file(bv.PROTECTED_API, bv.PROTECTED_WEB)
            evidence = self._run(source="backup", api_url=service.url,
                                 image_provider=provider)
        self.assertEqual(evidence["result"], "PASS")
        self.assertEqual(evidence["rollback_pair"]["api"], bv.PROTECTED_API)

    def _write_log(self, lines):
        evid = self.base / "deployment-evidence" / "tj-core-01" / "deploys.log"
        evid.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _set_state_sha(self, sha):
        (self.base / "cicd" / "state" / "tianji-prerelease.sha").write_text(
            sha, encoding="utf-8")

    def _deployed(self, sha, api, web, channel="prerelease", ts="2026-11-12T00:00:00+00:00"):
        return _log_line(sha=sha, result="DEPLOYED", channel=channel,
                         image=api,
                         detail="health+bazi ok; port 8080; web=%s" % web,
                         ts=ts)

    # -- A. Scratch isolation: fail-closed, zero writes outside scratch. --

    def test_scratch_equal_to_base_is_rejected_without_writes(self):
        before = self._tree_fingerprint(self.base)
        evidence = rd.run_drill(self.base, self.base, source="backup",
                                api_url="http://127.0.0.1:1",
                                image_provider="bogus")
        self.assertEqual(evidence["result"], "FAIL")
        self.assertIn("error", evidence)
        self.assertIn("outside the deployment base", evidence["error"])
        self.assertEqual(evidence["steps"], [])
        self.assertEqual(before, self._tree_fingerprint(self.base))

    def test_scratch_inside_base_is_rejected_without_writes(self):
        before = self._tree_fingerprint(self.base)
        evidence = rd.run_drill(self.base, self.base / "secure",
                                source="backup", api_url="http://127.0.0.1:1",
                                image_provider="bogus")
        self.assertEqual(evidence["result"], "FAIL")
        self.assertIn("outside the deployment base", evidence["error"])
        self.assertEqual(before, self._tree_fingerprint(self.base))

    def test_symlink_scratch_is_rejected_without_writes(self):
        target = self.tmp / "real-scratch-target"
        target.mkdir()
        sentinel = target / "sentinel.txt"
        sentinel.write_bytes(b"do not touch")
        link = self.tmp / "scratch-link"
        os.symlink(target, link)
        evidence = rd.run_drill(self.base, link, source="backup",
                                api_url="http://127.0.0.1:1",
                                image_provider="bogus")
        self.assertEqual(evidence["result"], "FAIL")
        self.assertIn("symlink", evidence["error"])
        self.assertEqual(sentinel.read_bytes(), b"do not touch")
        self.assertEqual(sorted(p.name for p in target.iterdir()),
                         ["sentinel.txt"])

    def test_preexisting_restored_in_scratch_is_rejected_and_untouched(self):
        self.scratch.mkdir(parents=True)
        restored = self.scratch / "restored"
        restored.mkdir()
        sentinel = restored / "sentinel.txt"
        sentinel.write_bytes(b"pre-existing data")
        evidence = self._run(source="backup", api_url="http://127.0.0.1:1",
                             image_provider="bogus")
        self.assertEqual(evidence["result"], "FAIL")
        self.assertIn("error", evidence)
        self.assertIn("not empty", evidence["error"])
        self.assertEqual(sentinel.read_bytes(), b"pre-existing data")

    def test_step_restore_refuses_preexisting_restored_and_keeps_sentinel(self):
        # step_restore itself must refuse: the run_drill scratch check
        # is not the only guard.
        self.scratch.mkdir(parents=True)
        restored = self.scratch / "restored"
        restored.mkdir()
        sentinel = restored / "sentinel.txt"
        sentinel.write_bytes(b"pre-existing data")
        step = rd.step_restore(self.base, self.scratch, "backup")
        self.assertEqual(step["status"], "fail")
        self.assertIn("refusing to overwrite", step["detail"])
        self.assertEqual(sentinel.read_bytes(), b"pre-existing data")

    def test_scratch_must_be_absolute(self):
        evidence = rd.run_drill(self.base, Path("relative/scratch"),
                                source="backup", api_url="http://127.0.0.1:1",
                                image_provider="bogus")
        self.assertEqual(evidence["result"], "FAIL")
        self.assertIn("absolute", evidence["error"])

    # -- B. Manifest path + symlink: traversal, absolute, links, membership. --

    def test_step_restore_rejects_traversal_manifest_path(self):
        backup = (self.base / "secure" / "tianji-knowledge-pre-2026-11-11")
        manifest_path = backup / "private-data-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["files"][0]["path"] = "data/canonical/../../evil.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        step = rd.step_restore(self.base, self.scratch, "backup")
        self.assertEqual(step["status"], "fail")
        self.assertIn("not self-consistent", step["detail"])
        self.assertIn("unsafe manifest path", step["detail"])
        self.assertFalse((self.scratch / "restored").exists())

    def test_step_restore_rejects_absolute_manifest_path(self):
        backup = (self.base / "secure" / "tianji-knowledge-pre-2026-11-11")
        manifest_path = backup / "private-data-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["files"][0]["path"] = "/etc/passwd"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        step = rd.step_restore(self.base, self.scratch, "backup")
        self.assertEqual(step["status"], "fail")
        self.assertIn("unsafe manifest path", step["detail"])

    def test_source_symlink_file_is_rejected_before_copy(self):
        backup = (self.base / "secure" / "tianji-knowledge-pre-2026-11-11")
        outside = self.tmp / "outside.txt"
        outside.write_bytes(b"secret")
        os.symlink(outside, backup / "data" / "canonical" / "evil.json")
        step = rd.step_restore(self.base, self.scratch, "backup")
        self.assertEqual(step["status"], "fail")
        self.assertIn("symlink", step["detail"])
        self.assertFalse((self.scratch / "restored").exists())
        self.assertEqual(outside.read_bytes(), b"secret")

    def test_source_symlinked_manifest_is_rejected(self):
        backup = (self.base / "secure" / "tianji-knowledge-pre-2026-11-11")
        real = self.tmp / "real-manifest.json"
        real.write_bytes(
            (backup / "private-data-manifest.json").read_bytes())
        (backup / "private-data-manifest.json").unlink()
        os.symlink(real, backup / "private-data-manifest.json")
        step = rd.step_restore(self.base, self.scratch, "backup")
        self.assertEqual(step["status"], "fail")
        self.assertIn("symlink", step["detail"])

    def test_restored_tree_extra_file_is_rejected(self):
        backup = (self.base / "secure" / "tianji-knowledge-pre-2026-11-11")
        (backup / "data" / "canonical" / "extra.json").write_bytes(b"{}")
        step = rd.step_restore(self.base, self.scratch, "backup")
        self.assertEqual(step["status"], "fail")
        self.assertIn("unmanifested file", step["detail"])

    def test_manifest_missing_file_is_rejected(self):
        backup = (self.base / "secure" / "tianji-knowledge-pre-2026-11-11")
        (backup / "data" / "canonical" / "a.json").unlink()
        step = rd.step_restore(self.base, self.scratch, "backup")
        self.assertEqual(step["status"], "fail")
        self.assertIn("restored file missing", step["detail"])

    # -- C. Rollback pair: stable channel only, anchored on the current row. --

    def test_rollback_ignores_newer_preview_deployed(self):
        # stable A -> stable B -> preview C; current is B. Preview C is
        # newer but must never become the stable rollback pair.
        sha_a, sha_b, sha_c = "a" * 40, "b" * 40, "c" * 40
        self._write_log([
            self._deployed(sha_a, "tianji-api:stable-a",
                           "ghcr.io/hellomrduan/tianji-web:" + sha_a,
                           ts="2026-11-12T00:00:00+00:00"),
            self._deployed(sha_b, "tianji-api:stable-b",
                           "ghcr.io/hellomrduan/tianji-web:" + sha_b,
                           ts="2026-11-12T00:01:00+00:00"),
            self._deployed(sha_c, "tianji-api:preview-c",
                           "ghcr.io/hellomrduan/tianji-web:" + sha_c,
                           channel="preview-round1",
                           ts="2026-11-12T00:02:00+00:00"),
        ])
        self._set_state_sha(sha_b)
        with StubService() as service:
            provider = self._pair_file(
                "tianji-api:stable-a",
                "ghcr.io/hellomrduan/tianji-web:" + sha_a)
            evidence = self._run(source="backup", api_url=service.url,
                                 image_provider=provider)
        self.assertEqual(evidence["result"], "PASS")
        self.assertEqual(evidence["rollback_pair"]["sha"], sha_a)
        self.assertEqual(evidence["rollback_pair"]["api"],
                         "tianji-api:stable-a")

    def test_rollback_ignores_preview_between_stable_deploys(self):
        # stable A -> preview C -> stable B; current is B. The previous
        # stable pair is A, not the preview in between.
        sha_a, sha_b, sha_c = "a" * 40, "b" * 40, "c" * 40
        self._write_log([
            self._deployed(sha_a, "tianji-api:stable-a",
                           "ghcr.io/hellomrduan/tianji-web:" + sha_a,
                           ts="2026-11-12T00:00:00+00:00"),
            self._deployed(sha_c, "tianji-api:preview-c",
                           "ghcr.io/hellomrduan/tianji-web:" + sha_c,
                           channel="preview-round1",
                           ts="2026-11-12T00:01:00+00:00"),
            self._deployed(sha_b, "tianji-api:stable-b",
                           "ghcr.io/hellomrduan/tianji-web:" + sha_b,
                           ts="2026-11-12T00:02:00+00:00"),
        ])
        self._set_state_sha(sha_b)
        with StubService() as service:
            provider = self._pair_file(
                "tianji-api:stable-a",
                "ghcr.io/hellomrduan/tianji-web:" + sha_a)
            evidence = self._run(source="backup", api_url=service.url,
                                 image_provider=provider)
        self.assertEqual(evidence["result"], "PASS")
        self.assertEqual(evidence["rollback_pair"]["sha"], sha_a)

    def test_rollback_fails_when_state_sha_not_in_log(self):
        # The recorded state SHA matches no stable DEPLOYED row: fail
        # closed instead of guessing a previous pair.
        self._set_state_sha("d" * 40)
        with StubService() as service:
            provider = self._pair_file(bv.PROTECTED_API, bv.PROTECTED_WEB)
            evidence = self._run(source="backup", api_url=service.url,
                                 image_provider=provider)
        self.assertEqual(evidence["result"], "FAIL")
        rollback = evidence["steps"][1]
        self.assertEqual(rollback["name"], "rollback")
        self.assertEqual(rollback["status"], "fail")
        self.assertIn("state/log mismatch", rollback["detail"])

    def test_rollback_fails_when_state_points_at_preview_sha(self):
        # The state records a preview SHA as the current deploy: no
        # stable anchor exists, so no preview pair may be selected.
        sha_a, sha_b, sha_c = "a" * 40, "b" * 40, "c" * 40
        self._write_log([
            self._deployed(sha_a, "tianji-api:stable-a",
                           "ghcr.io/hellomrduan/tianji-web:" + sha_a,
                           ts="2026-11-12T00:00:00+00:00"),
            self._deployed(sha_b, "tianji-api:stable-b",
                           "ghcr.io/hellomrduan/tianji-web:" + sha_b,
                           ts="2026-11-12T00:01:00+00:00"),
            self._deployed(sha_c, "tianji-api:preview-c",
                           "ghcr.io/hellomrduan/tianji-web:" + sha_c,
                           channel="preview-round1",
                           ts="2026-11-12T00:02:00+00:00"),
        ])
        self._set_state_sha(sha_c)
        with StubService() as service:
            provider = self._pair_file(bv.PROTECTED_API, bv.PROTECTED_WEB)
            evidence = self._run(source="backup", api_url=service.url,
                                 image_provider=provider)
        self.assertEqual(evidence["result"], "FAIL")
        rollback = evidence["steps"][1]
        self.assertEqual(rollback["status"], "fail")
        self.assertIn("state/log mismatch", rollback["detail"])

    # -- D. Health gate: three sub-results reported separately. --

    def test_health_gate_passes_when_running_current_but_rollback_pair_available(self):
        # Docker provider: the service runs the CURRENT pair (normal
        # production state) while the rollback pair images are present
        # in docker. The old gate failed this; the fixed gate passes
        # and reports the three sub-results separately.
        prev_api = "tianji-api:cicd-prerelease-aaaaaaaa"
        prev_web = "ghcr.io/hellomrduan/tianji-web:" + self.prev_sha
        cur_api = "tianji-api:cicd-prerelease-bbbbbbbb"
        cur_web = "ghcr.io/hellomrduan/tianji-web:" + self.cur_sha
        with StubService() as service, \
                patch.object(rd, "_docker_images_for_containers",
                             return_value=(cur_api, cur_web)), \
                patch.object(bv, "_docker_images",
                             return_value={prev_api, prev_web, cur_api,
                                           cur_web}):
            evidence = self._run(source="backup", api_url=service.url,
                                 image_provider="docker")
        self.assertEqual(evidence["result"], "PASS")
        gate = evidence["steps"][2]
        self.assertEqual(gate["status"], "pass")
        self.assertIn("differ from", gate["detail"])
        self.assertEqual(
            evidence["current_production_health"]["status"], "pass")
        self.assertEqual(
            evidence["rollback_pair_availability"]["status"], "pass")
        self.assertEqual(
            evidence["post_rollback_health"]["status"], "not_performed")
        self.assertIn("separate user authorization",
                      evidence["post_rollback_health"]["detail"])

    def test_health_gate_fails_when_rollback_pair_image_missing_from_docker(self):
        prev_api = "tianji-api:cicd-prerelease-aaaaaaaa"
        prev_web = "ghcr.io/hellomrduan/tianji-web:" + self.prev_sha
        cur_api = "tianji-api:cicd-prerelease-bbbbbbbb"
        cur_web = "ghcr.io/hellomrduan/tianji-web:" + self.cur_sha
        with StubService() as service, \
                patch.object(rd, "_docker_images_for_containers",
                             return_value=(cur_api, cur_web)), \
                patch.object(bv, "_docker_images",
                             return_value={prev_api, cur_api, cur_web}):
            evidence = self._run(source="backup", api_url=service.url,
                                 image_provider="docker")
        self.assertEqual(evidence["result"], "FAIL")
        gate = evidence["steps"][2]
        self.assertEqual(gate["status"], "fail")
        self.assertIn("not available in docker", gate["detail"])
        self.assertIn(prev_web, gate["detail"])
        self.assertEqual(
            evidence["rollback_pair_availability"]["status"], "fail")
        self.assertEqual(
            evidence["current_production_health"]["status"], "pass")

    def test_health_gate_reports_subresults_separately(self):
        with StubService() as service:
            provider = self._pair_file(
                "tianji-api:cicd-prerelease-aaaaaaaa",
                "ghcr.io/hellomrduan/tianji-web:" + self.prev_sha)
            evidence = self._run(source="backup", api_url=service.url,
                                 image_provider=provider)
        self.assertEqual(evidence["result"], "PASS")
        # The three sub-results are distinct keys with distinct statuses.
        self.assertEqual(
            evidence["current_production_health"]["status"], "pass")
        self.assertEqual(
            evidence["rollback_pair_availability"]["status"], "pass")
        self.assertEqual(
            evidence["post_rollback_health"]["status"], "not_performed")
        # A PASS must never be readable as a production rollback proof.
        self.assertIn("NOT verified",
                      evidence["steps"][2]["detail"])

    def test_main_exit_codes(self):
        with StubService() as service:
            provider = self._pair_file(
                "tianji-api:cicd-prerelease-aaaaaaaa",
                "ghcr.io/hellomrduan/tianji-web:" + self.prev_sha)
            with patch.object(rd, "HEALTH_ATTEMPTS", 2), \
                    patch.object(rd, "HEALTH_INTERVAL_S", 0.01), \
                    patch.object(sys, "argv",
                                 ["recovery_drill.py", "--base",
                                  str(self.base), "--scratch",
                                  str(self.scratch),
                                  "--api-url", service.url,
                                  "--image-provider", provider]):
                self.assertEqual(rd.main(), 0)
        # Missing base exits 2.
        with patch.object(sys, "argv",
                          ["recovery_drill.py", "--base",
                           str(self.tmp / "does-not-exist"), "--scratch",
                           str(self.scratch)]):
            self.assertEqual(rd.main(), 2)


if __name__ == "__main__":
    unittest.main()
