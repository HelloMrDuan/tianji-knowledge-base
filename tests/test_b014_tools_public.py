"""B014: public execution gate + projection contract for ziwei/qimen/fengshui.

Runs in public CI (validate.yml). No private Canonical/RAG data required:
it imports only tianji_kb.public_projection and exercises the gate set and
the projection function on synthetic chart dicts. It does NOT execute the
real engines (those need full runtime + knowledge data; see
test_b014_tools_engine.py, offline acceptance only).
"""
import unittest

from tianji_kb.public_projection import (
    PUBLIC_EXECUTION_DOMAINS,
    project_execution,
)


def _synthetic(domain, chart):
    return {
        'domain': domain,
        'variant': 'test-variant',
        'mode': 'production',
        'deterministic': True,
        'chart': chart,
        'rule_matches': [
            {'rule_id': 'secret-rule-1', 'matched': True,
             'kind': 'executed_calculation', 'evidence_scope': '',
             'evidence_ids': ['secret-evidence-1']},
        ],
        'trace': [{'rule_id': 'secret-rule-1'}],
        'evidence': {},
        'warnings': [],
        'limitations': ['test-scope', 'test-unresolved'],
    }


def _walk_keys(value):
    if isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from _walk_keys(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_keys(item)


class TestB014PublicGate(unittest.TestCase):
    def test_gate_includes_ziwei_qimen_fengshui(self):
        self.assertIn('ziwei', PUBLIC_EXECUTION_DOMAINS)
        self.assertIn('qimen', PUBLIC_EXECUTION_DOMAINS)
        self.assertIn('fengshui', PUBLIC_EXECUTION_DOMAINS)
        # Previously gated domains stay gated.
        for domain in ('bazi', 'liuyao', 'yijing', 'liuren'):
            self.assertIn(domain, PUBLIC_EXECUTION_DOMAINS)
        # The gate is exactly these seven domains in this batch.
        self.assertEqual(set(PUBLIC_EXECUTION_DOMAINS),
                         {'bazi', 'liuyao', 'yijing', 'liuren',
                          'ziwei', 'qimen', 'fengshui'})

    def test_ziwei_projection_strips_private_keys_and_preserves_scope(self):
        chart = {
            'life_palace': '子', 'body_palace': '戌', 'life_ganzhi': '庚子',
            'bureau': {'element': '土', 'number': 5},
            'palaces': {'命宫': '子', '兄弟': '亥'},
            'major_stars': {'紫微': '亥', '天机': '戌'},
            'auxiliary_stars': {'左辅': '未'},
            'four_transformations': {'化禄': '天同', '化忌': '廉贞'},
            'mutagen_variant': 'iztro-default-v2',
            'mutagen_evidence': 'D implementation table; classical types are C; 壬府/辅 unresolved',
            'input_scope': '显式非闰月农历；年干支由调用方按约定年界提供；无大限流年或庙旺吉凶',
            'canonical_path': '/private/secret/path.json',
            'source_refs': ['secret-ref'],
            'trace': [{'rule_id': 'secret-rule-1'}],
        }
        out = project_execution(_synthetic('ziwei', chart))
        keys = set(_walk_keys(out['chart']))
        self.assertNotIn('canonical_path', keys)
        self.assertNotIn('source_refs', keys)
        self.assertNotIn('trace', keys)
        # Real computed facts survive exactly.
        self.assertEqual(out['chart']['life_palace'], '子')
        self.assertEqual(out['chart']['body_palace'], '戌')
        self.assertEqual(out['chart']['life_ganzhi'], '庚子')
        self.assertEqual(out['chart']['palaces']['命宫'], '子')
        self.assertEqual(out['chart']['major_stars']['紫微'], '亥')
        self.assertEqual(out['chart']['four_transformations']['化禄'], '天同')
        # Boundary declarations survive verbatim.
        self.assertEqual(out['chart']['input_scope'], chart['input_scope'])
        self.assertEqual(out['chart']['mutagen_evidence'],
                         chart['mutagen_evidence'])
        # No dayun field is invented; the scope itself states the exclusion.
        self.assertNotIn('dayun', keys)
        self.assertIn('无大限流年', out['chart']['input_scope'])
        # Rule ids are aliased, never leaked raw.
        self.assertEqual(out['rule_matches'][0]['rule_id'], 'R01')
        # Trace steps become public ordinals only.
        self.assertEqual(out['trace'], [{'step': '计算步骤 01'}])
        self.assertTrue(out['deterministic'])

    def test_qimen_projection_strips_private_keys_and_preserves_scope(self):
        chart = {
            'dun': '阴', 'bureau': 7, 'yuan': '上元',
            'chief_star': {'name': '天心', 'names': ['天心'],
                           'origin': '6', 'palace': '4'},
            'chief_door': {'name': '开门', 'palace': '8'},
            'star_positions': {'天蓬': '9', '天心': '4'},
            'door_positions': {'休门': '3', '开门': '8'},
            'deity_positions': {'值符': '4'},
            'scope': '基础符号盘；不含置闰、超神接气、暗干、格局占断与其他流派。',
            'center_star_policy': '天禽随天芮同宫（禽芮）；保留所选qfdk转盘约定',
            'canonical_path': '/private/secret/path.json',
            'evidence': {'secret': 'leak'},
        }
        out = project_execution(_synthetic('qimen', chart))
        keys = set(_walk_keys(out['chart']))
        self.assertNotIn('canonical_path', keys)
        self.assertNotIn('evidence', keys)
        # Real computed facts survive exactly.
        self.assertEqual(out['chart']['dun'], '阴')
        self.assertEqual(out['chart']['bureau'], 7)
        self.assertEqual(out['chart']['yuan'], '上元')
        self.assertEqual(out['chart']['chief_star']['name'], '天心')
        self.assertEqual(out['chart']['chief_door']['name'], '开门')
        self.assertEqual(out['chart']['star_positions']['天蓬'], '9')
        # The super-intercalation exclusion survives verbatim in scope.
        self.assertEqual(out['chart']['scope'], chart['scope'])
        self.assertIn('不含置闰', out['chart']['scope'])
        # No intercalation field is invented.
        self.assertNotIn('intercalation', keys)
        self.assertNotIn('super_intercalation', keys)
        self.assertEqual(out['rule_matches'][0]['rule_id'], 'R01')
        self.assertEqual(out['trace'], [{'step': '计算步骤 01'}])

    def test_fengshui_projection_strips_private_keys_and_keeps_period_none(self):
        chart = {
            'degrees': 180, 'mountain': '午', 'mountain_element': '火',
            'trigram': '离', 'trigram_element': '火', 'opposite': '子',
            'period': None,
            'canonical_path': '/private/secret/path.json',
            'source_path': '/private/secret/source.txt',
        }
        out = project_execution(_synthetic('fengshui', chart))
        keys = set(_walk_keys(out['chart']))
        self.assertNotIn('canonical_path', keys)
        self.assertNotIn('source_path', keys)
        # Real computed facts survive exactly.
        self.assertEqual(out['chart']['degrees'], 180)
        self.assertEqual(out['chart']['mountain'], '午')
        self.assertEqual(out['chart']['mountain_element'], '火')
        self.assertEqual(out['chart']['trigram'], '离')
        self.assertEqual(out['chart']['opposite'], '子')
        # Production gate: no absolute period is smuggled through.
        self.assertIsNone(out['chart']['period'])
        # Top-level limitations channel survives projection.
        self.assertEqual(out['limitations'], ['test-scope', 'test-unresolved'])
        self.assertEqual(out['rule_matches'][0]['rule_id'], 'R01')
        self.assertEqual(out['trace'], [{'step': '计算步骤 01'}])


if __name__ == '__main__':
    unittest.main()
