"""Negative tests for the Liuren limitations compat gate in explanation_eval.

Runs in the assembled private backend (offline acceptance backend partition),
like the other Phase 4 tests: it needs the reviewed production runtime and
the real Liuren engine. Not wired into public CI.

Each negative test drives the REAL comparison path: execute_case() with the
engine output mutated after genuine execution. The gate itself lives in
tianji_kb.explanation_eval._frozen_oracle_result, never in this file.
"""
import copy
import unittest
from unittest.mock import patch

import tianji_kb.explanation_eval as ev
from tianji_kb.engine import execute
from tianji_kb.explanation_eval import (
    LIUREN_AUDITED_LIMITATIONS,
    execute_case,
    load_suite,
)


class LiurenLimitationsCompatTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        suite = load_suite()
        cls.case = next(
            c for c in suite["cases"]
            if c["id"] == "liuren.zeike" and c["expected"] == "explanation"
        )
        cls.raw = execute("liuren", copy.deepcopy(cls.case["input"]), cls.case["variant"])

    def run_case_with(self, mutate):
        raw = copy.deepcopy(self.raw)
        mutate(raw["result"])
        with patch.object(ev, "execute", return_value=raw):
            return execute_case(self.case)

    def test_unmutated_liuren_case_passes_oracle(self):
        # Positive control: the genuine engine output passes, and the engine
        # emits exactly the audited boundary statement pinned in
        # explanation_eval (B012 PR #320, reviewed and merged).
        self.assertEqual(self.raw["result"]["limitations"], LIUREN_AUDITED_LIMITATIONS)
        execute_case(self.case)

    def test_tampered_limitations_text_fails(self):
        with self.assertRaisesRegex(RuntimeError, "Reviewed Liuren boundary display"):
            self.run_case_with(lambda r: r.update(limitations=["篡改文本"]))

    def test_extended_limitations_list_fails(self):
        def mutate(result):
            result["limitations"] = list(LIUREN_AUDITED_LIMITATIONS) + ["额外声明"]
        with self.assertRaisesRegex(RuntimeError, "Reviewed Liuren boundary display"):
            self.run_case_with(mutate)

    def test_deleted_limitations_field_fails(self):
        def mutate(result):
            del result["limitations"]
        with self.assertRaisesRegex(RuntimeError, "Reviewed Liuren boundary display"):
            self.run_case_with(mutate)

    def test_changed_month_general_triggers_oracle_drift(self):
        def mutate(result):
            result["month_general"] = dict(result["month_general"], branch="子")
        with self.assertRaisesRegex(RuntimeError, "Engine oracle drift"):
            self.run_case_with(mutate)

    def test_changed_transmissions_triggers_oracle_drift(self):
        def mutate(result):
            transmissions = list(result["transmissions"])
            transmissions[0] = "子" if transmissions[0] != "子" else "丑"
            result["transmissions"] = transmissions
        with self.assertRaisesRegex(RuntimeError, "Engine oracle drift"):
            self.run_case_with(mutate)


if __name__ == "__main__":
    unittest.main()
