"""B026 verification: WBS mapping for TJ-022.1 / TJ-023.1 / TJ-024.2.

These are acceptance tests for already-shipped engine behavior, not new
features (B008 precedent: when the capability is present, the test itself
is the deliverable). Every assertion below maps to one WBS acceptance
clause; nothing here invents a verdict, score, or prediction.

OFFLINE ACCEPTANCE ONLY, NOT PUBLIC CI. The engine needs reviewed
canonical data (data/canonical/bazi/*.json) plus the production runtime,
neither of which exists in a bare public checkout: validate.yml installs
only jsonschema, and bare-checkout runs fail with RuntimeUnavailable.
Public CI must not claim these tests; it runs the gate, compileall, and
the pure-stdlib suites only.
"""
import unittest

from tianji_kb import scenario_engine
from tianji_kb.bazi_core import (
    reviewed_branch_pair_relations,
    reviewed_relations,
    taohua_matches,
)

BIRTH_A = "2000-01-07T12:00:00+08:00"
BIRTH_B = "1995-06-15T08:30:00+08:00"
PILLARS = ("year", "month", "day", "hour")


def _romance(year):
    return scenario_engine.execute_scenario(
        "romance", {"birth_value": BIRTH_A, "target_year": year})


def _career(year):
    return scenario_engine.execute_scenario(
        "career", {"birth_value": BIRTH_A, "target_year": year})


def _compatibility():
    return scenario_engine.execute_scenario("compatibility", {
        "person_a_birth_value": BIRTH_A,
        "person_b_birth_value": BIRTH_B,
    })


class TaohuaTwoBasesTests(unittest.TestCase):
    """TJ-022.1: year/day Xianchi bases have separate Rule/Evidence and
    must never be summed into a Taohua probability."""

    def test_taohua_targets_computed_per_basis_and_never_summed(self):
        result = taohua_matches("卯", "子", ["卯", "丑", "子", "午"])
        self.assertEqual(result["targets"],
                         {"year_branch": "子", "day_branch": "酉"})
        self.assertNotEqual(result["targets"]["year_branch"],
                            result["targets"]["day_branch"])
        self.assertEqual(result["matches"], [{
            "basis": "year_branch", "target_branch": "子", "pillar": "day",
        }])
        self.assertTrue(result["warning"])
        self.assertEqual(set(result), {"targets", "matches", "warning"})
        self.assertNotIn("probability", str(result))
        self.assertNotIn("概率", str(result))

    def test_two_bases_activate_independently_across_years(self):
        cases = {
            2020: (True, False),   # flow 子 hits the year-basis target only
            2029: (False, True),   # flow 酉 hits the day-basis target only
            2026: (False, False),  # flow 午 hits neither target
        }
        for year, (year_expected, day_expected) in cases.items():
            result = _romance(year)
            activation = result["result"]["target_year_activation"]
            self.assertEqual(set(activation),
                             {"year_branch_basis", "day_branch_basis"})
            self.assertEqual(activation["year_branch_basis"]["matched"],
                             year_expected)
            self.assertEqual(activation["day_branch_basis"]["matched"],
                             day_expected)
            self.assertEqual(activation["year_branch_basis"]["target_branch"],
                             "子")
            self.assertEqual(activation["day_branch_basis"]["target_branch"],
                             "酉")
            self.assertEqual(result["result"]["xianchi"]["basis_policy"],
                             "year_and_day_reported_separately")
            self.assertNotIn("概率", str(result["result"]))
            self.assertNotIn("probability", str(result["result"]))

    def test_natal_matches_carry_basis_and_never_merge(self):
        result = _romance(2026)
        xianchi = result["result"]["xianchi"]
        self.assertEqual(xianchi["targets"],
                         {"year_branch": "子", "day_branch": "酉"})
        self.assertEqual(xianchi["natal_matches"], [{
            "basis": "year_branch", "target_branch": "子", "pillar": "day",
        }])
        for match in xianchi["natal_matches"]:
            self.assertIn(match["basis"], ("year_branch", "day_branch"))
        self.assertTrue(xianchi["source_warning"])


class CareerAggregationTests(unittest.TestCase):
    """TJ-023.1: counts and real Ten-God positions retained; without
    strength/weakness adjudication no promotion or wealth-loss writing."""

    def test_counts_and_positions_retained_exactly(self):
        result = _career(2026)["result"]
        groups = result["structure_groups"]
        self.assertEqual(set(groups),
                         {"wealth", "authority", "output", "resource",
                          "peers"})
        for group_id, group in groups.items():
            occurrences = group["occurrences"]
            self.assertEqual(group["visible_count"] + group["hidden_count"],
                             len(occurrences))
            visible = [o for o in occurrences if o["layer"] == "visible_stem"]
            hidden = [o for o in occurrences if o["layer"] == "hidden_stem"]
            self.assertEqual(len(visible), group["visible_count"])
            self.assertEqual(len(hidden), group["hidden_count"])
            for occurrence in occurrences:
                self.assertIn(occurrence["pillar"], PILLARS)
                self.assertIn(occurrence["layer"],
                              ("visible_stem", "hidden_stem"))
                self.assertTrue(occurrence["stem"])
                self.assertIn(occurrence["ten_god"], group["ten_gods"])
            card = next(c for c in result["interpretation_cards"]
                        if c["group_id"] == group_id)
            self.assertEqual(card["visible_count"], group["visible_count"])
            self.assertEqual(card["hidden_count"], group["hidden_count"])
            self.assertEqual(card["ten_gods"], group["ten_gods"])

    def test_no_promotion_or_wealth_loss_writing(self):
        output = _career(2026)
        result = output["result"]
        serialized = str(result)
        self.assertNotIn("升职", serialized)
        self.assertNotIn("破财", serialized)
        boundary = result["annual_reading"]["boundary"]
        self.assertIn("尚未判定月令旺衰", boundary)
        self.assertIn("不得用它预测升迁", boundary)
        for card in result["interpretation_cards"]:
            self.assertFalse(card["personal_prediction"])
        self.assertFalse(result["annual_reading"]["personal_prediction"])
        self.assertEqual(
            sum(c["target_year_stem_matches_group"]
                for c in result["interpretation_cards"]), 1)


class SpousePalaceFourByFourTests(unittest.TestCase):
    """TJ-024.2: spouse palace, four-pillar 4x4 layering, and conflict
    limits; relation counts never become an adaptation score."""

    def test_spouse_palace_is_day_branch_structural_position(self):
        relations = reviewed_relations(["甲", "乙", "丙", "丁"],
                                       ["卯", "丑", "子", "午"])
        palace = relations["spouse_palace"]
        self.assertEqual(palace["pillar"], "day")
        self.assertEqual(palace["day_branch"], "子")
        result = _romance(2026)["result"]
        year_palace = result["spouse_palace_year_relations"]
        self.assertEqual(year_palace["pairs_checked"], 1)
        self.assertEqual(year_palace["natal_day_branch"], "子")
        for relation in year_palace["relations"]:
            self.assertIn(relation["relation_type"],
                          ("six_harmony", "harm", "clash"))
            self.assertEqual(relation["natal_pillar"], "day")
        self.assertFalse(year_palace["interpretation_allowed"])

    def test_pair_relations_cover_only_reviewed_kinds(self):
        self.assertEqual([r["kind"] for r in reviewed_branch_pair_relations("子", "丑")],
                         ["six_harmony"])
        self.assertEqual([r["kind"] for r in reviewed_branch_pair_relations("子", "午")],
                         ["clash"])
        self.assertEqual([r["kind"] for r in reviewed_branch_pair_relations("子", "未")],
                         ["harm"])
        self.assertEqual(reviewed_branch_pair_relations("子", "申"), [])
        self.assertEqual(reviewed_branch_pair_relations("子", "酉"), [])

    def test_triple_harmony_is_group_level_not_pair_level(self):
        relations = reviewed_relations(["甲", "乙", "丙", "丁"],
                                       ["申", "子", "辰", "午"])
        triples = relations["branch_triple_harmonies"]
        self.assertEqual(len(triples), 1)
        self.assertEqual(set(triples[0]["branches"]), {"申", "子", "辰"})
        self.assertEqual(len(triples[0]["branches"]), 3)
        self.assertEqual(len(triples[0]["pillars"]), 3)
        self.assertTrue(triples[0]["traditional_result_element"])
        for pair_list in (relations["branch_six_harmonies"],
                          relations["branch_six_harms"],
                          relations["branch_six_clashes"]):
            for row in pair_list:
                self.assertEqual(len(row["branches"]), 2)
                self.assertEqual(len(row["pillars"]), 2)

    def test_cross_matrix_4x4_tier_discipline(self):
        result = _compatibility()["result"]
        matrix = result["cross_relation_matrix"]
        hits = matrix["hits"]
        self.assertFalse(matrix["interpretation_allowed"])
        self.assertEqual(set(matrix["tier_policy"]),
                         {"core", "day_context", "supplemental"})
        for hit in hits:
            self.assertIn(hit["person_a_pillar"], PILLARS)
            self.assertIn(hit["person_b_pillar"], PILLARS)
            both_day = (hit["person_a_pillar"] == "day"
                        and hit["person_b_pillar"] == "day")
            one_day = ("day" in (hit["person_a_pillar"],
                                 hit["person_b_pillar"]))
            expected = ("core" if both_day else
                        "day_context" if one_day else "supplemental")
            self.assertEqual(hit["tier"], expected)
        core_hits = [h for h in hits if h["tier"] == "core"]
        self.assertIn({
            "tier": "core", "relation_type": "six_harmony",
            "rule_id": "bazi.phase2.branch_six_harmonies",
            "person_a_pillar": "day", "person_b_pillar": "day",
            "branches": ["子", "丑"], "traditional_result_element": "土",
        }, core_hits)
        summary = matrix["summary"]
        self.assertEqual(summary["core"] + summary["day_context"]
                         + summary["supplemental"], len(hits))
        for kind in ("stem_five_combination", "six_harmony", "harm",
                     "clash"):
            key = ("stem_five_combination" if kind == "stem_five_combination"
                   else kind)
            self.assertEqual(summary[key],
                             sum(1 for h in hits
                                 if h["relation_type"] == kind))

    def test_no_adaptation_score_anywhere(self):
        result = _compatibility()["result"]
        serialized = str(result)
        for token in ("适配分", "score", "percent", "compatibility_score"):
            self.assertNotIn(token, serialized)
        matrix = result["cross_relation_matrix"]
        self.assertEqual(set(matrix["summary"]), {
            "core", "day_context", "supplemental",
            "stem_five_combination", "six_harmony", "harm", "clash"})
        self.assertFalse(matrix["interpretation_allowed"])
        for item in result["relation_evidence_matrix"]:
            self.assertFalse(item["interpretation_allowed"])


if __name__ == "__main__":
    unittest.main()
