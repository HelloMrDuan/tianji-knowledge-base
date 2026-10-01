"""Upstream refresh stages candidates; it cannot promote canonical content."""
import hashlib
import re
from pathlib import Path


def stage_update(root: Path, target: str, source_id: str, commit: str, content: str) -> tuple[Path, bool]:
    destination = (root / target).resolve()
    if not destination.is_relative_to(root.resolve()) or Path(target).is_absolute():
        raise ValueError('Refresh target escapes repository')
    if target.startswith('data/canonical/'):
        if destination.exists() and destination.read_text(encoding='utf-8') == content:
            return destination, False
        if not all(re.fullmatch(r'[A-Za-z0-9_.-]+', part) and part not in ('.', '..') for part in (source_id, commit)):
            raise ValueError('Unsafe candidate source/commit')
        key = hashlib.sha256(target.encode()).hexdigest()[:16]
        destination = root / 'data/quarantine/refresh_candidates' / source_id / commit / f'{key}-{Path(target).name}'
    if not destination.resolve().is_relative_to(root.resolve()):
        raise ValueError('Refresh candidate escapes repository')
    old = destination.read_text(encoding='utf-8') if destination.exists() else None
    changed = old != content
    if changed:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding='utf-8')
    return destination, changed
