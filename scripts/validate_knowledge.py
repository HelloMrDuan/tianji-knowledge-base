#!/usr/bin/env python3
from pathlib import Path
from tianji_kb.knowledge import validate_knowledge, validate_protected_files

root = Path(__file__).resolve().parents[1]
validate_protected_files(root)
model = validate_knowledge(root)
print(f"Phase 1 model validated: {len(model['bundles'])} domains, {len(model['entities'])} entities")
