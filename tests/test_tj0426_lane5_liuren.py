"""TJ-0426 Lane 5 (O-03): compiled nine-method initial-transmission selection.

Local tests run WITHOUT data/: the compiled selector is pure (the
branch-element table is a pinned module constant; the stem-lodging
table is an explicit caller input, never defaulted). Data-gated
tests (skipUnless the sealed rules/golden files exist) prove
equivalence with the reference implementation
(liuren_chart.select / compute) over all 720 雨水 combinations and
the 11 Golden Cases, and pin the branch-element literal to the
sealed seed table.
"""
import unittest
from pathlib import Path

from tianji_kb.foundations import BRANCHES
from tianji_kb.operations.liuren import (
    BRANCH_ELEMENTS, COMPILED_VARIANT, FUYIN_PUNISH, LIUREN_GAPS,
    NOBLE_VARIANT_REGISTRY, compile_transmissions, noble_variant_status,
    select_initial_transmission, sky_plate,
)

ROOT = Path(__file__).resolve().parents[1]
RULES_FILE = ROOT / 'data/canonical/liuren/rules_v1.json'
GOLDEN_FILE = ROOT / 'data/canonical/liuren/phase2_golden.json'
SEED_FILE = ROOT / 'data/canonical/seed.json'
HAS_DATA = RULES_FILE.exists() and GOLDEN_FILE.exists() and SEED_FILE.exists()


def _lessons(pairs):
    return [{'lesson': i + 1, 'upper': upper, 'lower': lower}
            for i, (upper, lower) in enumerate(pairs)]


class CompiledSelectorLocalTests(unittest.TestCase):
    def test_biyong_from_attested_four_lessons(self):
        # 亥将加子时四课（test_phase1_liuren 的固定四课）：
        # 贼克候选 丑（甲木克土）与子（丑土克水）并存，同性取子 -> 比用。
        sky = sky_plate('亥', '子')
        lessons = _lessons([('丑', '甲'), ('子', '丑'), ('亥', '子'), ('戌', '亥')])
        result = compile_transmissions('甲子', sky, lessons, {'甲': '寅'})
        self.assertEqual(result['method'], '比用')
        self.assertEqual(result['transmissions'], ['子', '亥', '戌'])
        self.assertEqual(result['selection']['control_candidates'], ['丑', '子'])
        self.assertEqual(result['selection']['selection_method'], '比用')
        self.assertEqual(result['variant'], COMPILED_VARIANT)
        self.assertTrue(result['research_only'])
        self.assertFalse(result['public'])
        self.assertFalse(result['ai'])
        self.assertIsNone(result['verdict'])

    def test_fuyin_special_branch_matches_attested_case(self):
        # 伏吟：天盘不动（shift 0），无贼克候选，阳日取初传寅，
        # 中末传走刑链 寅->巳->申（与 compute('雨水','甲子','亥') 的
        # ['寅','巳','申'] 同一链路）。
        sky = {branch: branch for branch in BRANCHES}
        lessons = _lessons([('寅', '甲'), ('寅', '寅'), ('子', '子'), ('子', '子')])
        result = compile_transmissions('甲子', sky, lessons, {'甲': '寅'})
        self.assertEqual(result['method'], '伏吟')
        self.assertEqual(result['transmissions'], ['寅', '巳', '申'])

    def test_fanyin_horse_branch_without_control_candidates(self):
        # 返吟（shift 6）且无贼克候选：驿马分支。日支子属申子辰组，
        # 马在寅；中传取三课上神申，末传取一课上神寅。
        sky = sky_plate('午', '子')
        lessons = _lessons([('寅', '甲'), ('卯', '寅'), ('申', '子'), ('酉', '申')])
        result = compile_transmissions('甲子', sky, lessons, {'甲': '寅'})
        self.assertEqual(result['method'], '返吟')
        self.assertEqual(result['transmissions'], ['寅', '申', '寅'])
        self.assertEqual(result['selection']['control_candidates'], [])

    def test_fanyin_with_candidates_uses_sky_succession(self):
        # 返吟（shift 6）且有贼克候选：仍按比用选初传子，
        # 中末传走天盘续传 [子, 午, 子]，不用驿马分支。
        sky = sky_plate('午', '子')
        lessons = _lessons([('丑', '甲'), ('子', '丑'), ('亥', '子'), ('戌', '亥')])
        result = compile_transmissions('甲子', sky, lessons, {'甲': '寅'})
        self.assertEqual(result['method'], '返吟')
        self.assertEqual(result['transmissions'], ['子', '午', '子'])
        self.assertEqual(result['selection']['selection_method'], '比用')

    def test_lodging_is_never_defaulted_or_borrowed(self):
        # 涉害深浅须寄宫表：无表即拒算，缺干即具名；不得静默默认，
        # 更不得借用八字禄表（己寄午）冒充六壬寄宫。
        # 夹具：贼克候选 子（戌土克水）与寅（申金克木）并存，
        # 同性皆合（子/寅皆偶位），故走涉害深浅，须全表。
        sky = sky_plate('亥', '子')
        lessons_shehai = _lessons([('子', '戌'), ('寅', '申'), ('卯', '子'), ('午', '辰')])
        with self.assertRaises(ValueError):
            select_initial_transmission('甲子', sky, lessons_shehai)
        with self.assertRaises(ValueError):
            select_initial_transmission('甲子', sky, lessons_shehai, {'甲': '寅'})
        # 非涉害路径（比用单同性）不查表，None 可接受。
        lessons = _lessons([('丑', '甲'), ('子', '丑'), ('亥', '子'), ('戌', '亥')])
        result = compile_transmissions('甲子', sky, lessons)
        self.assertEqual(result['method'], '比用')

    def test_invalid_inputs_fail_closed(self):
        sky = sky_plate('亥', '子')
        lessons = _lessons([('丑', '甲'), ('子', '丑'), ('亥', '子'), ('戌', '亥')])
        for day in ('甲丑', '甲', '甲子午', ''):
            with self.assertRaises(ValueError):
                compile_transmissions(day, sky, lessons, {'甲': '寅'})
        bad_sky = dict(sky)
        bad_sky['子'], bad_sky['丑'] = bad_sky['丑'], bad_sky['子']
        with self.assertRaises(ValueError):
            compile_transmissions('甲子', bad_sky, lessons, {'甲': '寅'})
        with self.assertRaises(ValueError):
            compile_transmissions('甲子', sky, lessons[:3], {'甲': '寅'})

    def test_punish_table_matches_reference_literal(self):
        from tianji_kb.operations.liuren_chart import PUNISH
        self.assertEqual(FUYIN_PUNISH, PUNISH)

    def test_noble_variants_stay_partially_structured(self):
        self.assertEqual(set(NOBLE_VARIANT_REGISTRY), {'0', '1'})
        for variant in ('0', '1'):
            entry = noble_variant_status(variant)
            self.assertEqual(entry['status'], 'partially_structured')
            self.assertEqual(entry['evidence_level'], 'C')
        with self.assertRaises(ValueError):
            noble_variant_status(2)
        self.assertEqual(LIUREN_GAPS['heavenly_generals']['status'], 'gap')
        self.assertEqual(LIUREN_GAPS['verdict']['evidence_level'], 'D')


@unittest.skipUnless(HAS_DATA, 'sealed liuren rules/golden/seed files absent (public checkout)')
class CompiledSelectorEquivalenceTests(unittest.TestCase):
    def test_branch_element_literal_matches_sealed_seed(self):
        from tianji_kb.foundations import branch_element
        for branch, element in BRANCH_ELEMENTS.items():
            self.assertEqual(branch_element(branch), element, branch)

    def test_all_720_yushui_combinations_match_reference(self):
        from tianji_kb.foundations import CYCLE
        from tianji_kb.operations.liuren import base, four_lessons
        from tianji_kb.operations.liuren_chart import compute
        lodging = base()['stem_lodging']
        for day in CYCLE:
            for hour in BRANCHES:
                reference = compute('雨水', day, hour)
                sky = reference['sky_plate']
                lessons = four_lessons(day[0], day[1], sky)
                compiled = compile_transmissions(day, sky, lessons, lodging)
                self.assertEqual(compiled['method'], reference['method'], (day, hour))
                self.assertEqual(compiled['transmissions'], reference['transmissions'], (day, hour))

    def test_eleven_golden_cases_match_reference(self):
        from tianji_kb.golden import run_cases
        from tianji_kb.knowledge import read_json
        from tianji_kb.operations.liuren import base, four_lessons
        from tianji_kb.operations.liuren_chart import compute
        self.assertEqual(len(run_cases(domain='liuren')), 11)
        golden = read_json(GOLDEN_FILE)
        lodging = base()['stem_lodging']
        seen_methods = set()
        for case in golden['cases']:
            reference = compute(**case['input'])
            lessons = four_lessons(case['input']['day_ganzhi'][0],
                                   case['input']['day_ganzhi'][1], reference['sky_plate'])
            compiled = compile_transmissions(case['input']['day_ganzhi'],
                                             reference['sky_plate'], lessons, lodging)
            self.assertEqual(compiled['method'], reference['method'], case['id'])
            self.assertEqual(compiled['transmissions'], reference['transmissions'], case['id'])
            seen_methods.add(reference['method'])
        # 至少 3 个《六壬大全》课例对照：此处覆盖全部 11 例，
        # 方法集合须覆盖全部九宗门（与既有 phase2 测试同一口径）。
        self.assertEqual(seen_methods, {'贼克', '比用', '涉害', '遥克', '昴星', '别责', '八专', '伏吟', '返吟'})


if __name__ == '__main__':
    unittest.main()
