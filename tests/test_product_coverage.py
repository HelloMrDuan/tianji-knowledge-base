import asyncio
import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from phase4_helpers import valid_reply
from tianji_kb.engine import execute
from tianji_kb.explanation import ExplanationFailure, validate_reply
from tianji_kb.knowledge import read_json
from tianji_kb.product_coverage import build_product_coverage, inventory, dependency_report
from tianji_kb.product_claims import product_preflight, validate_calculation_basis, ProductExplanationService, authorize_structural_claim
from tianji_kb.claim_capabilities import bind_structural_claim
from tianji_kb.prompts import get_prompt
from tianji_kb.resolver import EvidenceResolver
from tianji_kb.scenario_engine import registry as scenario_registry, execute_scenario

ROOT = Path(__file__).resolve().parents[1]


class ProductCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.resolver = EvidenceResolver(ROOT, review_sources=True)
        # Use reviewed source resolver for this static audit suite, independently
        # of the existing runtime cache's Windows path issue (tracked in PR88).
        with patch('tianji_kb.engine.EvidenceResolver', return_value=cls.resolver), patch('tianji_kb.resolver.EvidenceResolver', return_value=cls.resolver):
            cls.raw = execute('yijing', {'bits': '111111', 'changing_lines': [1]})
        cls.report = read_json(ROOT / 'data/product/knowledge_coverage.json')

    def test_all_requested_products_and_specialist_tools_have_no_fake_authorization(self):
        rows = build_product_coverage(ROOT)
        self.assertEqual(len(rows) - 1, 16)
        self.assertEqual(sum(len(e['rules']) for e in rows['_audit']['engines'].values()), 52)
        self.assertEqual(sum(len(e['golden_ids']) for e in rows['_audit']['engines'].values()), 44)
        self.assertTrue(rows['_audit']['engines']['bazi']['registered'])
        self.assertEqual(rows['_audit']['engines']['bazi']['variant'], 'ziping-structural-v1')
        self.assertEqual(rows['_audit']['source_grades'], {'C': 91, 'D': 6})
        self.assertEqual(len(rows['_audit']['conflict_entities']), 3)
        self.assertTrue(rows['compatibility']['scenario_status']['runtime_implemented'])
        self.assertTrue(rows['bazi-reading']['scenario_status']['structural_public_release'])
        for pid, row in rows.items():
            if pid.startswith('_'): continue
            self.assertFalse(row['full_interpretation_ready'])
            self.assertEqual(row['production_claims'], row['ready_claims'])
            self.assertFalse(row['ai_enabled'])
        self.assertEqual(rows['dream']['status'], 'NOT_BUILT')
        self.assertEqual(rows['compatibility']['status'], 'PRODUCTIZABLE')
        self.assertEqual(rows['romance']['ready_claims'], ['romance.xianchi_structure'])
        self.assertIn('relationship.branch_clash', rows['compatibility']['ready_claims'])
        self.assertTrue(rows['_audit']['topics']['bazi-strength']['classical_text_candidates'])
        self.assertFalse(rows['_audit']['topics']['bazi-strength']['explanation_ready'])

    def test_missing_or_forged_rule_reference_is_not_counted_as_supported(self):
        spec = read_json(ROOT / 'config/product_requirements.json')
        spec['topics']['liuyao-inquiry']['execution_rules'].append('liuyao.fake.forecast')
        original = read_json
        def reader(path):
            return spec if path == ROOT / 'config/product_requirements.json' else original(path)
        with patch('tianji_kb.product_coverage.read_json', side_effect=reader):
            with self.assertRaisesRegex(ValueError, 'unknown execution Rule'):
                build_product_coverage(ROOT)

    def test_inventory_is_case_sensitive_portable_and_matches_exact_input_bytes(self):
        rows=inventory(ROOT)
        paths=[row['path'] for row in rows]
        self.assertEqual(paths,sorted(paths))

    def test_every_current_product_refuses_before_model_or_retriever_invocation(self):
        class ForbiddenProvider:
            async def explain(self, context):
                raise AssertionError('Model must never be called')
        class ForbiddenRetriever:
            def retrieve(self, raw):
                raise AssertionError('Retriever must never be called')
        service = ProductExplanationService(ROOT, ForbiddenProvider(), retriever=ForbiddenRetriever())
        for pid in self.report:
            if pid.startswith('_'): continue
            with self.assertRaisesRegex(ExplanationFailure, 'product_claim_unavailable|scenario_claim_unavailable|ai_quality_not_approved'):
                asyncio.run(service.explain(pid, self.raw))

    def test_stale_coverage_and_edited_booleans_never_release_product(self):
        report = copy.deepcopy(self.report)
        report['_audit']['input_files'][0]['sha256'] = '0' * 64
        with patch('tianji_kb.product_claims.read_json', return_value=report):
            with self.assertRaisesRegex(ExplanationFailure, 'product_coverage_stale'):
                product_preflight(ROOT, 'yijing-tool', self.raw)
        report = copy.deepcopy(self.report)
        report['one-question'].update(production_ready=True, public_enabled=True, ai_enabled=True,
                                      production_claims=['invented-permission'])
        scenarios = scenario_registry()
        for s in scenarios:
            s.update(public_release=True)
        with patch('tianji_kb.product_claims.read_json', return_value=report), patch('tianji_kb.product_claims.scenario_registry', return_value=scenarios):
            with self.assertRaisesRegex(ExplanationFailure, 'ai_quality_not_approved'):
                product_preflight(ROOT, 'one-question', self.raw)

    def test_ready_claims_bind_actual_scenario_facts_without_opening_advanced_predictions(self):
        with patch('tianji_kb.engine.EvidenceResolver', return_value=self.resolver), patch('tianji_kb.resolver.EvidenceResolver', return_value=self.resolver):
            profile = execute_scenario('bazi-profile', {'value': '2000-01-01T12:00:00+08:00'})
            romance = execute_scenario('romance', {'birth_value': '2000-01-01T12:00:00+08:00', 'target_year': 2026})
            pair = execute_scenario('compatibility', {'person_a_birth_value': '2000-01-01T12:00:00+08:00', 'person_b_birth_value': '2001-01-01T12:00:00+08:00'})
        claim = authorize_structural_claim(ROOT, 'bazi-reading', profile, 'bazi.day_master', resolver=self.resolver)
        self.assertEqual(claim['fact_value'], profile['result']['day_master'])
        self.assertTrue(claim['evidence'])
        self.assertFalse(claim['ai_enabled'])
        self.assertTrue(authorize_structural_claim(ROOT, 'romance', romance, 'romance.xianchi_structure', resolver=self.resolver)['evidence'])
        clash = authorize_structural_claim(ROOT, 'compatibility', pair, 'relationship.branch_clash', resolver=self.resolver)
        self.assertTrue(all(r['kind'] == 'clash' for r in clash['fact_value']))
        for forbidden in ('bazi.yongshen', 'fortune.year_good_bad', 'marriage.marriage_date'):
            with self.assertRaisesRegex(ExplanationFailure, 'product_claim_unavailable'):
                authorize_structural_claim(ROOT, 'bazi-reading', profile, forbidden, resolver=self.resolver)
        bad = copy.deepcopy(profile); bad['rule_matches'][0]['matched'] = False
        with self.assertRaisesRegex(ValueError, 'claim_rule_not_fired'):
            bind_structural_claim(bad, 'bazi.pillars', self.resolver)
        bad = copy.deepcopy(romance); bad['rule_matches'][0]['derived_from_rule_id'] = 'bazi.phase2.pillars'
        with self.assertRaisesRegex(ValueError, 'claim_composition_mismatch'):
            bind_structural_claim(bad, 'romance.xianchi_structure', self.resolver)
        bad = copy.deepcopy(profile); bad['evidence'][next(iter(bad['evidence']))]['original_text'] = '伪造'
        with self.assertRaisesRegex(ValueError, 'claim_evidence_mismatch'):
            bind_structural_claim(bad, 'bazi.pillars', self.resolver)

    def test_dependency_graph_preserves_structural_readiness_and_rejects_cycles(self):
        spec = read_json(ROOT / 'config/product_requirements.json')
        graph = dependency_report(self.report, spec)
        self.assertIn('bazi-strength', graph['topics']['bazi-pattern']['depends_on'])
        self.assertIn('bazi.pillars', graph['products']['bazi-reading']['ready_claims'])
        self.assertFalse(graph['knowledge_authority'])
        spec['topic_dependencies']['bazi-foundation'] = ['bazi-pattern']
        with self.assertRaisesRegex(ValueError, 'dependency cycle'):
            dependency_report(self.report, spec)

    def test_new_prompt_preserves_frozen_versions_and_validates_existing_claim_chain(self):
        self.assertEqual(get_prompt('explanation-prompt-v1')['sha256'], 'b831f0e70ad357f627fa5ad546edc3ba72c96c2585cd4f6196dcde7cc76b06af')
        context = validate_calculation_basis(ROOT, self.raw, resolver=self.resolver)
        self.assertIn('Absence of knowledge is not permission to use model prior knowledge.', context['instructions'])
        reply = valid_reply(context)
        result = validate_reply(reply, context)
        self.assertEqual(result['prompt_version'], 'explanation-prompt-v3')
        self.assertFalse(result['automatic_release_allowed'])
        bad = copy.deepcopy(reply)
        bad['claims'][0]['fact_value'] = 'invented'
        with self.assertRaisesRegex(ExplanationFailure, 'chart_fact_mismatch'):
            validate_reply(bad, context)
        bad = copy.deepcopy(reply)
        bad['claims'][0]['rule_ids'] = ['yijing.phase2.nuclear']
        with self.assertRaises(ExplanationFailure): validate_reply(bad, context)

    def test_absent_fact_unmatched_rule_unresolved_conflict_and_wrong_variant_refuse(self):
        mutations = [lambda r: r.update(deterministic=False),
                     lambda r: r['result'].pop('original'),
                     lambda r: r.update(source_conflicts=['unresolved']),
                     lambda r: r.update(variant='unreviewed'),
                     lambda r: r['rule_matches'][0].update(rule_id='invented-rule')]
        for mutate in mutations:
            raw = copy.deepcopy(self.raw); mutate(raw)
            with self.assertRaises(ExplanationFailure):
                validate_calculation_basis(ROOT, raw, resolver=self.resolver)
        resolver = copy.copy(self.resolver)
        resolver.contracts = copy.deepcopy(self.resolver.contracts)
        resolver.contracts['yijing']['rules'][0]['execution_status'] = 'descriptive_only'
        with self.assertRaisesRegex(ExplanationFailure, 'rule_not_executable'):
            validate_calculation_basis(ROOT, self.raw, resolver=resolver)
        resolver.contracts['yijing']['rules'][0]['execution_status'] = 'executable'
        resolver.contracts['yijing']['rules'][0]['golden_case_ids'] = ['missing-golden']
        with self.assertRaisesRegex(ExplanationFailure, 'golden_case_missing'):
            validate_calculation_basis(ROOT, self.raw, resolver=resolver)

    def test_forged_citations_and_unbound_natural_language_claims_refuse(self):
        raw = copy.deepcopy(self.raw)
        eid = next(iter(raw['evidence']))
        raw['evidence'][eid]['original_text'] = '伪造古籍'
        with self.assertRaisesRegex(ExplanationFailure, 'citation_rejected'):
            validate_calculation_basis(ROOT, raw, resolver=self.resolver)
        context = validate_calculation_basis(ROOT, self.raw, resolver=self.resolver)
        bad = valid_reply(context)
        bad['claims'][0]['text'] = '必然发财，确定结论'
        with self.assertRaisesRegex(ExplanationFailure, 'unsupported_certainty'):
            validate_reply(bad, context)

    def test_sanming_stays_quarantined_and_complete_pua_is_not_canonical_approval(self):
        sanming = self.report['_audit']['sanming']
        self.assertFalse(sanming['canonical_ready'])
        self.assertEqual(sanming['confirmed_private_use_mappings'], 86)
        self.assertEqual(sanming['confirmed_occurrences'], 524)
        self.assertEqual(sanming['remaining_private_use_chars'], 0)
        self.assertFalse((ROOT / 'data/canonical/classics/bazi/sanming_tonghui_v1.json').exists())

    def test_two_source_candidates_use_existing_quarantine_contract_without_promotion(self):
        directory = ROOT / 'data/quarantine/phase1_candidates/daizhigev20/4a6d6f2088825f132521d848c2ea86cf9c9a7620'
        candidates = [directory / (blob + '.json') for blob in ('e269843d0544fd18ac7d7c97d4e0bd268a5240ef', 'c7de6ab493e19460f5efba49085d20437c17e1d4')]
        for path in candidates:
            row = read_json(path)
            self.assertEqual(row['review_status'], 'pending')
            self.assertEqual(row['stage'], 'quarantine')
            self.assertEqual(row['evidence_level'], 'D')
            self.assertFalse(row['promotion_allowed'])
            self.assertFalse(row['body_saved_to_quarantine'])


if __name__ == '__main__':
    unittest.main()
