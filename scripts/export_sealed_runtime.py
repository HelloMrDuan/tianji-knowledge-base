#!/usr/bin/env python3
"""Export two pinned server-only artifacts; pass an absolute destination."""
import argparse
import json
from pathlib import Path

from tianji_kb.resolver import ROOT
from tianji_kb.sealed_bundle import export_sealed_bundle


def main():
    parser = argparse.ArgumentParser(description='Export private server runtime to an external directory')
    parser.add_argument('--destination', required=True, type=Path)
    args = parser.parse_args()
    if not args.destination.is_absolute():
        parser.error('--destination must be absolute')
    checksums = export_sealed_bundle(ROOT, args.destination)
    print(json.dumps({'mode': 'sealed', 'sha256_pin': checksums['production_runtime.json'],
                      'retrieval_sha256': checksums['production_rag.jsonl']}, sort_keys=True))


if __name__ == '__main__':
    main()
