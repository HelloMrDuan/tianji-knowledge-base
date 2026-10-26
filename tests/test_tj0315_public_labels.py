"""TJ-031.5 public labeling contracts (Track C LOW-1 / LOW-2 / LOW-3).

Public-CI safe: pure projection and record-resolution units only —
no FastAPI, no private Canonical data, no sealed runtime. The dream
cases exercise public_source_title, the exact helper the public dream
handler calls to derive a match's source_title from its evidence
records; end-to-end handler coverage with real reviewed records lives
in test_public_dream_culture_api.py (offline acceptance only, because
the public code job intentionally has no FastAPI installed).
"""
import json
import unittest

from tianji_kb.operations.dream_knowledge import public_source_title
from tianji_kb.public_projection import _Aliases, project_evidence, project_execution

JUDGMENT_SCOPE = 'verbatim_classical_hexagram_text_not_a_verdict'


def _project(refs):
    return project_evidence(refs, _Aliases(refs))


class ExcerptFlagTests(unittest.TestCase):
    """LOW-1: truncated citations must be flagged as excerpts."""

    def test_long_text_is_truncated_to_cap_and_flagged(self):
        row = _project({'r1': {'classic_title': '短题',
                               'original_text': '长' * 121,
                               'evidence_level': 'C'}})['E01']
        self.assertEqual(set(row), {'classic_title', 'original_text', 'evidence_level',
                                    'classic_title_excerpt', 'original_text_excerpt'})
        self.assertEqual(len(row['original_text']), 120)
        self.assertIs(row['original_text_excerpt'], True)
        self.assertIs(row['classic_title_excerpt'], False)
        self.assertEqual(row['classic_title'], '短题')

    def test_exactly_at_cap_is_complete_and_unflagged(self):
        row = _project({'r1': {'classic_title': '题' * 120,
                               'original_text': '文' * 120,
                               'evidence_level': 'C'}})['E01']
        self.assertEqual(row['classic_title'], '题' * 120)
        self.assertEqual(row['original_text'], '文' * 120)
        self.assertIs(row['classic_title_excerpt'], False)
        self.assertIs(row['original_text_excerpt'], False)

    def test_long_title_is_flagged_independently_of_text(self):
        row = _project({'r1': {'classic_title': '题' * 121,
                               'original_text': '短文',
                               'evidence_level': 'C'}})['E01']
        self.assertEqual(len(row['classic_title']), 120)
        self.assertIs(row['classic_title_excerpt'], True)
        self.assertIs(row['original_text_excerpt'], False)
        self.assertEqual(row['original_text'], '短文')

    def test_missing_fields_project_empty_and_unflagged(self):
        row = _project({'r1': {}})['E01']
        self.assertEqual(row['classic_title'], '')
        self.assertEqual(row['original_text'], '')
        self.assertIs(row['classic_title_excerpt'], False)
        self.assertIs(row['original_text_excerpt'], False)


def _classic():
    return {'title': '《周易》卦辞与爻辞',
            'source_level': 'L0-public-domain-classic',
            'original': {'number': 1, 'name': '乾为天', 'judgment': '乾：元亨利贞。'},
            'changed': {'number': 2, 'name': '坤为地', 'judgment': '坤：元亨，利牝马之贞。'},
            'scope': 'verbatim_classical_excerpts_only',
            'personal_prediction': False}


class JudgmentScopeTests(unittest.TestCase):
    """LOW-3: the liuyao judgment field keeps its name and verbatim
    text, and gains an explicit scope statement in public projection."""

    def test_domain_execution_shape_is_annotated(self):
        payload = {'domain': 'liuyao', 'chart': {'zhouyi_classic': _classic()},
                   'evidence': {}, 'rule_matches': [], 'trace': []}
        classic = project_execution(payload)['chart']['zhouyi_classic']
        for part in ('original', 'changed'):
            self.assertEqual(classic[part]['judgment_scope'], JUDGMENT_SCOPE)
        self.assertEqual(classic['original']['judgment'], '乾：元亨利贞。')
        self.assertEqual(classic['changed']['judgment'], '坤：元亨，利牝马之贞。')

    def test_scenario_nested_shape_is_annotated(self):
        payload = {'scenario_id': 'question',
                   'result': {'chart': {'zhouyi_classic': _classic()}},
                   'evidence': {}, 'rule_matches': [], 'trace': []}
        classic = project_execution(payload)['result']['chart']['zhouyi_classic']
        self.assertEqual(classic['original']['judgment_scope'], JUDGMENT_SCOPE)
        self.assertEqual(classic['changed']['judgment_scope'], JUDGMENT_SCOPE)

    def test_unrelated_judgment_keys_are_not_annotated(self):
        payload = {'domain': 'bazi', 'chart': {'other': {'judgment': '内部字段'}},
                   'evidence': {}, 'rule_matches': [], 'trace': []}
        self.assertNotIn('judgment_scope', json.dumps(project_execution(payload),
                                                      ensure_ascii=False))


class DreamSourceTitleTests(unittest.TestCase):
    """LOW-2: the public dream source title follows the candidate's own
    evidence records; it is never a fixed label."""

    def test_title_follows_the_referenced_record(self):
        evidence = {'e1': {'classic_title': '甲典·卷一'},
                    'e2': {'classic_title': '乙典·卷二'}}
        self.assertEqual(public_source_title(evidence, {'evidence_ids': ['e1']}), '甲典·卷一')
        self.assertEqual(public_source_title(evidence, {'evidence_ids': ['e2']}), '乙典·卷二')

    def test_record_title_field_variants_are_honored(self):
        evidence = {'e1': {'source_title': '乙典'}, 'e2': {'title': '丙典'}}
        self.assertEqual(public_source_title(evidence, {'evidence_ids': ['e1']}), '乙典')
        self.assertEqual(public_source_title(evidence, {'evidence_ids': ['e2']}), '丙典')

    def test_first_titled_record_wins(self):
        evidence = {'e1': {'original_text': '无题记录'},
                    'e2': {'classic_title': '乙典'}}
        self.assertEqual(public_source_title(evidence, {'evidence_ids': ['e1', 'e2']}), '乙典')

    def test_no_title_anywhere_is_empty_not_invented(self):
        evidence = {'e1': {'original_text': '无题记录'}}
        self.assertEqual(public_source_title(evidence, {'evidence_ids': ['e1']}), '')
        self.assertEqual(public_source_title({}, {'evidence_ids': ['missing']}), '')
        self.assertEqual(public_source_title(evidence, {}), '')
        self.assertEqual(public_source_title(evidence, {'evidence_ids': []}), '')


if __name__ == '__main__':
    unittest.main()
