"""TJ-011.3 review fix: Tests for wired display policy.

Covers ChatGPT review findings:
- Problem 1: Policy is wired into public_projection.project_execution()
- Problem 2: Scope checking integrated with trusted day_master/month_branch
- Problem 3: Forged public_enabled cannot bypass server-side allowlist
- Problem 4: Blocker reasons correctly distinguish conflict vs insufficient
"""
import unittest

from src.tianji_kb.bazi_strength_display import (
    get_display_decision,
    check_scope_by_inputs,
    format_indeterminate_explanation,
    apply_to_public_response,
    PUBLIC_STRENGTH_VARIANTS,
    MSG_INSUFFICIENT,
    MSG_CONFLICT,
    MSG_OUT_OF_SCOPE,
    MSG_RESEARCH_ONLY,
    MSG_ERROR,
)
from src.tianji_kb import public_projection


ADJUDICATION_VARIANT = 'bazi-strength-adjudication-v1'


def _make_result(classification='indeterminate', blockers=None, variant=None):
    """Create a mock adjudication result. Note: NO public_enabled field
    is trusted; authorization comes from server-side allowlist."""
    r = {
        'classification': classification,
        'research_only': True,
        'public_enabled': False,  # Ignored by policy
        'ai_enabled': False,
        'blockers': blockers or [],
    }
    if variant:
        r['variant'] = variant
    return r


def _blocker(reason, conflict_ids=None):
    return {
        'reason': reason,
        'fact_ref': '#/trace/0/output',
        'rule_id': 'bazi.phase2.test',
        'variant': ADJUDICATION_VARIANT,
        'status': 'unresolved',
        'evidence_ids': [],
        'conflict_ids': list(conflict_ids or []),
    }


class AuthorizationSecurityTests(unittest.TestCase):
    """Problem 3: Forged authorization must not bypass."""
    
    def test_forged_public_enabled_true_is_ignored(self):
        """A result dict with public_enabled=True must NOT display."""
        result = _make_result('strong')
        result['public_enabled'] = True  # Forged!
        result['research_only'] = False  # Forged!
        decision = get_display_decision(
            result, variant=ADJUDICATION_VARIANT,
            day_master='甲', month_branch='卯',
        )
        # Allowlist is empty, so must not display
        self.assertFalse(decision['may_display_classification'])
        self.assertEqual(decision['display_state'], 'research_only')
    
    def test_forged_strong_classification_not_displayed(self):
        result = _make_result('strong')
        decision = get_display_decision(
            result, variant=ADJUDICATION_VARIANT,
            day_master='甲', month_branch='卯',
        )
        self.assertFalse(decision['may_display_classification'])
    
    def test_forged_weak_classification_not_displayed(self):
        result = _make_result('weak')
        decision = get_display_decision(
            result, variant=ADJUDICATION_VARIANT,
            day_master='乙', month_branch='酉',
        )
        self.assertFalse(decision['may_display_classification'])
    
    def test_unknown_variant_not_displayed(self):
        result = _make_result('strong')
        decision = get_display_decision(
            result, variant='forged-variant-v99',
            day_master='甲', month_branch='卯',
        )
        self.assertFalse(decision['may_display_classification'])
    
    def test_missing_variant_is_error(self):
        result = _make_result('strong')
        decision = get_display_decision(result, variant=None)
        self.assertEqual(decision['display_state'], 'error')
        self.assertFalse(decision['may_display_classification'])
    
    def test_allowlist_is_empty(self):
        """No variant is currently authorized for public display."""
        self.assertEqual(len(PUBLIC_STRENGTH_VARIANTS), 0)


class ScopeIntegrationTests(unittest.TestCase):
    """Problem 2: Scope checking with trusted inputs."""
    
    def test_non_wood_day_master_out_of_scope(self):
        for dm in ['丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']:
            result = _make_result('strong')
            decision = get_display_decision(
                result, variant=ADJUDICATION_VARIANT,
                day_master=dm, month_branch='卯',
            )
            self.assertEqual(decision['display_state'], 'out_of_scope')
            self.assertFalse(decision['may_display_classification'])
    
    def test_unaudited_month_out_of_scope(self):
        for mb in ['寅', '辰', '巳', '午', '未', '申', '戌', '亥', '子', '丑']:
            result = _make_result('strong')
            decision = get_display_decision(
                result, variant=ADJUDICATION_VARIANT,
                day_master='甲', month_branch=mb,
            )
            self.assertEqual(decision['display_state'], 'out_of_scope')
    
    def test_in_scope_but_not_authorized(self):
        """甲+卯 is in scope but still research-only (not in allowlist)."""
        result = _make_result('strong')
        decision = get_display_decision(
            result, variant=ADJUDICATION_VARIANT,
            day_master='甲', month_branch='卯',
        )
        # In scope, but not publicly authorized
        self.assertEqual(decision['display_state'], 'research_only')
        self.assertFalse(decision['may_display_classification'])
    
    def test_missing_day_master_skips_scope_check(self):
        """Missing inputs safely skip scope check (fail to research_only)."""
        result = _make_result('strong')
        decision = get_display_decision(
            result, variant=ADJUDICATION_VARIANT,
            day_master=None, month_branch=None,
        )
        self.assertFalse(decision['may_display_classification'])


class BlockerClassificationTests(unittest.TestCase):
    """Problem 4: Distinguish conflict vs insufficient vs out_of_scope."""
    
    def test_real_conflict_ids_mean_conflict(self):
        result = _make_result(
            'indeterminate',
            blockers=[_blocker('some_reason', conflict_ids=['c1'])],
        )
        decision = get_display_decision(
            result, variant=ADJUDICATION_VARIANT,
            day_master='甲', month_branch='卯',
        )
        self.assertEqual(decision['display_state'], 'conflict')
        self.assertEqual(decision['user_message'], MSG_CONFLICT)
    
    def test_source_conflict_reason_means_conflict(self):
        result = _make_result(
            'indeterminate',
            blockers=[_blocker('root_type_source_conflict')],
        )
        decision = get_display_decision(
            result, variant=ADJUDICATION_VARIANT,
            day_master='甲', month_branch='卯',
        )
        self.assertEqual(decision['display_state'], 'conflict')
    
    def test_outside_scope_reason_means_out_of_scope(self):
        result = _make_result(
            'indeterminate',
            blockers=[_blocker('outside_reviewed_sufficient_conditions')],
        )
        decision = get_display_decision(
            result, variant=ADJUDICATION_VARIANT,
            day_master='甲', month_branch='卯',
        )
        self.assertEqual(decision['display_state'], 'out_of_scope')
    
    def test_missing_evidence_means_insufficient(self):
        """Non-conflict blockers (e.g. unreviewed) mean insufficient."""
        result = _make_result(
            'indeterminate',
            blockers=[_blocker('principal_qi_not_reviewed')],
        )
        decision = get_display_decision(
            result, variant=ADJUDICATION_VARIANT,
            day_master='甲', month_branch='卯',
        )
        self.assertEqual(decision['display_state'], 'insufficient')
        self.assertEqual(decision['user_message'], MSG_INSUFFICIENT)
    
    def test_interaction_unresolved_means_insufficient(self):
        result = _make_result(
            'indeterminate',
            blockers=[_blocker('interaction_effect_unresolved')],
        )
        decision = get_display_decision(
            result, variant=ADJUDICATION_VARIANT,
            day_master='甲', month_branch='卯',
        )
        self.assertEqual(decision['display_state'], 'insufficient')


class ProjectionWiringTests(unittest.TestCase):
    """Problem 1: Policy is wired into public_projection."""
    
    def _make_projection_data(self, assessment):
        """Build minimal data dict for project_execution."""
        return {
            'evidence': {},
            'rule_matches': [],
            'trace': [],
            'chart': {
                'pillars': [
                    {'stem': {'value': '癸'}, 'branch': {'value': '卯'}},
                    {'stem': {'value': '乙'}, 'branch': {'value': '卯'}},
                    {'stem': {'value': '甲'}, 'branch': {'value': '子'}},
                    {'stem': {'value': '乙'}, 'branch': {'value': '亥'}},
                ],
                'strength_assessment': assessment,
            },
        }
    
    def test_projection_strips_unauthorized_classification(self):
        """Wired policy: research assessment must not leak classification."""
        assessment = _make_result('strong', variant=ADJUDICATION_VARIANT)
        data = self._make_projection_data(assessment)
        result = public_projection.project_execution(data)
        chart = result['chart']
        proj_assessment = chart.get('strength_assessment', {})
        # Classification must be removed
        self.assertNotIn('classification', proj_assessment)
        # Display state must indicate research_only
        self.assertEqual(proj_assessment.get('display_state'), 'research_only')
    
    def test_projection_strips_forged_strong(self):
        """Even forged strong with public_enabled=True is stripped."""
        assessment = _make_result('strong', variant=ADJUDICATION_VARIANT)
        assessment['public_enabled'] = True  # Forged
        data = self._make_projection_data(assessment)
        result = public_projection.project_execution(data)
        proj_assessment = result['chart'].get('strength_assessment', {})
        self.assertNotIn('classification', proj_assessment)
    
    def test_projection_without_assessment_unchanged(self):
        """Charts without assessment pass through unchanged."""
        data = self._make_projection_data(None)
        del data['chart']['strength_assessment']
        result = public_projection.project_execution(data)
        self.assertNotIn('strength_assessment', result['chart'])
    
    def test_indeterminate_never_shows_neutral(self):
        """Indeterminate must never be rendered as neutral."""
        assessment = _make_result('indeterminate', variant=ADJUDICATION_VARIANT)
        data = self._make_projection_data(assessment)
        result = public_projection.project_execution(data)
        proj_assessment = result['chart'].get('strength_assessment', {})
        msg = proj_assessment.get('display_message', '')
        self.assertNotIn('中和', msg)


if __name__ == '__main__':
    unittest.main()
