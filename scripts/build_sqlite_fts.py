#!/usr/bin/env python3
from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAG = ROOT / "build/rag_chunks.jsonl"
DB = ROOT / "build/tianji_knowledge.sqlite3"

if not RAG.exists():
    subprocess.run([sys.executable, str(ROOT / "scripts/build_rag_chunks.py")], check=True)

rows = []
with RAG.open("r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            rows.append(json.loads(line))

DB.parent.mkdir(parents=True, exist_ok=True)
if DB.exists():
    DB.unlink()

con = sqlite3.connect(DB)
try:
    con.execute("PRAGMA journal_mode=DELETE")
    con.execute("""
        CREATE TABLE chunks (
            id TEXT PRIMARY KEY,
            text TEXT NOT NULL,
            domain TEXT,
            topic TEXT,
            ruleset TEXT,
            school TEXT,
            license TEXT,
            canonical_path TEXT,
            repo TEXT,
            source_path TEXT,
            commit_sha TEXT,
            metadata_json TEXT NOT NULL
        )
    """)
    try:
        con.execute("""
            CREATE VIRTUAL TABLE chunks_fts USING fts5(
                id UNINDEXED,
                text,
                domain,
                topic,
                ruleset,
                school,
                content='chunks',
                content_rowid='rowid',
                tokenize='unicode61'
            )
        """)
    except sqlite3.OperationalError as exc:
        raise SystemExit(f"SQLite FTS5 is required: {exc}") from exc

    for row in rows:
        meta = row.get("metadata") or {}
        cur = con.execute("""
            INSERT INTO chunks(
                id,text,domain,topic,ruleset,school,license,canonical_path,
                repo,source_path,commit_sha,metadata_json
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            row["id"],
            row["text"],
            meta.get("domain"),
            meta.get("topic"),
            meta.get("ruleset"),
            meta.get("school"),
            meta.get("license"),
            meta.get("canonical_path"),
            meta.get("repo"),
            meta.get("path"),
            meta.get("commit"),
            json.dumps(meta, ensure_ascii=False, sort_keys=True),
        ))
        rowid = cur.lastrowid
        con.execute("""
            INSERT INTO chunks_fts(rowid,id,text,domain,topic,ruleset,school)
            VALUES (?,?,?,?,?,?,?)
        """, (
            rowid, row["id"], row["text"], meta.get("domain"), meta.get("topic"),
            meta.get("ruleset"), meta.get("school")
        ))

    con.execute("CREATE INDEX idx_chunks_domain ON chunks(domain)")
    con.execute("CREATE INDEX idx_chunks_topic ON chunks(topic)")
    con.execute("CREATE INDEX idx_chunks_ruleset ON chunks(ruleset)")
    con.execute("CREATE INDEX idx_chunks_repo_commit ON chunks(repo, commit_sha)")
    con.commit()

    counts = dict(con.execute(
        "SELECT COALESCE(domain,'unknown'), COUNT(*) FROM chunks GROUP BY domain ORDER BY domain"
    ).fetchall())
    total = con.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
    print(json.dumps({
        "database": DB.relative_to(ROOT).as_posix(),
        "chunk_count": total,
        "domain_counts": counts,
        "fts5": True,
    }, ensure_ascii=False, indent=2))
finally:
    con.close()
