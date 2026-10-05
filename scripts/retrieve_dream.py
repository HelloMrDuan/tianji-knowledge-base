#!/usr/bin/env python3
"""Research CLI for reviewed dream culture; no model or public scenario calls."""
import argparse
import json

from tianji_kb.operations.dream_knowledge import retrieve

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dream_text')
    args = parser.parse_args()
    print(json.dumps(retrieve(args.dream_text), ensure_ascii=False, indent=2))
