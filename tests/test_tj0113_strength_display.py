"""TJ-011.3: Tests for bazi strength display boundary policy.

Verifies that:
- Research-only results are never displayed publicly
- indeterminate is never misread as neutral/weak/strong
- Out-of-scope inputs get proper messaging
- Conflicts are properly reported
- The server is authoritative (no client bypass)
"""
import unittest

from src.tianji_kb.bazi_strength_display import (
    get_display_decision,
    check_scope_by_inputs,
    format_indeterminate_explanation,
    MSG_INSUFFICIENT,
    MSG_CONFLICT,
    MSG_OUT_OF_SCOPE,
    MSG_RESEARCH_ONLY,
    MSG_ERROR,
)


def _make_result(classification='indeterminate', research_only=True,
                 public_enabled=False, blockers=None):
    """Create a mock adjudication result."""
    return {
        'classification': classification,
        'research_only': research_only,
        'public_enabled': public_enabled,
        'ai_enabled': False,
        'blockers': blockers or [],
    }


class DisplayPolicyTests(unittest.TestCase):
    def test_research_only_strong_not_displayed(self):
        """Research-only 'strong' must not be shown publicly."""
        result = _make_result('strong', research_only=True, public_enabled=False)
        decision = get_display_decision(result)
        self.assertFalse(decision['may_display_classification'])
        self.assertEqual(decision['display_state'], 'research_only')
        self.assertEqual(decision['user_message'], MSG_RESEARCH_ONLY)

    def test_research_only_weak_not_displayed(self):
        """Research-only 'weak' must not be shown publicly."""
        result = _make_result('weak', research_only=True, public_enabled=False)
        decision = get_display_decision(result)
        self.assertFalse(decision['may_display_classification'])
        self.assertEqual(decision['display_state'], 'research_only')

    def test_research_only_indeterminate_not_misread(self):
        """Indeterminate must not be misread as neutral or weak."""
        result = _make_result('indeterminate', research_only=True, public_enabled=False)
        decision = get_display_decision(result)
        self.assertFalse(decision['may_display_classification'])
        # Must not imply neutral ('中和') or weak
        self.assertNotIn('中和', decision['user_message'])
        self.assertNotIn('身弱', decision['user_message'])
        self.assertNotIn('身强', decision['user_message'])

    def test_conflict_takes_precedence(self):
        """Conflicts must be reported, not hidden."""
        result = _make_result(
            'indeterminate', research_only=True, public_enabled=False,
            blockers=[{'reason': 'test_conflict'}]
        )
        decision = get_display_decision(result)
        self.assertEqual(decision['display_state'], 'conflict')
        self.assertEqual(decision['user_message'], MSG_CONFLICT)
        self.assertFalse(decision['may_display_classification'])

    def test_none_result_is_error(self):
        """Missing result is an error, not indeterminate."""
        decision = get_display_decision(None)
        self.assertEqual(decision['display_state'], 'error')
        self.assertEqual(decision['user_message'], MSG_ERROR)
        self.assertFalse(decision['may_display_classification'])

    def test_public_enabled_strong_may_display(self):
        """Publicly authorized strong results may be displayed."""
        result = _make_result('strong', research_only=False, public_enabled=True)
        decision = get_display_decision(result)
        self.assertTrue(decision['may_display_classification'])
        self.assertEqual(decision['classification'], 'strong')
        self.assertEqual(decision['display_state'], 'public_result')

    def test_public_enabled_indeterminate_not_shown_as_result(self):
        """Public indeterminate must show insufficient message, not a verdict."""
        result = _make_result('indeterminate', research_only=False, public_enabled=True)
        decision = get_display_decision(result)
        self.assertFalse(decision['may_display_classification'])
        self.assertEqual(decision['display_state'], 'insufficient')
        self.assertEqual(decision['user_message'], MSG_INSUFFICIENT)

    def test_out_of_scope_day_master(self):
        """Non-wood day masters are out of scope."""
        for dm in ['丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']:
            decision = check_scope_by_inputs(dm, '卯')
            self.assertIsNotNone(decision)
            self.assertEqual(decision['display_state'], 'out_of_scope')
            self.assertEqual(decision['user_message'], MSG_OUT_OF_SCOPE)
            self.assertFalse(decision['may_display_classification'])

    def test_out_of_scope_month(self):
        """Months other than 卯/酉 are out of scope."""
        for mb in ['寅', '辰', '巳', '午', '未', '申', '戌', '亥', '子', '丑']:
            decision = check_scope_by_inputs('甲', mb)
            self.assertIsNotNone(decision)
            self.assertEqual(decision['display_state'], 'out_of_scope')

    def test_in_scope_inputs(self):
        """Wood day masters with 卯/酉 months are in scope."""
        for dm in ['甲', '乙']:
            for mb in ['卯', '酉']:
                decision = check_scope_by_inputs(dm, mb)
                self.assertIsNone(decision)

    def test_indeterminate_explanation_never_neutral(self):
        """Indeterminate explanation must never say neutral."""
        result = _make_result('indeterminate')
        explanation = format_indeterminate_explanation(result)
        self.assertNotIn('中和', explanation)
        # Should be insufficient or conflict message
        self.assertIn(explanation, [MSG_INSUFFICIENT, MSG_CONFLICT])

    def test_indeterminate_with_blockers_shows_conflict(self):
        """Indeterminate with blockers explains conflict."""
        result = _make_result('indeterminate', blockers=[{'reason': 'x'}])
        explanation = format_indeterminate_explanation(result)
        self.assertEqual(explanation, MSG_CONFLICT)


if __name__ == '__main__':
    unittest.main()
