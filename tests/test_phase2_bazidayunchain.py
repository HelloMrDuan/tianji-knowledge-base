"""TJ-014.2: Dayun fact-tracking chain - month pillar -> trace -> direction
source -> 60-cycle sequence -> ten gods -> research evidence boundary.

The chain verifies an existing candidate-sequence artefact against its
declared sources. Every tamper below must genuinely raise; none of these
tests assert mere key existence or swallow errors.
"""
import copy
import unittest
from unittest.mock import patch

from tianji_kb.bazi_dayun_chain import build_dayun_candidate_chain
from tianji_kb.bazi_dayun_direction import traditional_direction
from tianji_kb.bazi_dayun_sequence import candidate_sequence
from tianji_kb.engine import execute
from tianji_kb.operations.bazi_chart import chart

NATAL = ("庚辰", "己丑", "甲子", "庚午")


def fixed_chart(**kwargs):
    return chart(*NATAL, **kwargs)


class ChainPositiveTests(unittest.TestCase):
    def test_forward_chain_resolves_real_trace(self):
        out = fixed_chart(dayun_sequence_direction="forward", dayun_sequence_count=3)
        research = out["result"]["dayun_sequence_research"]
        chain = build_dayun_candidate_chain(
            out, research, direction="forward", periods=3)
        v = chain["chain_verification"]
        self.assertEqual(v["month_pillar"], "己丑")
        self.assertEqual(v["month_pillar_rule_id"], "bazi.phase2.pillars")
        self.assertEqual(v["month_pillar_trace_index"], 0)
        self.assertTrue(v["month_pillar_evidence_verified"])
        self.assertEqual(v["year_ganzhi"], "庚辰")
        self.assertEqual(v["day_stem"], "甲")
        self.assertEqual(v["direction"], "forward")
        self.assertEqual(v["direction_source"], "explicit_caller_selection_only")
        self.assertFalse(v["direction_candidate_validated"])
        self.assertFalse(v["direction_method_classical_approval"])
        self.assertTrue(v["research_only"])
        self.assertFalse(v["public_enabled"])
        self.assertFalse(v["ai_enabled"])
        self.assertEqual(
            [(r["period_index"], r["candidate_ganzhi"], r["ten_god"])
             for r in chain["row_lineage"]],
            [(1, "庚寅", "七杀"), (2, "辛卯", "正官"), (3, "壬辰", "偏印")])
        for row in chain["row_lineage"]:
            self.assertEqual(row["month_pillar_trace_index"], 0)

    def test_backward_chain_with_fixed_expectations(self):
        out = fixed_chart(dayun_sequence_direction="backward", dayun_sequence_count=3)
        research = out["result"]["dayun_sequence_research"]
        chain = build_dayun_candidate_chain(
            out, research, direction="backward", periods=3)
        self.assertEqual(
            [(r["candidate_ganzhi"], r["ten_god"]) for r in chain["row_lineage"]],
            [("戊子", "偏财"), ("丁亥", "伤官"), ("丙戌", "食神")])
        self.assertEqual(chain["chain_verification"]["direction"], "backward")

    def test_chain_resolves_pillars_by_rule_id_not_fixed_index(self):
        out = fixed_chart(dayun_sequence_direction="forward", dayun_sequence_count=3)
        research = out["result"]["dayun_sequence_research"]
        # Move the pillars step away from index 0: chain must still find it.
        shuffled = copy.deepcopy(out)
        steps = shuffled["trace"]
        pillars = next(s for s in steps if s["rule_id"] == "bazi.phase2.pillars")
        steps.remove(pillars)
        steps.append(pillars)
        chain = build_dayun_candidate_chain(
            shuffled, research, direction="forward", periods=3)
        self.assertEqual(
            chain["chain_verification"]["month_pillar_trace_index"],
            len(shuffled["trace"]) - 1)
        self.assertEqual(chain["chain_verification"]["month_pillar"], "己丑")


class ChainTamperTests(unittest.TestCase):
    def setUp(self):
        self.out = fixed_chart(dayun_sequence_direction="forward", dayun_sequence_count=3)
        self.research = self.out["result"]["dayun_sequence_research"]

    def valid(self):
        return build_dayun_candidate_chain(
            copy.deepcopy(self.out), copy.deepcopy(self.research),
            direction="forward", periods=3)

    def test_valid_chain_passes(self):
        self.assertTrue(self.valid()["chain_verification"]["research_only"])

    def test_missing_pillars_step_rejected(self):
        out = copy.deepcopy(self.out)
        out["trace"] = [s for s in out["trace"] if s["rule_id"] != "bazi.phase2.pillars"]
        with self.assertRaises(ValueError):
            build_dayun_candidate_chain(out, self.research, direction="forward", periods=3)

    def test_trace_not_a_list_rejected(self):
        out = copy.deepcopy(self.out)
        out["trace"] = {"rule_id": "bazi.phase2.pillars"}
        with self.assertRaises(ValueError):
            build_dayun_candidate_chain(out, self.research, direction="forward", periods=3)

    def test_dangling_evidence_rejected(self):
        out = copy.deepcopy(self.out)
        out["evidence"] = {}
        with self.assertRaises(ValueError):
            build_dayun_candidate_chain(out, self.research, direction="forward", periods=3)

    def test_sequence_from_wrong_month_rejected(self):
        wrong = candidate_sequence("戊子", "甲", direction="forward", periods=3)
        with self.assertRaises(ValueError):
            build_dayun_candidate_chain(
                self.out, wrong, direction="forward", periods=3)

    def test_first_row_repeating_month_rejected(self):
        seq = copy.deepcopy(self.research)
        seq["rows"][0]["candidate_ganzhi"] = "己丑"
        with self.assertRaises(ValueError):
            build_dayun_candidate_chain(
                self.out, seq, direction="forward", periods=3)

    def test_cycle_drift_rejected(self):
        seq = copy.deepcopy(self.research)
        seq["rows"][1]["candidate_ganzhi"] = "壬辰"
        with self.assertRaises(ValueError):
            build_dayun_candidate_chain(
                self.out, seq, direction="forward", periods=3)

    def test_ten_god_contradicting_day_stem_rejected(self):
        seq = copy.deepcopy(self.research)
        seq["rows"][0]["ten_god_relative_to_natal_day_stem"] = "正官"
        with self.assertRaises(ValueError):
            build_dayun_candidate_chain(
                self.out, seq, direction="forward", periods=3)

    def test_direction_mismatch_rejected(self):
        with self.assertRaises(ValueError):
            build_dayun_candidate_chain(
                self.out, self.research, direction="backward", periods=3)

    def test_research_promotion_rejected(self):
        seq = copy.deepcopy(self.research)
        seq["public_enabled"] = True
        with self.assertRaises(ValueError):
            build_dayun_candidate_chain(
                self.out, seq, direction="forward", periods=3)

    def test_review_status_promotion_rejected(self):
        seq = copy.deepcopy(self.research)
        seq["dayun_sequence_policy_review_status"] = "reviewed"
        with self.assertRaises(ValueError):
            build_dayun_candidate_chain(
                self.out, seq, direction="forward", periods=3)

    def test_forged_direction_candidate_rejected(self):
        candidate = traditional_direction("庚辰", traditional_role="male")
        candidate["classical_direction_evidence_approved"] = True
        with self.assertRaises(ValueError):
            build_dayun_candidate_chain(
                self.out, self.research, direction="forward",
                traditional_role="male", direction_candidate=candidate, periods=3)

    def test_candidate_year_mismatch_rejected(self):
        candidate = traditional_direction("辛巳", traditional_role="female")
        with self.assertRaises(ValueError):
            build_dayun_candidate_chain(
                self.out, self.research, direction="forward",
                traditional_role="female", direction_candidate=candidate, periods=3)

    def test_no_direction_source_rejected(self):
        with self.assertRaises(ValueError):
            build_dayun_candidate_chain(
                self.out, self.research, direction=None, periods=3)


class EngineGateTests(unittest.TestCase):
    def test_mode_b_chain_verification_in_execute(self):
        out = execute("bazi", dict(zip(
            ("year_ganzhi", "month_ganzhi", "day_ganzhi", "hour_ganzhi"), NATAL),
            dayun_direction_policy="bazi-dayun-year-stem-traditional-role-research-v1",
            traditional_role="male",
            dayun_sequence_count=3),
            allow_research=True)
        research = out["result"]["dayun_sequence_research"]
        self.assertIn("chain_verification", research)
        v = research["chain_verification"]
        self.assertEqual(v["direction"], "forward")
        self.assertEqual(
            v["direction_source"], "opt_in_traditional_year_stem_role_candidate")
        self.assertTrue(v["direction_candidate_validated"])
        self.assertEqual(v["month_pillar"], "己丑")
        self.assertTrue(v["research_only"])
        self.assertIn("direction_research", research)
        self.assertTrue(research["direction_research"]["research_only"])

    def test_mode_a_chain_verification_explicit(self):
        out = execute("bazi", dict(zip(
            ("year_ganzhi", "month_ganzhi", "day_ganzhi", "hour_ganzhi"), NATAL),
            dayun_sequence_direction="forward",
            dayun_sequence_count=3),
            allow_research=True)
        research = out["result"]["dayun_sequence_research"]
        v = research["chain_verification"]
        self.assertEqual(v["direction_source"], "explicit_caller_selection_only")
        self.assertFalse(v["direction_candidate_validated"])
        self.assertNotIn("direction_research", research)

    def test_engine_rejects_forged_direction_candidate(self):
        forged = traditional_direction("庚辰", traditional_role="male")
        forged["classical_direction_evidence_approved"] = True
        with patch("tianji_kb.engine.traditional_direction", return_value=forged):
            with self.assertRaises(ValueError):
                execute("bazi", dict(zip(
                    ("year_ganzhi", "month_ganzhi", "day_ganzhi", "hour_ganzhi"), NATAL),
                    dayun_direction_policy="bazi-dayun-year-stem-traditional-role-research-v1",
                    traditional_role="male",
                    dayun_sequence_count=3),
                    allow_research=True)

    def test_mode_b_and_manual_direction_conflict(self):
        with self.assertRaises(ValueError):
            execute("bazi", dict(zip(
                ("year_ganzhi", "month_ganzhi", "day_ganzhi", "hour_ganzhi"), NATAL),
                dayun_direction_policy="bazi-dayun-year-stem-traditional-role-research-v1",
                traditional_role="male",
                dayun_sequence_direction="forward"),
                allow_research=True)


class CycleBoundaryTests(unittest.TestCase):
    def test_full_sixty_cycle_no_duplicates(self):
        # Five consecutive 12-period windows cover all 60 positions once.
        months = ["甲子", "丙子", "戊子", "庚子", "壬子"]
        seen = []
        for month in months:
            seq = candidate_sequence(month, "甲", direction="forward", periods=12)
            seen.extend(r["candidate_ganzhi"] for r in seq["rows"])
        self.assertEqual(len(seen), 60)
        self.assertEqual(len(set(seen)), 60)
        from tianji_kb.foundations import CYCLE
        self.assertEqual(set(seen), set(CYCLE))

    def test_wraparound_both_directions(self):
        fwd = candidate_sequence("癸亥", "甲", direction="forward", periods=2)
        self.assertEqual(
            [r["candidate_ganzhi"] for r in fwd["rows"]], ["甲子", "乙丑"])
        bwd = candidate_sequence("甲子", "甲", direction="backward", periods=2)
        self.assertEqual(
            [r["candidate_ganzhi"] for r in bwd["rows"]], ["癸亥", "壬戌"])

    def test_ten_gods_follow_day_master_not_other_stems(self):
        seq = candidate_sequence("己丑", "丙", direction="forward", periods=3)
        self.assertEqual(
            [r["ten_god_relative_to_natal_day_stem"] for r in seq["rows"]],
            ["偏财", "正财", "七杀"])


if __name__ == "__main__":
    unittest.main()
