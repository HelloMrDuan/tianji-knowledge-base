#!/usr/bin/env python3
"""TJ-027.2: deployment readiness probe (API contract + served frontend assets).

This is a smoke check, not a browser end-to-end test or proof of production rollout.
Usage: python scripts/health_check.py [--api URL] [--frontend URL]
Exit 0 only if every concrete HTTP response meets its contract.
"""
import argparse
from html.parser import HTMLParser
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

LEAK_MARKERS = ("traceback", "tianji-private", "private-knowledge", "/root/", "/home/")


def _fetch(url):
    with urllib.request.urlopen(url, timeout=10) as response:
        body = response.read(2 * 1024 * 1024 + 1)
        if response.status != 200:
            raise ValueError("HTTP %s" % response.status)
        if len(body) > 2 * 1024 * 1024:
            raise ValueError("response too large")
        return body, response.headers.get("Content-Type", "")


def _no_leak(body):
    lowered = body.decode("utf-8", errors="replace").lower()
    return not any(marker in lowered for marker in LEAK_MARKERS)


class _FrontendParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.has_root = False
        self.modules = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "div" and attrs.get("id") == "root":
            self.has_root = True
        if tag == "script" and attrs.get("type") == "module" and attrs.get("src"):
            self.modules.append(attrs["src"])


def _verify(url, name):
    body, ctype = _fetch(url)
    if not _no_leak(body):
        raise ValueError("private/internal marker in response")
    if name == "frontend/home":
        if "text/html" not in ctype.lower():
            raise ValueError("frontend did not serve HTML")
        parser = _FrontendParser()
        parser.feed(body.decode("utf-8", errors="replace"))
        if not parser.has_root or not parser.modules:
            raise ValueError("missing app root or production module script")
        home = urllib.parse.urlsplit(url)
        for module_path in parser.modules:
            module_url = urllib.parse.urljoin(url, module_path)
            parsed = urllib.parse.urlsplit(module_url)
            if ((parsed.scheme, parsed.netloc) != (home.scheme, home.netloc)
                    or not parsed.path.endswith(".js")):
                raise ValueError("module asset is not a same-origin JavaScript file")
            script, script_ctype = _fetch(module_url)
            if (not script or not _no_leak(script)
                    or "javascript" not in script_ctype.lower()
                    or script.lstrip().lower().startswith(b"<!doctype html")):
                raise ValueError("frontend module asset was not served as JavaScript")
    else:
        if "json" not in ctype.lower():
            raise ValueError("API did not serve JSON")
        payload = json.loads(body)
        if not isinstance(payload, dict):
            raise ValueError("API response is not an object")
        if name == "api/health":
            if payload.get("status") != "ok" or payload.get("engine") != "ready":
                raise ValueError("API engine not ready")
        elif name == "api/capabilities":
            domains = payload.get("domains")
            if not isinstance(domains, list) or not domains:
                raise ValueError("API capabilities have no domains")
    return True, "%s: OK" % name


def check(url, name, expect_json=True):
    """Compatibility wrapper: return (success, detail), never silently accept HTTP 200."""
    try:
        return _verify(url, name)
    except (OSError, ValueError, UnicodeError, json.JSONDecodeError) as exc:
        return False, "%s: %s" % (name, type(exc).__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--api", default="http://127.0.0.1:8000")
    parser.add_argument("--frontend", default="http://127.0.0.1:8080")
    args = parser.parse_args()
    checks = [
        check(args.api.rstrip("/") + "/health", "api/health"),
        check(args.api.rstrip("/") + "/api/v1/capabilities", "api/capabilities"),
        check(args.frontend.rstrip("/") + "/", "frontend/home", expect_json=False),
    ]
    for _, message in checks:
        print(message)
    return 0 if all(passed for passed, _ in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
