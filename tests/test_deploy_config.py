"""TJ-005.1/TJ-005.3: deployment configuration static checks.

These verify the deployment CONFIGURATION without Docker. Real container
execution is covered by deploy/accept-sealed.sh on a Docker-capable
machine; these tests never pretend to be container tests.
"""
import re
import unittest
from pathlib import Path

DEPLOY = Path(__file__).resolve().parents[1] / "deploy"


class DeployConfigTests(unittest.TestCase):
    def test_dockerfile_uses_sealed_entrypoint(self):
        text = (DEPLOY / "Dockerfile").read_text(encoding="utf-8")
        self.assertIn("docker-entrypoint.py", text)
        self.assertIn("ENTRYPOINT", text)
        # No knowledge, secrets, or private data baked into the image.
        for banned in ("private-knowledge", "tianji-private", "COPY src/",
                       "COPY data/", "API_KEY", "ADMIN_READ_TOKEN"):
            self.assertNotIn(banned, text, f"banned in Dockerfile: {banned}")

    def test_dockerignore_next_to_dockerfile(self):
        # Build context is the repo root; Docker reads deploy/Dockerfile.dockerignore.
        ignore = DEPLOY / "Dockerfile.dockerignore"
        self.assertTrue(ignore.is_file(), "deploy/Dockerfile.dockerignore must exist")
        text = ignore.read_text(encoding="utf-8")
        for required in (".git", ".env", "data/", "private", "src/", "web/"):
            self.assertIn(required, text, f"must ignore {required}")
        # The misplaced deploy/.dockerignore must not exist (it never applied).
        self.assertFalse((DEPLOY / ".dockerignore").exists(),
                         "deploy/.dockerignore is misplaced and must be removed")

    def test_compose_sealed_mount_readonly_and_pinned(self):
        text = (DEPLOY / "docker-compose.yml").read_text(encoding="utf-8")
        self.assertIn(":/sealed:ro", text)
        self.assertIn("TIANJI_RUNTIME_MODE: sealed", text)
        self.assertIn("TIANJI_RUNTIME_ROOT: /sealed", text)
        self.assertIn("TIANJI_RUNTIME_SHA256: ${TIANJI_RUNTIME_SHA256:?",
                      text)
        # No hardcoded secrets.
        for banned in ("sk-", "Bearer ", "ADMIN_READ_TOKEN="):
            self.assertNotIn(banned, text, f"banned in compose: {banned}")

    def test_nginx_denies_hidden_and_proxies_api(self):
        text = (DEPLOY / "nginx.conf").read_text(encoding="utf-8")
        self.assertIn("location /api/", text)
        self.assertIn("proxy_pass http://api:8000", text)
        self.assertIn("try_files", text)  # SPA fallback
        self.assertRegex(text, r"location ~ /\\\.")

    def test_entrypoint_verifies_sealed_bundle(self):
        text = (DEPLOY / "docker-entrypoint.py").read_text(encoding="utf-8")
        # Must verify: sealed mode, absolute root, 64-hex pin,
        # code loaded from the bundle, resolver.ROOT consistency.
        for required in ("TIANJI_RUNTIME_MODE", "TIANJI_RUNTIME_ROOT",
                         "TIANJI_RUNTIME_SHA256", "resolver.ROOT",
                         "[0-9a-f]{64}", "sys.exit(1)"):
            self.assertIn(required, text, f"entrypoint must check {required}")

    def test_accept_script_exists_and_is_executable(self):
        script = DEPLOY / "accept-sealed.sh"
        self.assertTrue(script.is_file())
        import os, stat
        self.assertTrue(bool(os.stat(script).st_mode & stat.S_IXUSR))
        text = script.read_text(encoding="utf-8")
        for required in ("export_sealed_runtime.py", "TIANJI_RUNTIME_SHA256",
                         "docker compose", "/health", "wrong pin",
                         "ALL SEALED ACCEPTANCE CHECKS PASSED"):
            self.assertIn(required, text, f"accept script must cover {required}")


if __name__ == "__main__":
    unittest.main()
