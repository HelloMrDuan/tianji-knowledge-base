"""TJ-019.2 batch 04: five queue themes re-checked against the full RAW.

Batch 03 admitted the only two exact-action entries near the TJ-019.1
queue (death, revival). Batch 04 widened the search surface from the
quarantine candidate set to the complete pinned zhougong RAW (blob
0c7b0823..., sha256 d80c42b0...) and adjudicated every hit for the five
remaining themes (exam / pregnancy / marriage / work / chased):
NO theme has an exact-action original entry, so this batch admits ZERO
new scenes and the reviewed set stays at 12. Full retrieval tables and
per-clause adjudications live in docs/product/DREAM_KNOWLEDGE_BATCH_04.md;
later batches cite that registration instead of re-searching.

These tests pin the conclusion through the real /api/v1/dream/culture
flow plus the research retrieve() surface, using the assembled
production runtime (sealed Canonical + quarantine candidates), like the
other dream suites. Offline acceptance only, NOT public CI.
"""
import json
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from tianji_kb.api import create_app
from tianji_kb.knowledge import validate_knowledge
from tianji_kb.operations.dream_knowledge import retrieve

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = "/api/v1/dream/culture"
CANDIDATES = (ROOT / 'data' / 'quarantine' / 'public_domain_snapshots'
              / 'daizhigev20' / 'zhougong_dream_candidates.json')

# theme -> (candidate id, kept match_scope, queue narrative, topic label)
THEMES = (
    ('exam', 'related_only', '我梦见参加考试', '考试'),
    ('pregnancy', 'related_only', '我梦见自己怀孕了', '怀孕'),
    ('marriage', 'related_only', '我梦见自己结婚了', '结婚'),
    ('work', 'related_only', '我梦见在上班', '工作'),
    ('chased', 'not_found', '我梦见自己被坏人追赶', '被追'),
)


def _labels(out):
    return [t['label'] for t in out['unreviewed_input_topics']]


class Batch04RegistrationTests(unittest.TestCase):
    def test_reviewed_set_stays_at_twelve(self):
        model = validate_knowledge(ROOT)
        bundle = next(b for b in model['bundles'] if b['domain'] == 'dream')
        self.assertEqual(len(bundle['terms']), 12)
        self.assertEqual(len(bundle['rules']), 12)
        concept = next(c for c in bundle['concepts']
                       if c['id'] == 'dream.concept.traditional_variant_v1')
        ids = concept['attributes']['reviewed_term_ids']
        self.assertEqual(len(ids), 12)
        self.assertEqual(ids[-2:], ['dream.term.death', 'dream.term.revival'])

    def test_five_candidates_keep_unreviewed_status(self):
        data = json.loads(CANDIDATES.read_text(encoding='utf-8'))
        self.assertEqual(data['summary']['confirmed_interpretations'], 12)
        by_id = {c['id']: c for c in data['candidates']}
        for cid, scope, _narrative, _label in THEMES:
            with self.subTest(candidate=cid):
                record = by_id[cid]
                self.assertEqual(record['match_scope'], scope)
                self.assertEqual(record['review_status'], 'pending')
                self.assertEqual(record['evidence_level'], 'D')
                self.assertFalse(record['production_allowed'])
                self.assertIsNone(record['interpretation'])


class Batch04ThemeFlowTests(unittest.TestCase):
    def test_each_theme_yields_no_reviewed_interpretation(self):
        for _cid, _scope, narrative, label in THEMES:
            with self.subTest(theme=label):
                out = retrieve(narrative)
                self.assertEqual(out['status'], 'no_reviewed_interpretation')
                self.assertEqual(out['interpretation_candidates'], [])
                self.assertIn(label, _labels(out))
                topic = next(t for t in out['unreviewed_input_topics']
                             if t['label'] == label)
                self.assertEqual(topic['status'], 'input_observation_only')
                self.assertFalse(topic['reviewed_interpretation_available'])
                self.assertEqual(topic['evidence_ids'], [])

    def test_chased_is_input_observation_only(self):
        # The being_chased narrative observation is produced by the
        # existing snake-chase observation path; it never carries an
        # interpretation (batch 04 confirms no chased entry exists).
        out = retrieve('我梦见蛇追我')
        observations = [o for o in out['narrative_observations']
                        if o['action'] == 'being_chased']
        self.assertEqual(len(observations), 1)
        self.assertEqual(observations[0]['status'], 'input_observation_only')
        self.assertFalse(observations[0]['reviewed_interpretation_available'])
        self.assertEqual(observations[0]['evidence_ids'], [])

    def test_omen_position_words_do_not_create_scenes(self):
        # 水流洋洋有新婚: the dreamed scene is flowing water, 新婚 sits in
        # the omen position -- it must not become a marriage interpretation.
        out = retrieve('我梦见水流洋洋')
        self.assertEqual(out['interpretation_candidates'], [])
        self.assertNotIn('结婚', _labels(out))
        # 蛇入怀中生贵子: an unadmitted neighbouring entry; the admitted
        # snake scene is the bite only, and 生贵子 is omen-position.
        out = retrieve('我梦见蛇入怀中')
        self.assertEqual(out['interpretation_candidates'], [])
        self.assertNotIn('怀孕', _labels(out))

    def test_negation_and_third_person_stay_unlabelled(self):
        for text in ('我没有梦见参加考试', '朋友梦见参加考试',
                     '我没有梦见自己怀孕了', '朋友梦见自己结婚了'):
            with self.subTest(text=text):
                out = retrieve(text)
                self.assertEqual(out['status'], 'no_reviewed_interpretation')
                self.assertEqual(out['interpretation_candidates'], [])
                self.assertEqual(out['unreviewed_input_topics'], [])


class Batch04PublicApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(create_app(admin_read_token="<redacted>"))

    def _post(self, text):
        response = self.client.post(PUBLIC, json={"dream_text": text})
        self.assertEqual(response.status_code, 200, response.text)
        return response

    def test_five_themes_through_real_public_flow(self):
        for _cid, _scope, narrative, label in THEMES:
            with self.subTest(theme=label):
                data = self._post(narrative).json()
                self.assertEqual(data['status'], 'no_reviewed_interpretation')
                self.assertEqual(data['matches'], [])
                self.assertEqual([t['label'] for t in data['unreviewed_topics']],
                                 [label])
                self.assertFalse(data['ai_enabled'])
                self.assertFalse(data['personal_prediction'])

    def test_pregnancy_flow_carries_no_medical_or_omen_claim(self):
        response = self._post('我梦见自己怀孕了')
        data = response.json()
        self.assertEqual(data['status'], 'no_reviewed_interpretation')
        # No classical pregnancy omen text may leak into the public flow:
        # the theme stays an input observation with no interpretation.
        for leaked in ('妻有孕', '生贵子', '有贵孕', '孕妇吉'):
            self.assertNotIn(leaked, response.text)
        for key in ('rule_id', 'term_id', 'canonical_path', 'input_spans',
                    'retrieval', 'raw_unicode_offset', 'source_ref'):
            self.assertNotIn(key, response.text)


if __name__ == '__main__':
    unittest.main()
