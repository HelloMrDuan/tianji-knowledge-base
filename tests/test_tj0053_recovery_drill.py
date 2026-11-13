"""TJ-005.1/TJ-005.3: tests for scripts/recovery_drill.py.

All fixtures are synthetic temp dirs plus a real local HTTP stub
service (http.server): no trusted machine, no docker, no sealed
data, no network. The drill under test never touches the live
service and writes only into the scratch dir.
"""
import hashlib
import json
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
