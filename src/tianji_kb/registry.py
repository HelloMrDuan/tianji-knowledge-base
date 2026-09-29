from __future__ import annotations

import json
from pathlib import Path


def load_registry(path: str | Path) -> list[dict]:
    return json.loads(Path(path).read_text(encoding="utf-8"))["sources"]
