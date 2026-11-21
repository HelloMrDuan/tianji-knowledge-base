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
    DREAM_REVIEW_MARKER,
    DreamReviewError,
    build_dream_review_draft,
    extract_dream_review_result,
    is_dream_review_body,
    parse_dream_review_body,
    validate_result_against_retrieval,
    validate_review_reason,
)

EID = "a1b2c3d4e5f6a7b8c9d0e1f2"
QUOTE = "见人死自死皆吉"


def _retrieval_fixture():
    """The server-side audited retrieval for _explained_result().

    The trusted evidence record is identical to the submitted one,
    and the matched interpretation matches the submitted element.
    """
    return {
        "domain": "dream",
        "mode": "research",
        "status": "reviewed_interpretation_candidates",
        "public_enabled": False,
        "ai_enabled": False,
        "matched_interpretations": [
            {
                "term_id": "dream.term.death",
                "symbol": "死亡",
                "scene": "见人死自死",
                "source": "周公解梦",
                "evidence_ids": [EID],
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
    }


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
        title, body = build_dream_review_draft(
            _explained_result(), retrieval=_retrieval_fixture()
        )
        self.assertIn("AI 解梦研究草稿", title)
        self.assertTrue(is_dream_review_body(body))
        parsed = parse_dream_review_body(body, retrieval=_retrieval_fixture())
        self.assertEqual(parsed["verdict"], "explained")
        self.assertEqual(parsed["dream_text"], "我梦见自己死了")

    def test_refusal_cannot_enter_review(self):
        result = _explained_result()
        result["verdict"] = "abstained_no_reviewed_interpretation"
        with self.assertRaises(DreamReviewError) as caught:
            build_dream_review_draft(result, retrieval=_retrieval_fixture())
        self.assertEqual(caught.exception.code, "refusal_not_reviewable")

    def test_empty_claims_is_incomplete_evidence(self):
        result = _explained_result()
        result["claims"] = []
        with self.assertRaises(DreamReviewError) as caught:
            build_dream_review_draft(result, retrieval=_retrieval_fixture())
        self.assertEqual(caught.exception.code, "incomplete_evidence")

    def test_forged_evidence_id_is_invalid_citation(self):
        result = _explained_result()
        result["claims"][0]["evidence_ids"] = ["deadbeef" * 3]
        with self.assertRaises(DreamReviewError) as caught:
            build_dream_review_draft(result, retrieval=_retrieval_fixture())
        self.assertEqual(caught.exception.code, "invalid_citation")

    def test_non_verbatim_quote_is_invalid_citation(self):
        result = _explained_result()
        result["claims"][0]["quotes"] = [{"evidence_id": EID, "text": "见人死自死皆大吉大利"}]
        with self.assertRaises(DreamReviewError) as caught:
            build_dream_review_draft(result, retrieval=_retrieval_fixture())
        self.assertEqual(caught.exception.code, "invalid_citation")

    def test_diagnosis_text_is_invalid_citation(self):
        result = _explained_result()
        result["claims"][0]["text"] = "《周公解梦》载“见人死自死皆吉”，你患有焦虑症。"
        with self.assertRaises(DreamReviewError) as caught:
            build_dream_review_draft(result, retrieval=_retrieval_fixture())
        self.assertEqual(caught.exception.code, "invalid_citation")

    def test_fabricated_classic_title_is_invalid_citation(self):
        result = _explained_result()
        result["claims"][0]["text"] = "《伪造古籍》载“见人死自死皆吉”，此条仅言传统说法。"
        with self.assertRaises(DreamReviewError) as caught:
            build_dream_review_draft(result, retrieval=_retrieval_fixture())
        self.assertEqual(caught.exception.code, "invalid_citation")

    def test_fully_forged_but_self_consistent_evidence_is_untrusted(self):
        # A payload that is internally consistent (the forged quote
        # is verbatim against the forged record, the forged element
        # cites the forged id) but matches nothing in the audited
        # retrieval: it passed the old self-consistency check and
        # must now fail against the trusted retrieval.
        fake_id = "f" * 24
        fake_text = "伪造原文见人死皆吉"
        result = _explained_result()
        result["elements"][0]["evidence_ids"] = [fake_id]
        result["claims"][0]["text"] = (
            f"《周公解梦》载“{fake_text}”，此条仅言传统说法。"
        )
        result["claims"][0]["evidence_ids"] = [fake_id]
        result["claims"][0]["quotes"] = [{"evidence_id": fake_id, "text": fake_text}]
        result["evidence"] = {
            fake_id: {
                "source_id": "dream.source.forged",
                "original_text": fake_text,
                "classic_title": "周公解梦（电子本题名）",
                "locator": "伪造·一",
            }
        }
        with self.assertRaises(DreamReviewError) as caught:
            build_dream_review_draft(result, retrieval=_retrieval_fixture())
        self.assertEqual(caught.exception.code, "untrusted_evidence")

    def test_tampered_evidence_record_is_untrusted(self):
        # Same id, but the submitted record's original text differs
        # from the audited record; the claim quote is rewritten to
        # match the tampered record, so only the trusted check fails.
        tampered = "见人死自死皆大吉大利"
        result = _explained_result()
        result["evidence"][EID]["original_text"] = tampered
        result["claims"][0]["text"] = (
            f"《周公解梦》载“{tampered}”，此条仅言传统说法。"
        )
        result["claims"][0]["quotes"] = [{"evidence_id": EID, "text": tampered}]
        with self.assertRaises(DreamReviewError) as caught:
            build_dream_review_draft(result, retrieval=_retrieval_fixture())
        self.assertEqual(caught.exception.code, "untrusted_evidence")

    def test_element_not_matching_retrieval_is_untrusted(self):
        result = _explained_result()
        result["elements"][0]["scene"] = "见人死"
        with self.assertRaises(DreamReviewError) as caught:
            build_dream_review_draft(result, retrieval=_retrieval_fixture())
        self.assertEqual(caught.exception.code, "untrusted_evidence")

    def test_build_requires_a_trusted_retrieval(self):
        with self.assertRaises(DreamReviewError) as caught:
            build_dream_review_draft(_explained_result(), retrieval=None)
        self.assertEqual(caught.exception.code, "trusted_retrieval_unavailable")

    def test_plain_text_body_is_not_a_dream_draft(self):
        self.assertFalse(is_dream_review_body("just a title body"))
        self.assertIsNone(
            parse_dream_review_body("just a title body", retrieval=_retrieval_fixture())
        )
        self.assertIsNone(extract_dream_review_result("just a title body"))

    def test_corrupted_dream_body_is_still_a_dream_draft(self):
        import json

        _, body = build_dream_review_draft(
            _explained_result(), retrieval=_retrieval_fixture()
        )
        parsed = json.loads(body)
        # Corrupt only the claim's quote: the evidence still carries
        # the real text, so the quote is no longer verbatim.
        parsed["result"]["claims"][0]["quotes"][0]["text"] = "见人死自死皆大吉大利"
        corrupted = json.dumps(parsed, ensure_ascii=False)
        self.assertTrue(is_dream_review_body(corrupted))
        with self.assertRaises(DreamReviewError) as caught:
            parse_dream_review_body(corrupted, retrieval=_retrieval_fixture())
        self.assertEqual(caught.exception.code, "invalid_citation")

    def test_extract_is_structural_only_and_never_establishes_trust(self):
        # A fully forged but self-consistent body still extracts:
        # trust comes only from validate_result_against_retrieval.
        fake_id = "f" * 24
        fake_text = "伪造原文见人死皆吉"
        result = _explained_result()
        result["elements"][0]["evidence_ids"] = [fake_id]
        result["claims"][0]["text"] = (
            f"《周公解梦》载“{fake_text}”，此条仅言传统说法。"
        )
        result["claims"][0]["evidence_ids"] = [fake_id]
        result["claims"][0]["quotes"] = [{"evidence_id": fake_id, "text": fake_text}]
        result["evidence"] = {
            fake_id: {
                "source_id": "dream.source.forged",
                "original_text": fake_text,
                "classic_title": "周公解梦（电子本题名）",
                "locator": "伪造·一",
            }
        }
        import json

        forged_body = json.dumps(
            {"kind": "dream_ai_review", "result": result}, ensure_ascii=False
        )
        extracted = extract_dream_review_result(forged_body)
        self.assertEqual(extracted["dream_text"], "我梦见自己死了")
        with self.assertRaises(DreamReviewError) as caught:
            validate_result_against_retrieval(extracted, _retrieval_fixture())
        self.assertEqual(caught.exception.code, "untrusted_evidence")


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


class MarkerTests(unittest.TestCase):
    def test_marker_constant(self):
        self.assertEqual(DREAM_REVIEW_MARKER, "dream_ai")

    def test_memory_store_marker_survives_edit_transition_and_rollback(self):
        store = DraftStore()
        plain = store.create("t", "b", "editor")
        self.assertIsNone(plain["review_kind"])
        draft = store.create("t", "b", "editor", review_kind=DREAM_REVIEW_MARKER)
        self.assertEqual(draft["review_kind"], DREAM_REVIEW_MARKER)
        edited = store.edit(draft["id"], title="t2", body="b2", role="editor")
        self.assertEqual(edited["review_kind"], DREAM_REVIEW_MARKER)
        moved = store.transition(draft["id"], "submit", "editor")
        self.assertEqual(moved["review_kind"], DREAM_REVIEW_MARKER)
        moved = store.transition(draft["id"], "approve", "reviewer")
        self.assertEqual(moved["review_kind"], DREAM_REVIEW_MARKER)
        rolled = store.rollback(draft["id"], 1, "publisher")
        self.assertEqual(rolled["status"], "draft")
        self.assertEqual(rolled["review_kind"], DREAM_REVIEW_MARKER)
        self.assertEqual(store.get(draft["id"])["review_kind"], DREAM_REVIEW_MARKER)

    def test_sqlite_store_marker_persists_across_reopen_and_operations(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "admin.db")
            store = SqliteDraftStore(path)
            draft = store.create("t", "b", "editor", review_kind=DREAM_REVIEW_MARKER)
            store.edit(draft["id"], body="b2", role="editor")
            store.transition(draft["id"], "submit", "editor")
            store.transition(draft["id"], "approve", "reviewer")
            store.rollback(draft["id"], 1, "publisher")
            reopened = SqliteDraftStore(path)
            record = reopened.get(draft["id"])
            self.assertEqual(record["review_kind"], DREAM_REVIEW_MARKER)
            self.assertEqual(record["status"], "draft")
            plain = reopened.create("p", "b", "editor")
            self.assertIsNone(plain["review_kind"])

    def test_old_database_without_review_kind_column_is_migrated(self):
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
            # A pre-marker draft is an ordinary draft (marker None).
            self.assertIsNone(record["review_kind"])
            draft = store.create("t", "b", "editor", review_kind=DREAM_REVIEW_MARKER)
            self.assertEqual(
                SqliteDraftStore(path).get(draft["id"])["review_kind"],
                DREAM_REVIEW_MARKER,
            )


if __name__ == "__main__":
    unittest.main()
