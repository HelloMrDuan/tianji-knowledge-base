import json
from pathlib import Path
import unittest

from tianji_kb.bazi_adjudication import strength_assessment
from tianji_kb.bazi_root_conditions import STRENGTH_VARIANT
from tianji_kb.golden import run_cases
from tianji_kb.operations.bazi_chart import chart
from tianji_kb.resolver import EvidenceResolver, ExecutionTrace

ROOT = Path(__file__).resolve().parents[1]


class StrengthAdjudicationTests(unittest.TestCase):
    def test_seven_fixed_goldens_cover_references_boundaries_and_conflicts(self):
        cases = [c for c in run_cases(ROOT, 'bazi') if c['id'].startswith('bazi.strength-')]
        self.assertEqual(len(cases), 7)
        self.assertTrue(all('bazi.phase2.strength_adjudication' in c['rule_ids'] for c in cases))

    def test_classical_strong_weak_references_do_not_supply_unimplemented_verdicts(self):
        resolver = EvidenceResolver()
        policy = resolver.entities['bazi.concept.strength_adjudication_v1'][1]['attributes']
        self.assertEqual([c['source_classification'] for c in policy['reference_cases']], ['strong', 'weak'])
        for case in policy['reference_cases']:
            out = chart(*case['pillars'], strength_variant=STRENGTH_VARIANT)
            assessment = out['result']['strength_assessment']
            self.assertEqual(assessment['classification'], 'indeterminate')
            self.assertFalse(assessment['source_case_lookup_used'])
        self.assertIn('身弱太甚', resolver.entities['bazi.section.s045'][1]['text'])
        self.assertIn('旺可知矣', resolver.entities['bazi.section.s046'][1]['text'])
        self.assertFalse(policy['full_strength_classifier_ready'])
        self.assertFalse(policy['next_stage_allowed'])

    def test_blockers_resolve_to_real_trace_evidence_and_subvariant(self):
        out = chart('甲子', '丙寅', '甲辰', '戊辰', strength_variant=STRENGTH_VARIANT)
        assessment = out['result']['strength_assessment']
        self.assertTrue(assessment['blockers'])
        for blocker in assessment['blockers']:
            tokens = blocker['fact_ref'].split('/')[2:]
            value = out['trace'][int(tokens[0])]
            for token in tokens[1:]:
                value = value[int(token)] if isinstance(value, list) else value[token]
            self.assertIsNotNone(value)
            self.assertIn(blocker['evidence_id'], out['evidence'])
            self.assertEqual(out['trace'][int(tokens[0])]['rule_id'], blocker['rule_id'])
            self.assertTrue(blocker['variant'])
        conflicts = {cid for b in assessment['blockers'] for cid in b['conflict_ids']}
        self.assertIn('bazi.concept.conflict_siling_days', conflicts)
        self.assertIn('bazi.concept.conflict_root_type_readings', conflicts)

    def test_absent_roots_and_known_directions_do_not_imply_weak_or_balanced(self):
        out = chart('甲申', '甲子', '甲申', '甲戌', strength_variant=STRENGTH_VARIANT)
        self.assertFalse(out['result']['root_conditions']['present_structurally'])
        assessment = out['result']['strength_assessment']
        self.assertEqual(assessment['classification'], 'indeterminate')
        self.assertEqual(assessment['supported_classifications'], [])
        self.assertFalse(assessment['weights_available'])
        self.assertFalse(assessment['ai_enabled'])
        self.assertNotIn('root_availability_unresolved', {b['reason'] for b in assessment['blockers']})

    def test_default_does_not_enable_assessment_and_missing_factors_are_rejected(self):
        self.assertNotIn('strength_assessment', chart('甲寅', '丙寅', '甲子', '戊辰')['result'])
        with self.assertRaises(ValueError):
            strength_assessment(ExecutionTrace('bazi', 'ziping-structural-v1'))
        with self.assertRaises(ValueError):
            strength_assessment(ExecutionTrace('bazi', 'ziping-structural-v1'), strength_variant='unknown')

    def test_reviewed_reference_quotes_are_exact_fixed_source_anchors(self):
        resolver = EvidenceResolver()
        for n in (44, 45, 46):
            section = resolver.entities[f'bazi.section.s{n:03d}'][1]
            source = resolver.sources[section['source_id']]
            raw = (ROOT / source['content_path']).read_text('utf-8')
            self.assertEqual(raw.count(section['text']), 1)
            self.assertTrue(section['locator'].endswith(str(raw.index(section['text']))))


if __name__ == '__main__':
    unittest.main()
