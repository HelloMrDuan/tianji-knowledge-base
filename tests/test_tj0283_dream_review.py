"""TJ-028.3: dream review draft validation and review-reason records.

The review draft reuses the existing draft store: this file pins the
dream layer (only an explained result with valid claims/evidence may
enter review) and the reason records (transition entries and SQLite
rows carry the human reason; an old database without the reason
column gains it on first open).
"""

import copy
import sqlite3
import tempfile
import unittest
from pathlib import Path

from tianji_kb.admin_drafts import DraftStore, InvalidTransitionError
from tianji_kb.admin_storage import SqliteDraftStore
from tianji_kb.dream_review import (
    DreamReviewError,
    build_dream_review_draft,
    is_dream_review_body,
    parse_dream_review_body,
    validate_review_reason,
)

EID = "a1b2c3d4e5f6a7b8c9d0e1f2"
QUOTE = "见人死自死皆吉"


def _explained_result():
    return {
        "dream_text": "我梦见自己死了",
        "elements": [
            {
                "term_id": "dream.term.death",
                "symbol": "死亡",
                "scene": "见人死自死",
                "source": "周公解梦",
                "evidence_ids": [EID],
            }
        ],
        "verdict": "explained",
        "ai_enabled": False,
        "personal_prediction": False,
        "claims": [
            {
                "text": "《周公解梦》载“见人死自死皆吉”，此条仅言梦中见人死自死的传统说法，不作个人运势判断。",
                "evidence_ids": [EID],
                "quotes": [{"evidence_id": EID, "text": QUOTE}],
                "citations": [{"evidence_id": EID, "source_ref": {}}],
            }
        ],
        "evidence": {
            EID: {
                "source_id": "dream.source.zhougong-scenes",
                "original_text": QUOTE,
                "classic_title": "周公解梦（电子本题名）",
                "locator": "周公解梦·十八、哀乐 病死 歌唱",
            }
        },
        "limitations": [],
        "reason": None,
    }


class BuildTests(unittest.TestCase):
    def test_valid_explained_result_builds_a_review_draft(self):
        title, body = build_dream_review_draft(_explained_result())
        self.assertIn("AI 解梦研究草稿", title)
        self.assertTrue(is_dream_review_body(body))
        parsed = parse_dream_review_body(body)
        self.assertEqual(parsed["verdict"], "explained")
        self.assertEqual(parsed["dream_text"], "我梦见自己死了")

    def test_refusal_cannot_enter_review(self):
        result = _explained_result()
        result["verdict"] = "abstained_no_reviewed_interpretation"
        with self.assertRaises(DreamReviewError) as caught:
            build_dream_review_draft(result)
        self.assertEqual(caught.exception.code, "refusal_not_reviewable")

    def test_empty_claims_is_incomplete_evidence(self):
        result = _explained_result()
        result["claims"] = []
        with self.assertRaises(DreamReviewError) as caught:
            build_dream_review_draft(result)
        self.assertEqual(caught.exception.code, "incomplete_evidence")

    def test_forged_evidence_id_is_invalid_citation(self):
        result = _explained_result()
        result["claims"][0]["evidence_ids"] = ["deadbeef" * 3]
        with self.assertRaises(DreamReviewError) as caught:
            build_dream_review_draft(result)
        self.assertEqual(caught.exception.code, "invalid_citation")

    def test_non_verbatim_quote_is_invalid_citation(self):
        result = _explained_result()
        result["claims"][0]["quotes"] = [{"evidence_id": EID, "text": "见人死自死皆大吉大利"}]
        with self.assertRaises(DreamReviewError) as caught:
            build_dream_review_draft(result)
        self.assertEqual(caught.exception.code, "invalid_citation")

    def test_diagnosis_text_is_invalid_citation(self):
        result = _explained_result()
        result["claims"][0]["text"] = "《周公解梦》载“见人死自死皆吉”，你患有焦虑症。"
        with self.assertRaises(DreamReviewError) as caught:
            build_dream_review_draft(result)
        self.assertEqual(caught.exception.code, "invalid_citation")

    def test_fabricated_classic_title_is_invalid_citation(self):
        result = _explained_result()
        result["claims"][0]["text"] = "《伪造古籍》载“见人死自死皆吉”，此条仅言传统说法。"
        with self.assertRaises(DreamReviewError) as caught:
            build_dream_review_draft(result)
        self.assertEqual(caught.exception.code, "invalid_citation")

    def test_plain_text_body_is_not_a_dream_draft(self):
        self.assertFalse(is_dream_review_body("just a title body"))
        self.assertIsNone(parse_dream_review_body("just a title body"))

    def test_corrupted_dream_body_is_still_a_dream_draft(self):
        import json

        _, body = build_dream_review_draft(_explained_result())
        parsed = json.loads(body)
        # Corrupt only the claim's quote: the evidence still carries
        # the real text, so the quote is no longer verbatim.
        parsed["result"]["claims"][0]["quotes"][0]["text"] = "见人死自死皆大吉大利"
        corrupted = json.dumps(parsed, ensure_ascii=False)
        self.assertTrue(is_dream_review_body(corrupted))
        with self.assertRaises(DreamReviewError) as caught:
            parse_dream_review_body(corrupted)
        self.assertEqual(caught.exception.code, "invalid_citation")


class ReasonTests(unittest.TestCase):
    def test_review_reason_validation(self):
        self.assertEqual(validate_review_reason("  证据链完整，通过。 "), "证据链完整，通过。")
        with self.assertRaises(DreamReviewError):
            validate_review_reason("   ")
        with self.assertRaises(DreamReviewError):
            validate_review_reason("x" * 501)

    def test_memory_store_records_the_reason(self):
        store = DraftStore()
        draft = store.create("t", "b", "editor")
        moved = store.transition(draft["id"], "submit", "editor", reason="已核对梦象，提交审核。")
        self.assertEqual(moved["transitions"][-1]["reason"], "已核对梦象，提交审核。")
        self.assertEqual(moved["transitions"][0].get("reason"), None)
        with self.assertRaises(InvalidTransitionError):
            store.transition(draft["id"], "approve", "reviewer", reason="x" * 501)

    def test_sqlite_store_persists_reason_across_reopen(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "admin.db")
            store = SqliteDraftStore(path)
            draft = store.create("t", "b", "editor")
            store.transition(draft["id"], "submit", "editor", reason="提交审核。")
            reopened = SqliteDraftStore(path)
            record = reopened.get(draft["id"])
            self.assertEqual(record["transitions"][-1]["reason"], "提交审核。")
            reopened.transition(draft["id"], "approve", "reviewer", reason="证据链完整，通过。")
            self.assertEqual(
                SqliteDraftStore(path).get(draft["id"])["transitions"][-1]["reason"],
                "证据链完整，通过。",
            )

    def test_old_database_without_reason_column_is_migrated(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "old.db")
            conn = sqlite3.connect(path)
            conn.executescript(
                "CREATE TABLE audit_entries (seq INTEGER PRIMARY KEY AUTOINCREMENT,"
                " who TEXT NOT NULL, when_iso TEXT NOT NULL, what TEXT NOT NULL,"
                " outcome TEXT NOT NULL, detail TEXT);"
                "CREATE TABLE draft_id_seq (seq INTEGER PRIMARY KEY AUTOINCREMENT);"
                "CREATE TABLE drafts (id TEXT PRIMARY KEY, seq INTEGER NOT NULL,"
                " title TEXT NOT NULL, body TEXT NOT NULL, author_role TEXT NOT NULL,"
                " status TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL);"
                "CREATE TABLE draft_versions (draft_id TEXT NOT NULL, version INTEGER NOT NULL,"
                " title TEXT NOT NULL, body TEXT NOT NULL, action TEXT NOT NULL,"
                " role TEXT NOT NULL, at TEXT NOT NULL, PRIMARY KEY (draft_id, version));"
                "CREATE TABLE draft_transitions (seq INTEGER PRIMARY KEY AUTOINCREMENT,"
                " draft_id TEXT NOT NULL, action TEXT NOT NULL, role TEXT NOT NULL,"
                " at TEXT NOT NULL, version INTEGER);"
            )
            conn.execute("INSERT INTO draft_id_seq DEFAULT VALUES")
            conn.execute(
                "INSERT INTO drafts VALUES ('D-1', 1, 't', 'b', 'editor', 'draft', 't0', 't0')"
            )
            conn.execute(
                "INSERT INTO draft_versions VALUES ('D-1', 1, 't', 'b', 'create', 'editor', 't0')"
            )
            conn.execute(
                "INSERT INTO draft_transitions (draft_id, action, role, at, version)"
                " VALUES ('D-1', 'create', 'editor', 't0', NULL)"
            )
            conn.commit()
            conn.close()
            store = SqliteDraftStore(path)
            record = store.get("D-1")
            self.assertNotIn("reason", record["transitions"][0])
            moved = store.transition("D-1", "submit", "editor", reason="迁移后仍可记录原因。")
            self.assertEqual(moved["transitions"][-1]["reason"], "迁移后仍可记录原因。")


if __name__ == "__main__":
    unittest.main()
