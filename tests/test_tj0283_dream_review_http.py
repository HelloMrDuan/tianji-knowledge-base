"""TJ-028.3: dream review workflow HTTP verification.

Offline acceptance ONLY: requires the FastAPI stack. NOT wired into
public CI (validate.yml) and must never be claimed as a public CI run.
Run locally, e.g.:

    PYTHONPATH=src python -m pytest tests/test_tj0283_dream_review_http.py -q

Covers: review-draft creation gates (only an explained result with
valid claims/evidence enters review), the role matrix (401/403),
approve/reject reason recording, the approve/publish content gate
(corrupted evidence can never be approved or published, but can be
rejected), restart persistence through the shared SQLite file, and
the audit log (reasons recorded, no draft content leaked).
"""

import copy
import os
import tempfile
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from tianji_kb.api import create_app
from tianji_kb.rag_context import RetrievalUnavailable

ROLE_TOKENS = {
    "user-token": "user",
    "editor-token": "editor",
    "reviewer-token": "reviewer",
    "publisher-token": "publisher",
}
READ_TOKEN = "test-admin-token"

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


def _retrieval_fixture():
    """The server-side audited retrieval for _explained_result().

    The trusted evidence record is identical to the submitted one,
    and the matched interpretation matches the submitted element.
    The review-drafts endpoint and the approve/publish gate re-run
    this retrieval server-side; tests patch
    ``tianji_kb.api.retrieve_dream_culture`` with it (the audited
    index is sealed data, unavailable in this environment).
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


def _client(db_path=None):
    if db_path is None:
        fd, db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
    return TestClient(
        create_app(
            admin_role_tokens=dict(ROLE_TOKENS),
            admin_read_token=READ_TOKEN,
            admin_read_scopes={"system"},
            admin_db_path=db_path,
        )
    )


def _auth(token):
    return {} if token is None else {"Authorization": f"Bearer {token}"}


class ReviewDraftHttpTests(unittest.TestCase):
    def setUp(self):
        self.client = _client()
        self._retrieve_patcher = patch(
            "tianji_kb.api.retrieve_dream_culture",
            return_value=_retrieval_fixture(),
        )
        self._retrieve_patcher.start()
        self.addCleanup(self._retrieve_patcher.stop)

    def _create(self, token="editor-token", result=None):
        return self.client.post(
            "/api/v1/admin/research/dream/review-drafts",
            json=result if result is not None else _explained_result(),
            headers=_auth(token),
        )

    def test_create_review_draft_from_explained_result(self):
        response = self._create()
        self.assertEqual(response.status_code, 200, response.text)
        draft = response.json()["draft"]
        self.assertEqual(draft["status"], "draft")
        self.assertEqual(draft["review_kind"], "dream_ai")
        self.assertIn("AI 解梦研究草稿", draft["title"])
        self.assertIn("dream_ai_review", draft["body"])
        self.assertEqual(draft["versions"][0]["action"], "create")

    def test_create_requires_a_role_token(self):
        self.assertEqual(self._create(token=None).status_code, 401)
        self.assertEqual(self._create(token="user-token").status_code, 403)
        self.assertEqual(self._create(token="bogus-token").status_code, 401)

    def test_refusal_cannot_enter_review(self):
        result = _explained_result()
        result["verdict"] = "abstained_no_reviewed_interpretation"
        result["claims"] = []
        result["evidence"] = {}
        response = self._create(result=result)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["detail"]["code"], "refusal_not_reviewable")

    def test_forged_evidence_cannot_enter_review(self):
        result = _explained_result()
        result["claims"][0]["evidence_ids"] = ["deadbeef" * 3]
        response = self._create(result=result)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["detail"]["code"], "invalid_citation")

    def test_create_rejects_fully_forged_but_self_consistent_evidence(self):
        # A payload that is internally consistent (the forged quote
        # is verbatim against the forged record, the forged element
        # cites the forged id) but matches nothing in the audited
        # retrieval: it passed the old self-consistency check and
        # must now fail against the trusted retrieval.
        fake_id = "f" * 24
        fake_text = "伪造原文见人死皆吉"
        result = _explained_result()
        result["elements"][0]["evidence_ids"] = [fake_id]
        result["claims"][0]["text"] = f"《周公解梦》载“{fake_text}”，此条仅言传统说法。"
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
        response = self._create(result=result)
        self.assertEqual(response.status_code, 422, response.text)
        self.assertEqual(response.json()["detail"]["code"], "untrusted_evidence")

    def test_create_refuses_without_trusted_retrieval(self):
        # No audited retrieval runtime: refuse, never downgrade to
        # client self-attestation.
        with patch(
            "tianji_kb.api.retrieve_dream_culture",
            side_effect=RetrievalUnavailable("unavailable"),
        ):
            response = self._create()
        self.assertEqual(response.status_code, 503, response.text)
        self.assertEqual(
            response.json()["detail"]["code"], "reviewed_retrieval_unavailable"
        )

    def test_approve_refuses_without_trusted_retrieval(self):
        draft_id = self._create().json()["draft"]["id"]
        self.client.post(
            f"/api/v1/admin/drafts/{draft_id}/submit", headers=_auth("editor-token")
        )
        with patch(
            "tianji_kb.api.retrieve_dream_culture",
            side_effect=RetrievalUnavailable("unavailable"),
        ):
            blocked = self.client.post(
                f"/api/v1/admin/drafts/{draft_id}/approve",
                json={"reason": "试图通过。"},
                headers=_auth("reviewer-token"),
            )
        self.assertEqual(blocked.status_code, 503, blocked.text)
        self.assertEqual(
            blocked.json()["detail"]["code"], "reviewed_retrieval_unavailable"
        )

    def test_create_sets_immutable_marker(self):
        draft = self._create().json()["draft"]
        self.assertEqual(draft["review_kind"], "dream_ai")
        # PATCH can change the body but never the marker.
        edited = self.client.patch(
            f"/api/v1/admin/drafts/{draft['id']}",
            json={"title": "AI 解梦研究草稿：改标题"},
            headers=_auth("editor-token"),
        )
        self.assertEqual(edited.status_code, 200, edited.text)
        self.assertEqual(edited.json()["draft"]["review_kind"], "dream_ai")

    def test_ai_draft_kind_tampering_cannot_use_ordinary_path(self):
        import json

        def _tampered_draft(mutate):
            draft_id = self._create().json()["draft"]["id"]
            draft = self.client.get(
                f"/api/v1/admin/drafts/{draft_id}", headers=_auth("editor-token")
            ).json()["draft"]
            body = mutate(draft["body"])
            edited = self.client.patch(
                f"/api/v1/admin/drafts/{draft_id}",
                json={"body": body},
                headers=_auth("editor-token"),
            )
            self.assertEqual(edited.status_code, 200, edited.text)
            self.client.post(
                f"/api/v1/admin/drafts/{draft_id}/submit",
                headers=_auth("editor-token"),
            )
            return draft_id

        def _remove_kind(body):
            parsed = json.loads(body)
            del parsed["kind"]
            return json.dumps(parsed, ensure_ascii=False)

        def _plain_text(body):
            return "plain text, not a dream draft"

        def _other_kind(body):
            parsed = json.loads(body)
            parsed["kind"] = "other_kind"
            return json.dumps(parsed, ensure_ascii=False)

        for mutate in (_remove_kind, _plain_text, _other_kind):
            draft_id = _tampered_draft(mutate)
            blocked = self.client.post(
                f"/api/v1/admin/drafts/{draft_id}/approve",
                json={"reason": "试图通过普通路径批准。"},
                headers=_auth("reviewer-token"),
            )
            self.assertEqual(blocked.status_code, 422, blocked.text)
            self.assertEqual(
                blocked.json()["detail"]["code"], "invalid_dream_review_content"
            )
            publish_blocked = self.client.post(
                f"/api/v1/admin/drafts/{draft_id}/publish",
                headers=_auth("publisher-token"),
            )
            self.assertEqual(publish_blocked.status_code, 422, publish_blocked.text)
            self.assertEqual(
                publish_blocked.json()["detail"]["code"],
                "invalid_dream_review_content",
            )

    def test_rollback_preserves_marker_and_restores_review(self):
        import json

        draft_id = self._create().json()["draft"]["id"]
        draft = self.client.get(
            f"/api/v1/admin/drafts/{draft_id}", headers=_auth("editor-token")
        ).json()["draft"]
        parsed = json.loads(draft["body"])
        del parsed["kind"]
        self.client.patch(
            f"/api/v1/admin/drafts/{draft_id}",
            json={"body": json.dumps(parsed, ensure_ascii=False)},
            headers=_auth("editor-token"),
        )
        rolled_back = self.client.post(
            f"/api/v1/admin/drafts/{draft_id}/rollback",
            json={"version": 1},
            headers=_auth("publisher-token"),
        )
        self.assertEqual(rolled_back.status_code, 200, rolled_back.text)
        restored = rolled_back.json()["draft"]
        self.assertEqual(restored["status"], "draft")
        self.assertEqual(restored["review_kind"], "dream_ai")
        self.assertIn("dream_ai_review", restored["body"])
        self.client.post(
            f"/api/v1/admin/drafts/{draft_id}/submit", headers=_auth("editor-token")
        )
        approved = self.client.post(
            f"/api/v1/admin/drafts/{draft_id}/approve",
            json={"reason": "回滚后重新审核，通过。"},
            headers=_auth("reviewer-token"),
        )
        self.assertEqual(approved.status_code, 200, approved.text)
        self.assertEqual(approved.json()["draft"]["status"], "approved")

    def test_full_review_flow_approve_then_publish(self):
        draft_id = self._create().json()["draft"]["id"]
        self.assertEqual(
            self.client.post(
                f"/api/v1/admin/drafts/{draft_id}/submit", headers=_auth("editor-token")
            ).status_code,
            200,
        )
        # Approve without a reason is rejected for dream drafts.
        no_reason = self.client.post(
            f"/api/v1/admin/drafts/{draft_id}/approve", headers=_auth("reviewer-token")
        )
        self.assertEqual(no_reason.status_code, 422)
        self.assertEqual(no_reason.json()["detail"]["code"], "missing_review_reason")
        # An editor may not approve at all.
        self.assertEqual(
            self.client.post(
                f"/api/v1/admin/drafts/{draft_id}/approve",
                json={"reason": "通过。"},
                headers=_auth("editor-token"),
            ).status_code,
            403,
        )
        approved = self.client.post(
            f"/api/v1/admin/drafts/{draft_id}/approve",
            json={"reason": "证据链完整，通过。"},
            headers=_auth("reviewer-token"),
        )
        self.assertEqual(approved.status_code, 200, approved.text)
        draft = approved.json()["draft"]
        self.assertEqual(draft["status"], "approved")
        self.assertEqual(
            draft["transitions"][-1]["reason"], "证据链完整，通过。"
        )
        self.assertEqual(draft["transitions"][-1]["role"], "reviewer")
        self.assertEqual(len(draft["versions"]), 3)
        # Publish is publisher-only.
        self.assertEqual(
            self.client.post(
                f"/api/v1/admin/drafts/{draft_id}/publish",
                headers=_auth("reviewer-token"),
            ).status_code,
            403,
        )
        published = self.client.post(
            f"/api/v1/admin/drafts/{draft_id}/publish",
            json={"reason": "发布已审研究草稿。"},
            headers=_auth("publisher-token"),
        )
        self.assertEqual(published.status_code, 200, published.text)
        self.assertEqual(published.json()["draft"]["status"], "published")

    def test_corrupted_body_cannot_be_approved_but_can_be_rejected(self):
        import json

        draft_id = self._create().json()["draft"]["id"]
        # Roll back is not needed yet: edit in 'draft' status, then
        # corrupt the claim's quote (evidence keeps the real text).
        draft = self.client.get(
            f"/api/v1/admin/drafts/{draft_id}", headers=_auth("editor-token")
        ).json()["draft"]
        parsed = json.loads(draft["body"])
        parsed["result"]["claims"][0]["quotes"][0]["text"] = "见人死自死皆大吉大利"
        edited = self.client.patch(
            f"/api/v1/admin/drafts/{draft_id}",
            json={"body": json.dumps(parsed, ensure_ascii=False)},
            headers=_auth("editor-token"),
        )
        self.assertEqual(edited.status_code, 200, edited.text)
        self.client.post(
            f"/api/v1/admin/drafts/{draft_id}/submit", headers=_auth("editor-token")
        )
        blocked = self.client.post(
            f"/api/v1/admin/drafts/{draft_id}/approve",
            json={"reason": "试图通过。"},
            headers=_auth("reviewer-token"),
        )
        self.assertEqual(blocked.status_code, 422)
        self.assertEqual(
            blocked.json()["detail"]["code"], "invalid_dream_review_content"
        )
        rejected = self.client.post(
            f"/api/v1/admin/drafts/{draft_id}/reject",
            json={"reason": "引文与已审原文不符，拒绝。"},
            headers=_auth("reviewer-token"),
        )
        self.assertEqual(rejected.status_code, 200, rejected.text)
        self.assertEqual(rejected.json()["draft"]["status"], "rejected")

    def test_edit_after_approval_requires_rollback_and_re_review(self):
        draft_id = self._create().json()["draft"]["id"]
        self.client.post(
            f"/api/v1/admin/drafts/{draft_id}/submit", headers=_auth("editor-token")
        )
        self.client.post(
            f"/api/v1/admin/drafts/{draft_id}/approve",
            json={"reason": "证据链完整，通过。"},
            headers=_auth("reviewer-token"),
        )
        edit = self.client.patch(
            f"/api/v1/admin/drafts/{draft_id}",
            json={"title": "篡改标题"},
            headers=_auth("editor-token"),
        )
        self.assertEqual(edit.status_code, 422)
        rolled_back = self.client.post(
            f"/api/v1/admin/drafts/{draft_id}/rollback",
            json={"version": 1},
            headers=_auth("publisher-token"),
        )
        self.assertEqual(rolled_back.status_code, 200, rolled_back.text)
        self.assertEqual(rolled_back.json()["draft"]["status"], "draft")
        edited = self.client.patch(
            f"/api/v1/admin/drafts/{draft_id}",
            json={"title": "AI 解梦研究草稿：修改后"},
            headers=_auth("editor-token"),
        )
        self.assertEqual(edited.status_code, 200, edited.text)
        # The edited draft must pass review again before publishing.
        publish = self.client.post(
            f"/api/v1/admin/drafts/{draft_id}/publish",
            headers=_auth("publisher-token"),
        )
        self.assertEqual(publish.status_code, 422)

    def test_drafts_and_reviews_survive_restart(self):
        fd, db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        first = _client(db_path=db_path)
        draft_id = first.post(
            "/api/v1/admin/research/dream/review-drafts",
            json=_explained_result(),
            headers=_auth("editor-token"),
        ).json()["draft"]["id"]
        first.post(
            f"/api/v1/admin/drafts/{draft_id}/submit", headers=_auth("editor-token")
        )
        first.post(
            f"/api/v1/admin/drafts/{draft_id}/approve",
            json={"reason": "证据链完整，通过。"},
            headers=_auth("reviewer-token"),
        )
        second = _client(db_path=db_path)
        record = second.get(
            f"/api/v1/admin/drafts/{draft_id}", headers=_auth("reviewer-token")
        ).json()["draft"]
        self.assertEqual(record["status"], "approved")
        self.assertEqual(record["review_kind"], "dream_ai")
        self.assertEqual(record["transitions"][-1]["reason"], "证据链完整，通过。")
        self.assertEqual(len(record["versions"]), 3)

    def test_plain_draft_needs_no_reason(self):
        created = self.client.post(
            "/api/v1/admin/drafts",
            json={"title": "Plain", "body": "plain body"},
            headers=_auth("editor-token"),
        )
        draft_id = created.json()["draft"]["id"]
        self.assertIsNone(created.json()["draft"]["review_kind"])
        self.client.post(
            f"/api/v1/admin/drafts/{draft_id}/submit", headers=_auth("editor-token")
        )
        approved = self.client.post(
            f"/api/v1/admin/drafts/{draft_id}/approve",
            headers=_auth("reviewer-token"),
        )
        self.assertEqual(approved.status_code, 200, approved.text)

    def test_audit_log_records_reasons_without_draft_content(self):
        draft_id = self._create().json()["draft"]["id"]
        self.client.post(
            f"/api/v1/admin/drafts/{draft_id}/submit", headers=_auth("editor-token")
        )
        self.client.post(
            f"/api/v1/admin/drafts/{draft_id}/approve",
            json={"reason": "证据链完整，通过。"},
            headers=_auth("reviewer-token"),
        )
        entries = self.client.get(
            "/api/v1/admin/system/audit", headers=_auth(READ_TOKEN)
        ).json()["entries"]
        approve_entries = [
            e for e in entries if e["what"] == f"draft:approve:{draft_id}"
        ]
        self.assertEqual(len(approve_entries), 1)
        self.assertEqual(approve_entries[0]["detail"], "证据链完整，通过。")
        self.assertEqual(approve_entries[0]["who"], "reviewer")
        blob = str(entries)
        self.assertNotIn("我梦见自己死了", blob)
        self.assertNotIn(QUOTE, blob)


if __name__ == "__main__":
    unittest.main()
