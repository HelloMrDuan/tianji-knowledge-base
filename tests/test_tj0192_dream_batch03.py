"""TJ-019.2 batch 03: two narrow dream scenes admitted verbatim.

见人死自死皆吉 (death candidate, direct_scene) and 死人复活主有信
(deceased candidate's own exact entry — admitted as the scene 死人复活,
NOT as a 故人 interpretation) join the reviewed set: 10 -> 12 scenes.
Golden runs the real /api/v1/dream/culture flow plus the research
retrieve() surface. Per WBS TJ-019.2 each admitted scene carries >=2
semantic positives, >=2 wrong-theme counterexamples and >=2
negation/third-person abstentions. Requires the assembled production
runtime (sealed Canonical), like the other dream suites.
"""
import unittest

from fastapi.testclient import TestClient

from tianji_kb.api import create_app
from tianji_kb.knowledge import validate_knowledge
from tianji_kb.operations.dream_knowledge import retrieve
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = "/api/v1/dream/culture"

DEATH = 'dream.term.death'
REVIVAL = 'dream.term.revival'


def _term_ids(out):
    return [c['term_id'] for c in out['interpretation_candidates']]


class Batch03AdmissionTests(unittest.TestCase):
    def test_reviewed_set_grows_from_ten_to_twelve(self):
        model = validate_knowledge(ROOT)
        bundle = next(b for b in model['bundles'] if b['domain'] == 'dream')
        self.assertEqual(len(bundle['terms']), 12)
        self.assertEqual(len(bundle['rules']), 12)
        concept = next(c for c in bundle['concepts']
                       if c['id'] == 'dream.concept.traditional_variant_v1')
        ids = concept['attributes']['reviewed_term_ids']
        self.assertEqual(len(ids), 12)
        self.assertEqual(ids[-2:], [DEATH, REVIVAL])
        self.assertEqual(bundle['classics'][0]['body_stage'], 'quarantine')

    def test_death_positives_hit_exact_quote_with_c_evidence(self):
        for text in ('我梦见自己死了', '我梦见看见一个路人死了', '我梦见见人死', '梦见我死亡'):
            with self.subTest(text=text):
                out = retrieve(text)
                self.assertEqual(_term_ids(out), [DEATH])
                candidate = out['interpretation_candidates'][0]
                self.assertEqual(candidate['original_text_short_quote'], '见人死自死皆吉')
                self.assertEqual(candidate['scene'], '见人死自死')
                self.assertEqual(candidate['evidence_level'], 'C')
                self.assertFalse(candidate['personal_prediction'])
                refs = [out['evidence'][eid] for eid in candidate['evidence_ids']]
                self.assertTrue(any(r['original_text'] == '见人死自死皆吉' for r in refs))
                self.assertTrue(all(r['commit'] and r['sha256'] and r['locator'] for r in refs))
                # The theme is reviewed now: no unreviewed 死亡 topic remains.
                self.assertNotIn('死亡', [t['label'] for t in out['unreviewed_input_topics']])

    def test_death_counterexamples_do_not_match(self):
        # Wrong themes: a neighbouring unadmitted entry (子死者), the
        # deceased-person theme without a death of self/witnessed stranger,
        # and the revival scene (a different admitted entry).
        for text, expected in (('我梦见儿子死了', []),
                               ('我梦见爷爷去世了', []),
                               ('我梦见死人复活了', [REVIVAL])):
            with self.subTest(text=text):
                self.assertEqual(_term_ids(retrieve(text)), expected)

    def test_death_abstains_on_negation_hypothetical_and_third_person(self):
        for text in ('我没有梦见自己死了', '如果我梦见自己死了', '朋友梦见自己死了'):
            with self.subTest(text=text):
                out = retrieve(text)
                self.assertEqual(out['status'], 'no_reviewed_interpretation')
                self.assertEqual(out['interpretation_candidates'], [])

    def test_revival_positives_hit_exact_quote_with_c_evidence(self):
        for text in ('我梦见死人复活了', '我梦见去世的爷爷复活了'):
            with self.subTest(text=text):
                out = retrieve(text)
                self.assertEqual(_term_ids(out), [REVIVAL])
                candidate = out['interpretation_candidates'][0]
                self.assertEqual(candidate['original_text_short_quote'], '死人复活主有信')
                self.assertEqual(candidate['scene'], '死人复活')
                self.assertEqual(candidate['evidence_level'], 'C')
                self.assertFalse(candidate['personal_prediction'])
                refs = [out['evidence'][eid] for eid in candidate['evidence_ids']]
                self.assertTrue(any(r['original_text'] == '死人复活主有信' for r in refs))
                self.assertTrue(all(r['commit'] and r['sha256'] and r['locator'] for r in refs))

    def test_revival_counterexamples_do_not_fill_the_deceased_theme_gap(self):
        # 梦见故人 without revival stays an unreviewed input topic: this
        # admission deliberately does NOT interpret 故人 dreams.
        out = retrieve('我梦见已故的亲人')
        self.assertEqual(out['status'], 'no_reviewed_interpretation')
        self.assertEqual([t['label'] for t in out['unreviewed_input_topics']], ['故人'])
        # Neighbouring entry 死人哭泣 is not admitted either.
        out = retrieve('我梦见死人哭泣')
        self.assertEqual(out['status'], 'no_reviewed_interpretation')
        self.assertEqual(out['interpretation_candidates'], [])

    def test_revival_abstains_on_negation_reported_and_third_person(self):
        for text in ('我没有梦见死人复活', '听说有人梦见死人复活', '朋友梦见死人复活了'):
            with self.subTest(text=text):
                out = retrieve(text)
                self.assertEqual(out['status'], 'no_reviewed_interpretation')
                self.assertEqual(out['interpretation_candidates'], [])


class Batch03PublicApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(create_app(admin_read_token="<redacted>"))

    def _post(self, text):
        response = self.client.post(PUBLIC, json={"dream_text": text})
        self.assertEqual(response.status_code, 200, response.text)
        return response

    def test_death_scene_through_real_public_flow(self):
        response = self._post('我梦见自己死了')
        data = response.json()
        self.assertEqual(data['status'], 'reviewed_cultural_matches')
        self.assertEqual(len(data['matches']), 1)
        match = data['matches'][0]
        self.assertEqual(match['scene'], '见人死自死')
        self.assertEqual(match['short_quote'], '见人死自死皆吉')
        self.assertEqual(match['evidence_level'], 'C')
        self.assertEqual(data['unreviewed_topics'], [])
        self.assertFalse(data['ai_enabled'])
        self.assertFalse(data['personal_prediction'])
        for key in ('rule_id', 'term_id', 'canonical_path', 'input_spans', 'retrieval',
                    'raw_unicode_offset', 'source_ref'):
            self.assertNotIn(key, response.text)

    def test_revival_scene_through_real_public_flow(self):
        response = self._post('我梦见去世的爷爷复活了')
        data = response.json()
        self.assertEqual(data['status'], 'reviewed_cultural_matches')
        self.assertEqual(len(data['matches']), 1)
        self.assertEqual(data['matches'][0]['short_quote'], '死人复活主有信')
        self.assertEqual(data['matches'][0]['scene'], '死人复活')

    def test_abstentions_and_deceased_gap_through_real_public_flow(self):
        for text in ('朋友梦见死人复活了', '我没有梦见自己死了'):
            with self.subTest(text=text):
                data = self._post(text).json()
                self.assertEqual(data['status'], 'no_reviewed_interpretation')
                self.assertEqual(data['matches'], [])
                self.assertEqual(data['unreviewed_topics'], [])
        data = self._post('我梦见已故的亲人').json()
        self.assertEqual(data['status'], 'no_reviewed_interpretation')
        self.assertEqual(data['matches'], [])
        self.assertEqual([t['label'] for t in data['unreviewed_topics']], ['故人'])


if __name__ == '__main__':
    unittest.main()
