#!/usr/bin/env python3
"""TJ-027.2: deployment health check.

Probes the API and frontend endpoints, reports status.
Usage: python scripts/health_check.py [--api URL] [--frontend URL]
Exit 0 if all checks pass, 1 otherwise.
"""
import argparse
import sys
import urllib.request
import urllib.error
import json


def check(url, name, expect_json=True):
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            body = resp.read()
            if resp.status != 200:
                return False, f"{name}: HTTP {resp.status}"
            if expect_json:
                data = json.loads(body)
                # Health must not leak internals.
                text = body.decode('utf-8', errors='ignore').lower()
                for marker in ("traceback", "tianji-private", "/root/"):
                    if marker in text:
                        return False, f"{name}: leak marker {marker}"
            return True, f"{name}: OK"
    except urllib.error.HTTPError as e:
        return False, f"{name}: HTTP {e.code}"
    except Exception as e:
        return False, f"{name}: {e}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--api", default="http://127.0.0.1:8000")
    parser.add_argument("--frontend", default="http://127.0.0.1:8080")
    args = parser.parse_args()
    checks = [
        check(f"{args.api}/health", "api/health"),
        check(f"{args.api}/api/v1/capabilities", "api/capabilities"),
        check(f"{args.frontend}/", "frontend/home", expect_json=False),
    ]
    ok = True
    for passed, msg in checks:
        print(msg)
        ok = ok and passed
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
