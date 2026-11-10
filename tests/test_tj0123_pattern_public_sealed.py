"""TJ-012.3 D-1 寅月真格有限公开呈现 SEALED tests (Stage B).

Offline acceptance ONLY (machine-assembled sealed data tree),
following the test_tj012_d1_yin_research_link_sealed precedent.
This file is deliberately NOT named in .github/workflows/validate.yml:
the bazi-profile execution and the research gate's execute("bazi")
step need the sealed Canonical foundations, which a public checkout
does not contain.

What is verified here and nowhere else:
- the full pattern gate through _bazi_profile over all fifteen
  Golden cases: the attached pattern_presentation equals the builder
  output over the gate's own record and envelope, and its fields
  equal the hand-derived expectations (positive pattern names,
  commander-not-visible conservative presentation, D5 比肩格 not
  public, luren abstention, non-寅月 not_judgeable, and the s2
  distinction -- the live gate carries no precision-warning
  declaration, so the s2 birth enters and presents 七杀格 like t2);
- the 巳月 birth through _bazi_profile presents nothing Ren: the
  Sanming T1 巳月 pilot never enters the Ren presentation;
- the production API carries no raw D-1 trace and the public
  projection keeps only the validated presentation; other scenarios
  carry no pattern key at all;
- the F4 strength gate and this pattern gate do not contaminate
  each other on a shared 丙×寅 甲段 birth (both presentations in
  one envelope, pillars agreeing with the research gate);
- the U1 strength / tiaohou / bingyao / dayun public presentations
  coexist with the new key, each valid in its own closed shape.
"""
import copy
import json
import unittest
from pathlib import Path

from tianji_kb.bazi_dayun_public import (
    is_valid_public_dayun_presentation,
)
from tianji_kb.bazi_pattern_public import (
    is_valid_public_pattern_presentation,
    public_pattern_presentation,
)
from tianji_kb.bazi_strength_public import (
    is_valid_public_strength_presentation,
)
from tianji_kb.bazi_xiyong_public import is_valid_public_presentation
from tianji_kb.engine import execute
from tianji_kb.public_projection import project_execution
from tianji_kb.scenario_engine import (
    _bazi_profile,
    execute_scenario,
    ren_yin_research_execution,
)

ROOT = Path(__file__).resolve().parents[1]
REN_GOLDEN = json.loads(
    (ROOT / 'tests/golden_tj012_ren_yin_true.json').read_text('utf-8'))
LINK_GOLDEN = json.loads(
    (ROOT / 'tests/golden_tj012_d1_yin_research_link.json').read_text('utf-8'))
ZONE = 'Asia/Shanghai'
PILLAR_LABELS = {'year': '年干', 'month': '月干', 'hour': '时干'}

# Hand-derived presentation expectations per Golden case id:
# (status, outcome-or-reason, pattern, statement-or-None,
#  commander stem, visible pillars).
EXPECTED = {
    't1-wu-zhengcai': ('presented', 'true_pattern', '正财格',
                      '司令戊透于时干，真格成立。', '戊', ['hour']),
    'n1-touchstone': ('presented', 'commander_not_visible', None,
                      '司令戊不透，无真格。', '戊', []),
    't2-bing-qisha': ('presented', 'true_pattern', '七杀格',
                      '司令丙透于月干，真格成立。', '丙', ['month']),
    'f1-boundary-minus-1s': ('presented', 'commander_not_visible', None,
                             '司令戊不透，无真格。', '戊', []),
    'f2-boundary-exact': ('presented', 'true_pattern', '伤官格',
                          '司令丙透于月干，真格成立。', '丙', ['month']),
    't3-jia-pianyin': ('presented', 'true_pattern', '偏印格',
                      '司令甲透于年干，真格成立。', '甲', ['year']),
    't4-jia-shishen': ('presented', 'true_pattern', '食神格',
                      '司令甲透于年干，真格成立。', '甲', ['year']),
    's3-route-precedence': ('abstained', 'luren_route_precedence', None,
                            None, None, None),
    'a1-wu-daymaster-neg': ('presented', 'commander_not_visible', None,
                            '司令戊不透，无真格。', '戊', []),
    'a2-wu-daymaster-pos': ('not_judgeable', 'pattern_name_not_public',
                            None, None, None, None),
    'a3-bing-daymaster-neg': ('presented', 'commander_not_visible', None,
                              '司令丙不透，无真格。', '丙', []),
    'a4-bing-daymaster-pos': ('not_judgeable', 'pattern_name_not_public',
                              None, None, None, None),
    'n2-jia-not-visible-2025': ('presented', 'commander_not_visible',
                                None, '司令甲不透，无真格。', '甲', []),
    's1-non-yin': ('not_judgeable', 'month_not_yin', None,
                   None, None, None),
    # s2: the live gate carries no precision-warning declaration,
    # so it enters and presents like t2 (same birth, same pillars).
    's2-pilot-uncertain': ('presented', 'true_pattern', '七杀格',
                           '司令丙透于月干，真格成立。', '丙', ['month']),
}


def _all_keys(node):
    if isinstance(node, dict):
        for key, value in node.items():
            yield key
            yield from _all_keys(value)
    elif isinstance(node, list):
        for item in node:
            yield from _all_keys(item)


class RealProfileGateTests(unittest.TestCase):
    def test_all_golden_cases_through_bazi_profile(self):
        for case in REN_GOLDEN['cases']:
            with self.subTest(case=case['id']):
                birth = case['source_birth']
                profile = _bazi_profile({'value': birth['value'],
                                         'zone': birth['zone']})
                result = profile['result']
                self.assertIn('pattern_presentation', result)
                presentation = result['pattern_presentation']
                self.assertTrue(
                    is_valid_public_pattern_presentation(presentation))
                self.assertNotIn('pattern_determination_ren_yin', result)
                # The attached presentation equals the builder output
                # over the gate's own record and envelope, on the
                # profile's own pillars.
                record = ren_yin_research_execution(
                    birth['value'], birth['zone'])
                execution = None
                if record['entered']:
                    envelope = record['envelope']
                    execution = {
                        'trace': envelope['trace'],
                        'rule_matches': envelope['rule_matches'],
                        'evidence': envelope['evidence'],
                    }
                rebuilt = public_pattern_presentation(
                    record, execution, result['pillars'])
                self.assertEqual(presentation, rebuilt)
                # Hand-derived expectations (Golden, not implementation
                # output): status / outcome-or-reason / pattern /
                # statement / commander / visible pillars.
                (status, second, pattern, statement, stem,
                 visible) = EXPECTED[case['id']]
                self.assertEqual(presentation['status'], status)
                if status == 'presented':
                    self.assertEqual(presentation['outcome'], second)
                    self.assertEqual(presentation['pattern'], pattern)
                    self.assertEqual(presentation['statement'], statement)
                    self.assertEqual(
                        presentation['commander']['stem'], stem)
                    self.assertEqual(
                        presentation['commander']['visible_pillars'],
                        visible)
                    self.assertEqual(
                        presentation['evidence_ids'],
                        sorted(presentation['evidence_ids']))
                    self.assertEqual(presentation['source_ids'],
                                     ['bazi.source.ditiansui-spouse'])
                    self.assertEqual(
                        presentation['rule_ids'],
                        ['renshi.zhenge_definition',
                         'renshi.siling_true_false_procedure'])
                elif status == 'not_judgeable':
                    self.assertEqual(presentation['reason'], second)
                    self.assertNotIn('pattern', presentation)
                    self.assertNotIn(
                        '比肩格',
                        json.dumps(presentation, ensure_ascii=False))
                else:
                    self.assertEqual(presentation['reason'], second)
                    self.assertEqual(presentation['decision_step'], 2)
                # The presentation's day master / month branch are
                # this request's chart facts.
                self.assertEqual(
                    presentation['day_master'], case['day_stem'])
                self.assertEqual(
                    presentation['month_branch'], case['month_branch'])

    def test_si_month_profile_presents_nothing_ren(self):
        case = next(c for c in LINK_GOLDEN['cases']
                    if c['id'] == 'link-si')
        birth = case['source_birth']
        profile = _bazi_profile({'value': birth['value'],
                                 'zone': birth['zone']})
        presentation = profile['result']['pattern_presentation']
        self.assertEqual(presentation['status'], 'not_judgeable')
        self.assertEqual(presentation['reason'], 'month_not_yin')
        self.assertEqual(presentation['month_branch'], '巳')
        self.assertNotIn('pattern', presentation)


class ProductionLeakTests(unittest.TestCase):
    def test_plain_bazi_api_carries_no_pattern_keys(self):
        case = next(c for c in REN_GOLDEN['cases']
                    if c['id'] == 't1-wu-zhengcai')
        plain = execute('bazi', {'value': case['source_birth']['value'],
                                 'zone': ZONE})
        self.assertNotIn('pattern_determination_ren_yin',
                         plain['result'])
        self.assertNotIn('pattern_presentation', plain['result'])

    def test_projection_keeps_only_the_presentation(self):
        case = next(c for c in REN_GOLDEN['cases']
                    if c['id'] == 't1-wu-zhengcai')
        profile = _bazi_profile({'value': case['source_birth']['value'],
                                 'zone': ZONE})
        projected = project_execution(copy.deepcopy(profile))
        self.assertEqual(
            projected['result']['pattern_presentation'],
            profile['result']['pattern_presentation'])
        dumped = json.dumps(projected, ensure_ascii=False)
        self.assertNotIn('pattern_determination_ren_yin', dumped)
        self.assertNotIn('ren_yin_true_pattern', dumped)
        self.assertNotIn('ren-pattern-yin-true-v1', dumped)
        self.assertNotIn('siling-yin-pilot', dumped)
        self.assertNotIn('pattern_determination_ren_yin',
                         projected['result'])
        # The D5 name never reaches a public response.
        a2 = next(c for c in REN_GOLDEN['cases']
                  if c['id'] == 'a2-wu-daymaster-pos')
        projected_a2 = project_execution(copy.deepcopy(_bazi_profile(
            {'value': a2['source_birth']['value'],
             'zone': a2['source_birth']['zone']})))
        self.assertNotIn(
            '比肩格', json.dumps(projected_a2, ensure_ascii=False))

    def test_other_scenarios_carry_no_pattern_key(self):
        samples = {
            'daily': {'birth_value': '2000-01-07T12:00:00+08:00',
                      'target_date': '2026-10-04'},
            'weekly': {'birth_value': '2000-01-07T12:00:00+08:00',
                       'anchor_date': '2026-10-04'},
            'monthly': {'birth_value': '2000-01-07T12:00:00+08:00',
                        'target_month': '2026-10'},
            'yearly': {'birth_value': '2000-01-07T12:00:00+08:00',
                       'target_year': 2026},
            'romance': {'birth_value': '2000-01-07T12:00:00+08:00',
                        'target_year': 2026},
            'career': {'birth_value': '2000-01-07T12:00:00+08:00',
                       'target_year': 2026},
            'life': {'birth_value': '2000-01-07T12:00:00+08:00',
                     'target_year': 2026},
            'question': {'value': '2000-01-07T12:00:00+08:00',
                         'yao_values': [9, 7, 7, 7, 7, 7]},
            'compatibility': {
                'person_a_birth_value': '2000-01-07T12:00:00+08:00',
                'person_b_birth_value': '2000-02-01T12:00:00+08:00'},
        }
        for scenario_id, inputs in samples.items():
            with self.subTest(scenario=scenario_id):
                envelope = execute_scenario(scenario_id, inputs)
                keys = set(_all_keys(envelope))
                self.assertNotIn('pattern_presentation', keys)
                self.assertNotIn('pattern_determination_ren_yin', keys)
                projected = project_execution(copy.deepcopy(envelope))
                self.assertNotIn(
                    'pattern_presentation',
                    json.dumps(projected, ensure_ascii=False))


class GateNonContaminationTests(unittest.TestCase):
    def test_f4_and_pattern_gates_share_one_profile(self):
        # Shared 丙×寅 birth in the 甲段 (t3): the strength gate
        # presents changsheng, the pattern gate presents true 偏印格;
        # both presentations live in one envelope, neither gate's
        # raw output appears in the other's place, and the pillars
        # agree with the research gate's envelope.
        case = next(c for c in REN_GOLDEN['cases']
                    if c['id'] == 't3-jia-pianyin')
        profile = _bazi_profile({'value': case['source_birth']['value'],
                                 'zone': ZONE})
        result = profile['result']
        self.assertIn('strength_presentation', result)
        self.assertIn('pattern_presentation', result)
        self.assertTrue(is_valid_public_strength_presentation(
            result['strength_presentation']))
        self.assertTrue(is_valid_public_pattern_presentation(
            result['pattern_presentation']))
        self.assertEqual(result['pattern_presentation']['pattern'],
                         '偏印格')
        self.assertNotIn('pattern_determination_ren_yin', result)
        self.assertNotIn('strength_assessment', result)
        record = ren_yin_research_execution(
            case['source_birth']['value'], case['source_birth']['zone'])
        self.assertEqual(result['pillars'],
                         record['envelope']['result']['pillars'])


class CoexistenceTests(unittest.TestCase):
    def test_all_four_presentations_coexist_and_validate(self):
        # (12) Existing U1 strength / tiaohou / bingyao / dayun
        # public presentations show no regression: each validates
        # in its own closed shape beside the new key.
        birth = next(c for c in REN_GOLDEN['cases']
                     if c['id'] == 't1-wu-zhengcai')['source_birth']
        envelope = execute_scenario(
            'bazi-profile',
            {'value': birth['value'], 'zone': birth['zone'],
             'traditional_role': 'male'})
        result = envelope['result']
        self.assertTrue(is_valid_public_presentation(
            result['xiyong_presentation']))
        self.assertTrue(is_valid_public_strength_presentation(
            result['strength_presentation']))
        self.assertTrue(is_valid_public_dayun_presentation(
            result['dayun_presentation']))
        self.assertTrue(is_valid_public_pattern_presentation(
            result['pattern_presentation']))
        projected = project_execution(copy.deepcopy(envelope))
        self.assertEqual(
            projected['result']['pattern_presentation'],
            result['pattern_presentation'])
        self.assertEqual(
            projected['result']['strength_presentation'],
            result['strength_presentation'])
        self.assertEqual(
            projected['result']['xiyong_presentation'],
            result['xiyong_presentation'])
        self.assertEqual(
            projected['result']['dayun_presentation'],
            result['dayun_presentation'])


if __name__ == '__main__':
    unittest.main()
