"""TJ-0426 Lane 5 (O-02): Qimen inference layer — variant gate + structural facts.

Local tests run WITHOUT data/: structural_summary() consumes a chart
dict, and the fixture below carries the same keys as
operations/qimen_chart.chart() output. Data-gated tests (skipUnless
the sealed qfdk tables + lunar_python exist) replay the 4 Golden
cases and the fixed bureau anchors against the real chart.
"""
import unittest
from pathlib import Path

from tianji_kb.operations.qimen_reading import (
    IMPLEMENTED_RULESET, QIMEN_GAPS, VARIANT, VARIANT_REGISTRY,
    structural_summary, validate_variant,
)

ROOT = Path(__file__).resolve().parents[1]
QFDK_FILE = ROOT / 'data/canonical/qimen/qfdk_maoshan_v1.json'
GOLDEN_FILE = ROOT / 'data/canonical/qimen/phase2_golden.json'
try:
    import lunar_python  # noqa: F401
    HAS_LUNAR = True
except ImportError:
    HAS_LUNAR = False
HAS_DATA = QFDK_FILE.exists() and GOLDEN_FILE.exists() and HAS_LUNAR

# Fixture chart dict with the same keys as qimen_chart.chart() output
# (values are a coherent plate excerpt, not a real computed chart).
FIXTURE_CHART = {
    'ruleset': 'qfdk-table-exact-term-v1',
    'solar_term': '冬至', 'dun': '阳', 'bureau': 1, 'yuan': '上元',
    'chief_star_origin': '1', 'chief_star_palace': '1',
    'chief_door_palace': '1',
    'star_positions': {'天蓬': '1', '天任': '8', '天冲': '3', '天辅': '4',
                       '天英': '9', '天禽': '2', '天芮': '2', '天柱': '7', '天心': '6'},
    'door_positions': {'休门': '1', '生门': '8', '伤门': '3', '杜门': '4',
                       '景门': '9', '死门': '2', '惊门': '7', '开门': '6'},
    'deity_positions': {'值符': '1', '腾蛇': '2', '太阴': '3', '六合': '4',
                        '白虎': '9', '玄武': '8', '九地': '7', '九天': '6'},
}


class QimenVariantGateTests(unittest.TestCase):
    def test_implemented_variant_passes(self):
        entry = validate_variant('qfdk-table-exact-term-v1')
        self.assertEqual(entry['status'], 'implemented')
        self.assertEqual(entry['plate'], '转盘')

    def test_unmerged_variants_are_refused_not_mixed(self):
        for variant in ('置闰', '超接', '飞盘', '超接置闰', 'unreviewed', ''):
            with self.assertRaises(ValueError, msg=variant):
                validate_variant(variant)
        for variant in ('置闰', '超接', '飞盘'):
            self.assertEqual(VARIANT_REGISTRY[variant]['status'], 'unmerged')

    def test_gaps_carry_evidence_levels(self):
        self.assertEqual(QIMEN_GAPS['inference_rules']['status'], 'gap')
        self.assertEqual(QIMEN_GAPS['variant_merge']['status'], 'gap')
        for entry in QIMEN_GAPS.values():
            self.assertEqual(entry['evidence_level'], 'D')


class QimenStructuralSummaryTests(unittest.TestCase):
    def test_fixture_summary_restates_positions_only(self):
        summary = structural_summary(dict(FIXTURE_CHART))
        self.assertEqual(summary['variant'], VARIANT)
        self.assertEqual(summary['ruleset'], IMPLEMENTED_RULESET)
        self.assertTrue(summary['research_only'])
        self.assertFalse(summary['public'])
        self.assertFalse(summary['ai'])
        self.assertIsNone(summary['verdict'])
        self.assertIsNone(summary['determination'])
        self.assertEqual(summary['bureau'],
                         {'solar_term': '冬至', 'dun': '阳', 'number': 1, 'yuan': '上元'})
        self.assertEqual(summary['chief_star'],
                         {'palace': '1', 'origin': '1', 'name': '天蓬'})
        self.assertEqual(summary['chief_door'], {'palace': '1'})
        self.assertEqual(summary['star_positions'], FIXTURE_CHART['star_positions'])
        self.assertEqual(summary['inference']['status'], 'structural_only')
        # No verdict field ever carries a judgment: the only 吉凶
        # mention is the explicit "no verdict" note itself.
        self.assertNotIn('judgment', summary)
        self.assertNotIn('断语结论', str(summary))

    def test_shared_qin_rui_palace_names_both_stars(self):
        fixture = dict(FIXTURE_CHART)
        fixture['chief_star_palace'] = '2'
        summary = structural_summary(fixture)
        self.assertEqual(summary['chief_star']['name'], '天禽/天芮')

    def test_variant_mixing_is_refused(self):
        fixture = dict(FIXTURE_CHART, ruleset='置闰')
        with self.assertRaises(ValueError):
            structural_summary(fixture)
        fixture = dict(FIXTURE_CHART, ruleset='飞盘')
        with self.assertRaises(ValueError):
            structural_summary(fixture)

    def test_incomplete_or_wrong_chart_is_refused(self):
        fixture = dict(FIXTURE_CHART)
        del fixture['star_positions']
        with self.assertRaises(ValueError):
            structural_summary(fixture)
        fixture = dict(FIXTURE_CHART)
        fixture['star_positions'] = dict(fixture['star_positions'])
        del fixture['star_positions']['天心']
        with self.assertRaises(ValueError):
            structural_summary(fixture)
        fixture = dict(FIXTURE_CHART)
        fixture['door_positions'] = dict(fixture['door_positions'])
        del fixture['door_positions']['开门']
        with self.assertRaises(ValueError):
            structural_summary(fixture)
        with self.assertRaises(ValueError):
            structural_summary('not-a-chart')


@unittest.skipUnless(HAS_DATA, 'sealed qfdk tables or lunar_python absent (public checkout)')
class QimenGoldenRegressionTests(unittest.TestCase):
    def test_four_golden_cases_and_fixed_bureau_anchors(self):
        from tianji_kb.golden import run_cases
        from tianji_kb.operations.qimen import bureau
        from tianji_kb.operations.qimen_chart import chart
        self.assertEqual(len(run_cases(domain='qimen')), 4)
        # Fixed solar-term + day-ganzhi bureau anchors (qfdk 表核对）。
        self.assertEqual(bureau('冬至', '甲子')['bureau'], 1)
        self.assertEqual(bureau('冬至', '己巳')['bureau'], 7)
        self.assertEqual(bureau('冬至', '甲戌')['bureau'], 4)
        self.assertEqual(bureau('夏至', '甲子')['dun'], '阴')
        output = chart('2000-01-07T12:00:00+08:00')
        result = output['result']
        summary = structural_summary(result)
        self.assertEqual(summary['chief_star']['palace'], result['chief_star_palace'])
        self.assertEqual(summary['chief_door']['palace'], result['chief_door_palace'])
        self.assertEqual(summary['star_positions'], result['star_positions'])
        self.assertEqual(summary['door_positions'], result['door_positions'])
        self.assertEqual(summary['deity_positions'], result['deity_positions'])
        self.assertEqual(summary['bureau']['number'], result['bureau'])
        self.assertIsNone(summary['verdict'])


if __name__ == '__main__':
    unittest.main()
