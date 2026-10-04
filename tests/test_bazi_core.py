import unittest

from tianji_kb.bazi_core import (
    VARIANT,
    branch_relations,
    chart_from_datetime,
    chart_from_pillars,
    hidden_stems,
    taohua_matches,
    ten_god,
)


class BaziDeterministicCoreTests(unittest.TestCase):
    def test_ten_gods_for_jia_day_master(self):
        expected = {
            "甲": "比肩",
            "乙": "劫财",
            "丙": "食神",
            "丁": "伤官",
            "戊": "偏财",
            "己": "正财",
            "庚": "七杀",
            "辛": "正官",
            "壬": "偏印",
            "癸": "正印",
        }
        self.assertEqual({stem: ten_god("甲", stem) for stem in expected}, expected)

    def test_hidden_stems_are_structural_and_ten_god_bound(self):
        self.assertEqual(
            hidden_stems("辰", "甲"),
            [
                {"stem": "戊", "ten_god": "偏财"},
                {"stem": "乙", "ten_god": "劫财"},
                {"stem": "癸", "ten_god": "正印"},
            ],
        )

    def test_branch_relations_and_complete_groups(self):
        rel = branch_relations(["子", "丑", "午", "未"])
        kinds = {(item["kind"], frozenset(item["branches"])) for item in rel["pairs"]}
        self.assertIn(("clash", frozenset(("子", "午"))), kinds)
        self.assertIn(("six_harmony", frozenset(("子", "丑"))), kinds)
        self.assertIn(("harm", frozenset(("子", "未"))), kinds)

        group = branch_relations(["申", "子", "辰", "酉"])["groups"]
        self.assertIn(
            {"kind": "triple_harmony", "branches": ["申", "子", "辰"], "result_element": "水"},
            group,
        )

    def test_taohua_is_lookup_fact_not_judgement(self):
        output = taohua_matches("寅", "午", ["寅", "卯", "午", "戌"])
        self.assertEqual(output["targets"], {"year_branch": "卯", "day_branch": "卯"})
        self.assertEqual(
            output["matches"],
            [
                {"basis": "year_branch", "target_branch": "卯", "pillar": "month"},
                {"basis": "day_branch", "target_branch": "卯", "pillar": "month"},
            ],
        )
        self.assertIn("辅助", output["warning"])

    def test_pillar_chart_is_deterministic_and_stops_before_judgement(self):
        first = chart_from_pillars("庚辰", "己丑", "甲子", "庚午")
        second = chart_from_pillars("庚辰", "己丑", "甲子", "庚午")
        self.assertEqual(first, second)
        self.assertEqual(first["variant"], VARIANT)
        self.assertEqual(first["day_master"]["stem"], "甲")
        self.assertEqual([x["name"] for x in first["pillars"]], ["year", "month", "day", "hour"])
        self.assertTrue(first["limitations"])
        self.assertNotIn("strength", first)
        self.assertNotIn("useful_god", first)

    def test_datetime_adapter_uses_pinned_calendar_and_is_repeatable(self):
        value = "2000-01-07T12:00:00+08:00"
        first = chart_from_datetime(value)
        second = chart_from_datetime(value)
        self.assertEqual(first, second)
        self.assertEqual(first["calendar"]["calendar_provider"], "lunar-python==1.4.8")
        self.assertEqual(first["calendar"]["day_boundary"], "midnight")

    def test_invalid_inputs_and_variant_rejected(self):
        with self.assertRaises(ValueError):
            ten_god("A", "甲")
        with self.assertRaises(ValueError):
            branch_relations(["子"])
        with self.assertRaises(ValueError):
            chart_from_pillars("甲子", "甲子", "BAD", "甲子")
        with self.assertRaises(ValueError):
            chart_from_pillars("甲子", "甲子", "甲子", "甲子", variant="unknown")


if __name__ == "__main__":
    unittest.main()
