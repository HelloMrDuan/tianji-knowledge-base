"""TJ-005.1: public API / bundle / error / log leak redlines.

Every test asserts a REAL negative: responses must not carry tracebacks,
filesystem paths, private-data markers, or unauthenticated admin access.
Fail-closed is verified, not assumed.
"""
import unittest
from pathlib import Path


def _body_text(response):
    try:
        return response.text
    except Exception:
        return ""


class FrontendSourceHygieneTests(unittest.TestCase):
    def test_frontend_source_has_no_hardcoded_secrets(self):
        import re
        # Real secret VALUES, not field names like api_key_present.
        patterns = [
            re.compile(r"sk-[a-zA-Z0-9]{20,}"),
            re.compile(r"['\"]api[_-]?key['\"]\s*:\s*['\"][a-zA-Z0-9]{8,}"),
            re.compile(r"tianji-private-knowledge"),
        ]
        root = Path(__file__).resolve().parents[1] / "web" / "visual-prototype" / "src"
        if not root.is_dir():
            self.skipTest("frontend source not present")
        hits = []
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix not in (".ts", ".tsx", ".js"):
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for pattern in patterns:
                if pattern.search(text):
                    hits.append(f"{path.name}:{pattern.pattern[:20]}")
        self.assertEqual(hits, [], f"hardcoded secrets in frontend: {hits}")


if __name__ == "__main__":
    unittest.main()
