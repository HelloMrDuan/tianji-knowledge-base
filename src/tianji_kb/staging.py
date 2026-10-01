"""Upstream refresh stages candidates; it cannot promote canonical content."""
import hashlib
from pathlib import Path


def stage_update(root: Path, target: str, source_id: str, commit: str, content: str) -> tuple[Path, bool]:
    destination = (root / target).resolve()
    if not destination.is_relative_to(root.resolve()) or Path(target).is_absolute():
        raise ValueError('Refresh target escapes repository')
    if target.startswith('data/canonical/'):
        key = hashlib.sha256(target.encode()).hexdigest()[:16]
        destination = root / 'data/quarantine/refresh_candidates' / source_id / commit / f'{key}-{Path(target).name}'
    old = destination.read_text(encoding='utf-8') if destination.exists() else None
    changed = old != content
    if changed:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding='utf-8')
    return destination, changed
