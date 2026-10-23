"""TJ-027.2: real loopback HTTP probes for fail-closed deployment health checks."""
import threading
import unittest
from unittest.mock import patch
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from scripts.health_check import check, main


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        status, mime, body = self.server.routes.get(
            self.path, (404, "text/plain", b"missing"))
        self.send_response(status)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class HealthCheckTests(unittest.TestCase):
    def setUp(self):
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
        self.server.routes = {
            "/health": (200, "application/json", b'{"status":"ok","engine":"ready"}'),
            "/api/v1/capabilities": (
                200, "application/json",
                b'{"api_version":"v1","domains":[{"domain":"bazi"}]}'),
            "/": (200, "text/html",
                  b'<!doctype html><html><body><div id="root"></div>'
                  b'<script type="module" src="/assets/index-123.js"></script></body></html>'),
            "/assets/index-123.js": (
                200, "application/javascript", b'console.log("ready");'),
        }
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = "http://127.0.0.1:%d" % self.server.server_port

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

    def probe(self, path, name):
        return check(self.base + path, name)[0]

    def test_real_api_and_frontend_assets_pass(self):
        self.assertTrue(self.probe("/health", "api/health"))
        self.assertTrue(self.probe("/api/v1/capabilities", "api/capabilities"))
        self.assertTrue(self.probe("/", "frontend/home"))

    def test_api_200_with_unready_engine_fails(self):
        self.server.routes["/health"] = (
            200, "application/json", b'{"status":"degraded","engine":"ready"}')
        self.assertFalse(self.probe("/health", "api/health"))

    def test_capabilities_200_without_domains_fails(self):
        self.server.routes["/api/v1/capabilities"] = (
            200, "application/json", b'{"scenarios":[]}')
        self.assertFalse(self.probe("/api/v1/capabilities", "api/capabilities"))

    def test_api_html_fallback_is_not_json(self):
        self.server.routes["/health"] = (
            200, "text/html", b'<html>not an API</html>')
        self.assertFalse(self.probe("/health", "api/health"))

    def test_frontend_html_without_module_rejected(self):
        self.server.routes["/"] = (
            200, "text/html", b'<html><div id="root"></div></html>')
        self.assertFalse(self.probe("/", "frontend/home"))

    def test_frontend_broken_module_rejected(self):
        self.server.routes["/assets/index-123.js"] = (
            404, "text/plain", b'not found')
        self.assertFalse(self.probe("/", "frontend/home"))

    def test_spa_fallback_served_as_javascript_rejected(self):
        self.server.routes["/assets/index-123.js"] = (
            200, "text/html", b'<!doctype html><html>fallback</html>')
        self.assertFalse(self.probe("/", "frontend/home"))

    def test_cross_origin_module_rejected(self):
        self.server.routes["/"] = (
            200, "text/html",
            b'<div id="root"></div><script type="module" '
            b'src="https://example.net/app.js"></script>')
        self.assertFalse(self.probe("/", "frontend/home"))

    def test_gateway_capabilities_contract(self):
        # Exercise the real loopback HTTP client with the gateway label.
        self.assertTrue(self.probe("/api/v1/capabilities", "gateway/capabilities"))
        self.server.routes["/api/v1/capabilities"] = (
            200, "text/html", b"<html>SPA fallback instead of API</html>")
        self.assertFalse(self.probe("/api/v1/capabilities", "gateway/capabilities"))

    def test_main_rejects_broken_frontend_api_proxy(self):
        # Direct API works, frontend HTML and JS work, only /api proxy is broken.
        frontend = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
        frontend.routes = {
            key: value for key, value in self.server.routes.items()
            if key != "/api/v1/capabilities"
        }
        thread = threading.Thread(target=frontend.serve_forever, daemon=True)
        thread.start()
        try:
            frontend_base = "http://127.0.0.1:%d" % frontend.server_port
            with patch("sys.argv", ["health_check.py", "--api", self.base,
                                    "--frontend", frontend_base]):
                self.assertEqual(main(), 1)
        finally:
            frontend.shutdown()
            frontend.server_close()
            thread.join(timeout=2)

    def test_main_accepts_healthy_frontend_api_proxy(self):
        with patch("sys.argv", ["health_check.py", "--api", self.base,
                                "--frontend", self.base]):
            self.assertEqual(main(), 0)

    def test_leak_marker_rejected(self):
        self.server.routes["/health"] = (
            200, "application/json", b'{"status":"ok","engine":"ready","error":"traceback"}')
        self.assertFalse(self.probe("/health", "api/health"))


if __name__ == "__main__":
    unittest.main()
