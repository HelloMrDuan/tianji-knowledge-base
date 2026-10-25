"""B012: public execution gate + projection contract for yijing/liuren.

Runs in public CI (validate.yml). No private Canonical/RAG data required:
it imports only tianji_kb.public_projection and exercises the gate set and
the projection function on synthetic chart dicts. It does NOT execute the
real engines (those need full runtime + knowledge data; see
test_b012_tools_engine.py, offline acceptance only).
"""
import unittest

from tianji_kb.public_projection import (
    PUBLIC_EXECUTION_DOMAINS,
    project_execution,
    _PRIVATE_KEYS,
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
        'limitations': [],
    }


def _walk_keys(value):
    if isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from _walk_keys(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_keys(item)


class TestB012PublicGate(unittest.TestCase):
    def test_gate_includes_yijing_and_liuren(self):
        self.assertIn('yijing', PUBLIC_EXECUTION_DOMAINS)
        self.assertIn('liuren', PUBLIC_EXECUTION_DOMAINS)
        # Previously gated domains stay gated.
        self.assertIn('bazi', PUBLIC_EXECUTION_DOMAINS)
        self.assertIn('liuyao', PUBLIC_EXECUTION_DOMAINS)
        # B014 supersedes B012's batch-scoped exclusion: ziwei/qimen/
        # fengshui joined the gate in B014 (see test_b014_tools_public.py
        # for the full seven-domain gate assertion). This test no longer
        # asserts their absence, because that assertion is now false by
        # design, not by regression.

    def test_yijing_projection_strips_private_keys(self):
        chart = {
            'original': {'number': 1, 'name': '乾为天', 'binary': '111111',
                         'lower': '乾', 'upper': '乾'},
            'change': {'number': 44, 'name': '天风姤', 'binary': '011111',
                       'lower': '巽', 'upper': '乾'},
            'canonical_path': '/private/secret/path.json',
            'source_path': '/private/secret/source.txt',
            'trace': [{'rule_id': 'secret-rule-1'}],
        }
        out = project_execution(_synthetic('yijing', chart))
        keys = set(_walk_keys(out['chart']))
        self.assertNotIn('canonical_path', keys)
        self.assertNotIn('source_path', keys)
        self.assertNotIn('trace', keys)
        # Real computed facts survive projection exactly.
        self.assertEqual(out['chart']['original']['name'], '乾为天')
        self.assertEqual(out['chart']['original']['number'], 1)
        self.assertEqual(out['chart']['change']['name'], '天风姤')
        self.assertEqual(out['chart']['change']['number'], 44)
        # Rule ids are aliased, never leaked raw.
        self.assertEqual(out['rule_matches'][0]['rule_id'], 'R01')
        # Unbound evidence ids drop instead of leaking.
        self.assertEqual(out['rule_matches'][0]['evidence_ids'], [])
        # Trace steps become public ordinals only.
        self.assertEqual(out['trace'], [{'step': '计算步骤 01'}])
        self.assertTrue(out['deterministic'])

    def test_liuren_projection_strips_private_keys_and_preserves_limitations(self):
        chart = {
            'month_general': {'terms': ['秋分', '寒露'], 'branch': '辰',
                              'name': '天罡'},
            'method': '遥克',
            'transmissions': ['午', '巳', '辰'],
            'limitations': ['天将未实现：本次六壬结果不含天将（贵人）排布；'
                            '天将起法尚未接入本计算，不作天将相关推断。'],
            'canonical_path': '/private/secret/path.json',
            'source_refs': ['secret-ref'],
            'evidence': {'secret': 'leak'},
        }
        out = project_execution(_synthetic('liuren', chart))
        keys = set(_walk_keys(out['chart']))
        self.assertNotIn('canonical_path', keys)
        self.assertNotIn('source_refs', keys)
        self.assertNotIn('evidence', keys)
        # The limitation declaration channel survives projection verbatim.
        self.assertEqual(out['chart']['limitations'], chart['limitations'])
        # Projection invents no noble-general field.
        self.assertNotIn('noble', keys)
        self.assertNotIn('天将', keys)
        self.assertEqual(out['chart']['method'], '遥克')
        self.assertEqual(out['chart']['transmissions'], ['午', '巳', '辰'])


if __name__ == '__main__':
    unittest.main()
