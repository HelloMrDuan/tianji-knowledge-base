#!/usr/bin/env python3
"""Explicitly inspect an approved source update; never auto-promote its body."""
import argparse
import json
from pathlib import Path
from urllib.parse import quote

from tianji_kb.acquisition import stage_candidate
from tianji_kb.github import GitHubClient
from tianji_kb.knowledge import read_json

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', help='Exact ID from config/knowledge_sources.json')
    parser.add_argument('--discover-head', action='store_true', help='Compare the latest upstream commit and file blob with the pinned version')
    args = parser.parse_args()
    sources = {s['source_id']: s for s in read_json(ROOT / 'config/knowledge_sources.json')['sources']}
    if not args.source:
        print('\n'.join(sorted(sources)))
        return
    if args.source not in sources:
        parser.error('Source is not in the reviewed registry')
    source = sources[args.source]
    client = GitHubClient()
    repo = source['repository']
    commit = source['commit']
    api_path = f'/repos/{repo}/contents/{quote(source["path"], safe="/")}'
    baseline = client.api(api_path, {'ref': commit})['sha']
    if args.discover_head:
        branch = client.repo(repo)['default_branch']
        commit = client.latest_commit(repo, branch)['sha']
    meta = client.api(api_path, {'ref': commit})
    content = client.fetch_text_file(repo, source['path'], ref=commit).encode('utf-8')
    result = stage_candidate(ROOT, source, commit, content, meta['sha'], baseline)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
