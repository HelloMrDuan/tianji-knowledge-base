#!/usr/bin/env python3
"""Sealed-runtime entrypoint: fail fast unless the pinned sealed bundle is in use.

Verifies BEFORE serving traffic:
1. TIANJI_RUNTIME_MODE=sealed, absolute TIANJI_RUNTIME_ROOT, 64-hex SHA pin.
2. `import tianji_kb` resolves INSIDE the sealed bundle (not site-packages).
3. resolver.ROOT (derived from the code location) equals the sealed root.

The full SHA-pin integrity check runs inside load_catalog() on first request;
this gate ensures we never even start with the wrong code.
"""
import os
import re
import sys


def fail(message):
    print(f"SEALED BOOT REFUSED: {message}", file=sys.stderr, flush=True)
    sys.exit(1)


mode = os.environ.get("TIANJI_RUNTIME_MODE", "")
root = os.environ.get("TIANJI_RUNTIME_ROOT", "")
pin = os.environ.get("TIANJI_RUNTIME_SHA256", "")
if mode != "sealed":
    fail("TIANJI_RUNTIME_MODE must be 'sealed'")
if not root or not os.path.isabs(root):
    fail("TIANJI_RUNTIME_ROOT must be an absolute path")
if not re.fullmatch(r"[0-9a-f]{64}", pin or ""):
    fail("TIANJI_RUNTIME_SHA256 must be a 64-char hex pin")

sys.path.insert(0, os.path.join(root, "src"))
try:
    import tianji_kb
    from tianji_kb.resolver import ROOT
except ImportError as error:
    fail(f"cannot import tianji_kb from sealed bundle: {error}")

code_file = tianji_kb.__file__ or ""
if not code_file.startswith(root + "/src/"):
    fail(f"tianji_kb not loaded from sealed bundle: {code_file}")
if str(ROOT) != root:
    fail(f"resolver.ROOT {ROOT} != sealed root {root}")

print(f"sealed runtime verified: code={code_file} root={ROOT}",
      flush=True)
os.execvp("python", ["python", "-m", "uvicorn", "tianji_kb.api:create_app",
                     "--factory", "--host", "0.0.0.0", "--port", "8000",
                     "--workers", "2"])
