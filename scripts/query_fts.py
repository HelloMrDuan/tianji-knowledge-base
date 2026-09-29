#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sqlite3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "build/tianji_knowledge.sqlite3"

parser = argparse.ArgumentParser()
parser.add_argument("query")
parser.add_argument("--domain")
parser.add_argument("--topic")
parser.add_argument("--ruleset")
parser.add_argument("--school")
parser.add_argument("--limit", type=int, default=10)
parser.add_argument("--rebuild", action="store_true")
args = parser.parse_args()

if args.rebuild or not DB.exists():
    subprocess.run([sys.executable, str(ROOT / "scripts/build_sqlite_fts.py")], check=True)

con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row
try:
    clauses = ["chunks_fts MATCH ?"]
    params: list[object] = [args.query]
    for col, value in [
        ("c.domain", args.domain),
        ("c.topic", args.topic),
        ("c.ruleset", args.ruleset),
        ("c.school", args.school),
    ]:
        if value:
            clauses.append(f"{col} = ?")
            params.append(value)

    params.append(args.limit)
    sql = f"""
        SELECT
            c.id,
            c.text,
            c.domain,
            c.topic,
            c.ruleset,
            c.school,
            c.license,
            c.canonical_path,
            c.repo,
            c.source_path,
            c.commit_sha,
            bm25(chunks_fts) AS rank
        FROM chunks_fts
        JOIN chunks c ON c.rowid = chunks_fts.rowid
        WHERE {' AND '.join(clauses)}
        ORDER BY rank
        LIMIT ?
    """
    try:
        rows = [dict(x) for x in con.execute(sql, params).fetchall()]
    except sqlite3.OperationalError:
        # Chinese multi-character phrases may not tokenize as the caller expects.
        # Fall back to literal substring search while preserving metadata filters.
        clauses = ["c.text LIKE ?"]
        params = [f"%{args.query}%"]
        for col, value in [
            ("c.domain", args.domain),
            ("c.topic", args.topic),
            ("c.ruleset", args.ruleset),
            ("c.school", args.school),
        ]:
            if value:
                clauses.append(f"{col} = ?")
                params.append(value)
        params.append(args.limit)
        rows = [dict(x) for x in con.execute(f"""
            SELECT c.*, NULL AS rank
            FROM chunks c
            WHERE {' AND '.join(clauses)}
            ORDER BY c.domain, c.topic, c.id
            LIMIT ?
        """, params).fetchall()]
        for row in rows:
            row.pop("metadata_json", None)

    print(json.dumps(rows, ensure_ascii=False, indent=2))
finally:
    con.close()
