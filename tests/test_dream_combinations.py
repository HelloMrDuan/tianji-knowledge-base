"""Fixed input/evidence expectations; no model or combined dream interpretation."""
import hashlib
from pathlib import Path
import unittest
from unittest.mock import patch

from tianji_kb.knowledge import read_json
from tianji_kb.operations.dream_knowledge import retrieve

ROOT = Path(__file__).resolve().parents[1]


class DreamCombinationTests(unittest.TestCase):
    def test_five_new_scenes_match_only_their_exact_reviewed_cultural_quotes(self):
        cases = [('我梦见我乘龙入水','dragon','乘龙入水有贵位'),
                 ('我梦见一群鱼在水里游','fish','群鱼游水主有财'),
                 ('我梦见我的房屋翻新了','house','屋宅更新主大吉'),
                 ('我梦见我的兄弟互相打架','family','兄弟相打大吉利'),
                 ('我梦见我捡到了钱','money','拾得钱物皆大吉')]
        for text,key,quote in cases:
            with self.subTest(scene=key):
                out=retrieve(text)
                matches=out['matched_interpretations']
                self.assertEqual(len(matches),1)
                match=matches[0]
                self.assertEqual(match['term_id'],'dream.term.'+key)
                self.assertEqual(match['original_text_short_quote'],quote)
                refs=[out['evidence'][eid] for eid in match['evidence_ids']]
                self.assertTrue(any(r['original_text']==quote for r in refs))
                self.assertTrue(all(r['sha256'] and r['commit'] and r['locator'] for r in refs))
                self.assertEqual(match['evidence_level'],'C')
                self.assertFalse(match['personal_prediction'])
                self.assertEqual(out['matched_interpretations'],out['interpretation_candidates'])

    def test_adjacent_snake_chase_then_bite_keeps_entities_actions_and_matches_separate(self):
        text='梦见一条蛇在水里追我，后来咬了我。'
        out=retrieve(text)
        self.assertTrue({'蛇','水'} <= {e['symbol'] for e in out['entities']})
        self.assertEqual([m['term_id'] for m in out['matched_interpretations']],['dream.term.snake'])
        match=out['matched_interpretations'][0]
        self.assertEqual(match['input_matches'][0]['method'],'bounded_adjacent_snake_chase_then_self_bite')
        self.assertEqual([s['text'] for s in match['input_matches'][0]['input_spans']],
                         ['梦见一条蛇在水里追我','后来咬了我'])
        observation=out['narrative_observations'][0]
        self.assertEqual(observation['action'],'being_chased')
        self.assertEqual(observation['status'],'input_observation_only')
        self.assertFalse(observation['reviewed_interpretation_available'])
        self.assertEqual(observation['evidence_ids'],[])
        self.assertNotIn('combined_interpretation',out)
        self.assertFalse(out['ai_enabled'])
        self.assertFalse(out['public_enabled'])

    def test_negative_other_subject_hypothetical_and_reported_context_never_match_self_bite(self):
        for text in ['没有被蛇咬','别人被蛇咬','我害怕会被蛇咬，但没发生',
                     '电影里有人被蛇咬','我梦见别人讲述一个蛇咬人的梦',
                     '梦见小明被蛇咬','我被蛇咬，但没有发生',
                     '电影里有一条蛇追我，后来咬了我',
                     '我听说一条蛇追我，后来咬了我']:
            with self.subTest(text=text):
                out=retrieve(text)
                self.assertEqual(out['matched_interpretations'],[])
                self.assertEqual(out['evidence'],{})
                self.assertEqual(out['narrative_observations'],[])

    def test_unreviewed_symbols_ambiguous_antecedents_and_unrelated_actions_abstain(self):
        for text in ['梦见龙','梦见鱼','梦见我的房子','梦见家人','梦见钱',
                     '梦见一条蛇在水里追我','梦见蛇追我，后来狗咬了我',
                     '梦见蛇和狗追我，后来咬了我','梦见两条蛇追我，后来咬了我',
                     '梦见别人被蛇追，后来咬了我','梦见蛇追我，我走了一段路，后来咬了我',
                     '梦见我没有捡到钱','梦见别人乘龙入水','梦见我的家人吵架']:
            with self.subTest(text=text):
                out=retrieve(text)
                self.assertEqual(out['matched_interpretations'],[])
                self.assertEqual(out['evidence'],{})

    def test_multiple_affirmed_scenes_stay_distinct_and_input_spans_are_exact(self):
        text='我没有被蛇咬，但我梦见我掉进井里，我梦见我捡到了钱。'
        out=retrieve(text)
        self.assertEqual([m['term_id'] for m in out['matched_interpretations']],
                         ['dream.term.falling','dream.term.money'])
        for match in out['matched_interpretations']:
            for hit in match['input_matches']:
                for span in hit['input_spans']:
                    self.assertEqual(text[span['start']:span['end']],span['text'])
            self.assertTrue(match['evidence_ids'])
        self.assertNotIn('combined_interpretation',out)

    def test_new_review_is_traceable_without_promoting_full_book_or_independent_source_grade(self):
        bundle=read_json(ROOT/'data/canonical/dream/phase1_knowledge.json')
        source=next(s for s in read_json(ROOT/'config/knowledge_sources.json')['sources']
                    if s['source_id']=='dream.source.zhougong-scenes')
        self.assertEqual(hashlib.sha256((ROOT/source['content_path']).read_bytes()).hexdigest(),source['sha256'])
        self.assertEqual(source['evidence_level'],'C')
        self.assertEqual(bundle['concepts'][0]['attributes']['independent_source_count'],0)
        self.assertFalse(bundle['concepts'][0]['attributes']['source_independence_confirmed'])
        self.assertEqual(bundle['concepts'][0]['attributes']['raw_sha256'],
                         'd80c42b0b8f44f5b8cf2c4e1c286b200388b65dcd321347eb7ac1011d0be5e97')
        for term in bundle['terms'][5:]:
            comparison=term['attributes']['external_text_comparison']
            self.assertTrue(comparison['short_quote_agrees'])
            self.assertFalse(comparison['independent_edition_confirmed'])
            self.assertIn('oldid=7907671',comparison['url'])

    def test_combination_retrieval_uses_no_raw_body_network_or_model(self):
        original_bytes,original_text=Path.read_bytes,Path.read_text
        def guard(original):
            def read(path,*args,**kwargs):
                if '/data/quarantine/' in path.as_posix() or '/data/raw/' in path.as_posix():
                    raise AssertionError('No source-body access at runtime')
                return original(path,*args,**kwargs)
            return read
        with patch.object(Path,'read_bytes',guard(original_bytes)), \
             patch.object(Path,'read_text',guard(original_text)), \
             patch('socket.create_connection',side_effect=AssertionError('No network/model')):
            out=retrieve('梦见一条蛇在水里追我，后来咬了我')
            self.assertEqual(len(out['matched_interpretations']),1)
            self.assertFalse(out['chart_generated'])


if __name__=='__main__':unittest.main()
