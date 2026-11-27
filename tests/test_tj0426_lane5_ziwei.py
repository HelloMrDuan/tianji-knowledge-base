"""TJ-0426 Lane 5 (O-01): Ziwei decade/annual candidate arithmetic.

Local tests run WITHOUT data/: anchor checks use the pure
bureau_for()/ziwei_position() functions, and decade/annual arithmetic
takes plain inputs. The data-gated test (skipUnless the sealed
tables exist) replays the full chart('甲子',1,1,'子') anchor and pins
the iztro 壬年化科 cell plus the unreviewed-variant refusal.
"""
import unittest
from pathlib import Path

from tianji_kb.operations.ziwei import (
    FOUR_TRANSFORMATIONS_REN_DISPUTE, KUIYUE_DISPUTE, ZIWEI_GAPS,
    kuiyue_dispute, transformation_disputes,
)
from tianji_kb.operations.ziwei_chart import bureau_for, ziwei_position
from tianji_kb.operations.ziwei_periods import (
    RULE_STATUS, annual_palace, anchor_check, decade_direction,
    decade_periods, decade_start_age,
)

ROOT = Path(__file__).resolve().parents[1]
IZTRO_FILE = ROOT / 'data/canonical/ziwei/iztro_rules_v1.json'
HAS_DATA = IZTRO_FILE.exists()


class ZiweiAnchorLocalTests(unittest.TestCase):
    def test_fixed_classical_anchor_pure_functions(self):
        # 《紫微斗数全书》甲子年正月初一子时：丙寅火六局、酉宫紫微。
        anchor = anchor_check()
        self.assertTrue(anchor['matches'])
        self.assertEqual(anchor['bureau'], {'element': '火', 'number': 6})
        self.assertEqual(anchor['ziwei_branch'], '酉')
        self.assertEqual(bureau_for('丙', '寅'), {'element': '火', 'number': 6})
        self.assertEqual(ziwei_position(1, 6), 9)  # branch index 9 == 酉

    def test_decade_start_age_is_the_bureau_number(self):
        self.assertEqual({n: decade_start_age(n) for n in (2, 3, 4, 5, 6)},
                         {2: 2, 3: 3, 4: 4, 5: 5, 6: 6})
        for bad in (1, 7, 0, '6', 6.0, True):
            with self.assertRaises(ValueError):
                decade_start_age(bad)

    def test_decade_direction_requires_explicit_sex_and_stem(self):
        self.assertEqual(decade_direction('甲', '男'), 'forward')   # 阳干男顺行
        self.assertEqual(decade_direction('甲', '女'), 'backward')  # 阳干女逆行
        self.assertEqual(decade_direction('乙', '女'), 'forward')   # 阴干女顺行
        self.assertEqual(decade_direction('乙', '男'), 'backward')  # 阴干男逆行
        for stem, sex in (('甲', 'M'), ('甲', ''), ('甲', None), ('不明', '男')):
            with self.assertRaises(ValueError):
                decade_direction(stem, sex)

    def test_decade_periods_for_anchor_case(self):
        # 锚点：火六局、命宫酉、甲子年（甲阳干）男命顺行。
        # 大限 6-15 酉命宫，16-25 申兄弟，26-35 未夫妻（沿宫位环）。
        result = decade_periods(bureau_number=6, life_palace_branch='酉',
                                year_stem='甲', sex='男')
        self.assertEqual(result['rule_status'], RULE_STATUS)
        self.assertEqual(result['evidence_level'], 'D')
        self.assertTrue(result['research_only'])
        self.assertFalse(result['public'])
        self.assertFalse(result['ai'])
        self.assertIsNone(result['determination'])
        self.assertIsNone(result['verdict'])
        self.assertEqual(result['direction'], 'forward')
        self.assertEqual(result['decade_start_age'], 6)
        first_three = [(p['palace'], p['branch'], p['age_start'], p['age_end'])
                       for p in result['periods'][:3]]
        self.assertEqual(first_three, [('命宫', '酉', 6, 15),
                                       ('兄弟', '申', 16, 25),
                                       ('夫妻', '未', 26, 35)])
        self.assertEqual(len(result['periods']), 12)
        self.assertEqual([p['age_start'] for p in result['periods']],
                         [6 + 10 * i for i in range(12)])

    def test_decade_periods_backward_goes_to_parents_palace(self):
        result = decade_periods(bureau_number=6, life_palace_branch='酉',
                                year_stem='甲', sex='女')
        self.assertEqual(result['direction'], 'backward')
        self.assertEqual([(p['palace'], p['branch']) for p in result['periods'][:2]],
                         [('命宫', '酉'), ('父母', '戌')])

    def test_annual_palace_convention_is_explicit(self):
        # 生年子、命宫酉：丑年按 branch_plus 得戌父母宫，
        # 按 branch_minus 得申兄弟宫；方向未核定，故无默认值。
        base = dict(life_palace_branch='酉', birth_year_branch='子',
                    target_year_branch='丑')
        plus = annual_palace(convention='branch_plus', **base)
        self.assertEqual((plus['annual_palace'], plus['annual_palace_branch']), ('父母', '戌'))
        self.assertEqual(plus['year_offset'], 1)
        minus = annual_palace(convention='branch_minus', **base)
        self.assertEqual((minus['annual_palace'], minus['annual_palace_branch']), ('兄弟', '申'))
        for bad in (None, 'forward', ''):
            with self.assertRaises(ValueError):
                annual_palace(convention=bad, **base)
        same_year = annual_palace(convention='branch_plus', target_year_branch='子', **{
            'life_palace_branch': '酉', 'birth_year_branch': '子'})
        self.assertEqual(same_year['annual_palace'], '命宫')

    def test_book_case_counterpart_for_new_inference(self):
        # 新增推断的书中命例对照：锚点盘（甲子年正月初一子时）之外，
        # 以同一纯函数核对另一局：水二局起 2 岁、命宫顺行首运在命宫。
        result = decade_periods(bureau_number=2, life_palace_branch='子',
                                year_stem='丙', sex='男')
        self.assertEqual(result['periods'][0], {'decade': 1, 'palace': '命宫',
                                                'branch': '子', 'age_start': 2, 'age_end': 11})


class ZiweiDisputeRegistryTests(unittest.TestCase):
    def test_ren_four_transformations_dispute_only_registered(self):
        dispute = transformation_disputes()['壬']
        self.assertEqual(dispute['status'], 'unresolved')
        self.assertEqual(dispute['evidence_level'], 'D')
        self.assertIsNone(dispute['determination'])
        # Only the attested cell is recorded; the full row stays the
        # unchanged iztro table and is never re-decoded here.
        self.assertEqual(dispute['iztro_default_v2'], {'化科': '左辅'})
        self.assertIn('壬梁紫府武', dispute['isolated_candidate']['original_text_contains'])
        self.assertEqual(dispute['isolated_candidate']['stage'], 'quarantine')

    def test_kuiyue_dispute_only_registered(self):
        dispute = kuiyue_dispute()
        self.assertEqual(dispute['status'], 'unresolved')
        self.assertEqual(dispute['classical_reading'], '丙丁猪狗')
        self.assertEqual(dispute['modern_implementation_reading'], '丙丁猪鸡')
        self.assertEqual(dispute['structured_rules_retained'], 'partial')
        self.assertIsNone(dispute['determination'])
        self.assertEqual(KUIYUE_DISPUTE['stars'], ('天魁', '天钺'))

    def test_gaps_carry_evidence_levels(self):
        self.assertEqual(ZIWEI_GAPS['decade_annual']['status'], 'candidate_pending_collation')
        self.assertEqual(ZIWEI_GAPS['temple_prosperity']['status'], 'gap')
        for entry in ZIWEI_GAPS.values():
            self.assertIn(entry['evidence_level'], ('C', 'D'))


@unittest.skipUnless(HAS_DATA, 'sealed ziwei tables absent (public checkout)')
class ZiweiAnchorSealedTests(unittest.TestCase):
    def test_full_chart_anchor_and_unchanged_mutagen_table(self):
        from tianji_kb.golden import run_cases
        from tianji_kb.operations.ziwei import four_transformations
        from tianji_kb.operations.ziwei_chart import chart
        self.assertEqual(len(run_cases(domain='ziwei')), 3)
        result = chart('甲子', 1, 1, '子')['result']
        self.assertEqual(result['bureau'], {'element': '火', 'number': 6})
        self.assertEqual(result['life_palace'], '酉')
        self.assertEqual(result['life_ganzhi'], '丙寅')
        self.assertEqual(result['major_stars']['紫微'], '酉')
        self.assertEqual(result['mutagen_variant'], 'iztro-default-v2')
        # 壬年四化表值未改：化科仍为左辅；未核定 variant 仍拒绝。
        self.assertEqual(four_transformations('壬', 'iztro-default-v2')['化科'], '左辅')
        with self.assertRaises(ValueError):
            four_transformations('壬', 'unreviewed-quanshu-reading')
        # 大限候选算术与整盘输出一致：命宫酉、火六局、甲阳干男顺行。
        periods = decade_periods(bureau_number=result['bureau']['number'],
                                 life_palace_branch=result['life_palace'],
                                 year_stem='甲', sex='男')
        self.assertEqual(periods['periods'][0]['palace'], '命宫')
        self.assertEqual(periods['periods'][0]['age_start'], 6)


if __name__ == '__main__':
    unittest.main()
