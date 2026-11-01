"""TJ-018.2 E0352: tiaohou Canonical construction, sealed side.

《穷通宝鉴》 built as the sixth Canonical classic
bazi.classic.qiongtong (body_stage=quarantine): 11 chapters, 110
sections (anchor s075 + entry sections s076-s184 by ascending
entry span; s099 is the adjudicated WINDOW section [8668,8852)
of the Bing-Mao entry whose full span [8668,9025) carries an
unadjudicated hehua proposition in its tail), term
bazi.term.tiaohou, Phase1 rules r042-r051 whose source_refs are
exactly the 120 deduped entry quotes, and the Phase2 step
bazi.phase2.tiaohou_assessment validated by 30 Golden cases
(G1-G6). Design: docs/product/TIAOHOU_CANONICAL_DESIGN.md
(E0350 + section 10 revision E0351).
"""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tianji_kb.bazi_tiaohou import ENTRIES
from tianji_kb.golden import run_cases
from tianji_kb.knowledge import read_json
from tianji_kb.resolver import ROOT as RESOLVER_ROOT
from tianji_kb.resolver import EvidenceResolver

ROOT = Path(__file__).resolve().parents[1]
STEP = 'bazi.phase2.tiaohou_assessment'
RULES = [f'bazi.rule.r{i:03d}' for i in range(42, 52)]
SECTIONS = [f'bazi.section.s{i:03d}' for i in range(75, 185)]
KEYWORDS = ('化气', '合化', '化象', '真化', '化格', '五合')
EXPECT_REFS = {'甲': 13, '乙': 11, '丙': 16, '丁': 13, '戊': 10,
               '己': 6, '庚': 13, '辛': 13, '壬': 12, '癸': 13}
SNAPSHOT = (ROOT / 'data/quarantine/public_domain_snapshots'
            '/daizhigev20/qiongtong_baojian.txt')


class _Bundle:
    """Entity access over the resolver's validated model."""

    def __init__(self, root):
        self.entities = EvidenceResolver(root).entities


def _bundle():
    return _Bundle(RESOLVER_ROOT)


def _entity(bundle, entity_id):
    kind, entity = bundle.entities[entity_id]
    return entity


class RegistrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = _bundle()
        cls.text = SNAPSHOT.read_text('utf-8')

    def test_classic_chapters_sections(self):
        bundle = self.bundle
        classic = _entity(bundle, 'bazi.classic.qiongtong')
        self.assertEqual(classic['source_id'],
                         'bazi.source.qiongtong')
        self.assertEqual(classic['body_stage'], 'quarantine')
        self.assertEqual(classic['name'], '《穷通宝鉴》')
        chapters = [e for k, e in bundle.entities.values()
                    if k == 'chapters'
                    and e['classic_id'] == 'bazi.classic.qiongtong']
        self.assertEqual(len(chapters), 11)
        sections = [e for k, e in bundle.entities.values()
                    if k == 'sections'
                    and e['classic_id'] == 'bazi.classic.qiongtong']
        self.assertEqual(sorted(e['id'] for e in sections),
                         SECTIONS)
        # Bazi bundle totals after the flip.
        knowledge = read_json(
            ROOT / 'data/canonical/bazi/phase1_knowledge.json')
        self.assertEqual(len(knowledge['classics']), 6)
        self.assertEqual(len(knowledge['chapters']), 44)
        self.assertEqual(len(knowledge['sections']), 184)
        self.assertEqual(len(knowledge['terms']), 39)
        self.assertEqual(len(knowledge['rules']), 51)

    def test_section_texts_are_verbatim_slices(self):
        text = self.text
        spans = sorted({(e['section']['char_start'],
                         e['section']['char_end']) for e in ENTRIES})
        self.assertEqual(len(spans), 109)
        expect = {}
        for i, span in enumerate(spans):
            sid = f'bazi.section.s{76 + i:03d}'
            if span == (8668, 9025):
                self.assertEqual(sid, 'bazi.section.s099')
                expect[sid] = text[8668:8852]
            else:
                expect[sid] = text[span[0]:span[1]]
        expect['bazi.section.s075'] = text[6:517]
        for sid, want in expect.items():
            section = _entity(self.bundle, sid)
            self.assertEqual(section['text'], want, sid)
            self.assertEqual(section['review']['status'],
                             'approved', sid)

    def test_window_section_record(self):
        s099 = _entity(self.bundle, 'bazi.section.s099')
        self.assertEqual(s099['name'], '穷通宝鉴·丙火二月条（窗口节）')
        self.assertIn('[8668,8852)', s099['locator'])
        self.assertIn('[8668,9025)', s099['locator'])
        self.assertIn('窗口', s099['review']['scope'])
        self.assertIn('[8853,9025)', s099['review']['scope'])
        # The excluded tail is not any section's text and does
        # carry the barred keyword (the reason for the window).
        excluded = self.text[8853:9025]
        self.assertIn('化格', excluded)
        for kind, entity in self.bundle.entities.values():
            if kind == 'sections' and entity['domain'] == 'bazi':
                self.assertNotEqual(entity['text'], excluded)

    def test_no_hehua_keywords_or_marks(self):
        for sid in SECTIONS:
            section = _entity(self.bundle, sid)
            for kw in KEYWORDS:
                self.assertNotIn(kw, section['text'], (sid, kw))
                self.assertNotIn(kw, section['name'], (sid, kw))
            self.assertNotIn('□', section['text'], sid)
            self.assertFalse(
                any('\ue000' <= ch <= '\uf8ff'
                    for ch in section['text']), sid)

    def test_term_anchor(self):
        term = _entity(self.bundle, 'bazi.term.tiaohou')
        self.assertEqual(term['name'], '调候')
        self.assertEqual(len(term['source_refs']), 1)
        ref = term['source_refs'][0]
        self.assertEqual(ref['section_id'], 'bazi.section.s075')
        self.assertEqual(ref['original_text'], self.text[33:98])
        self.assertEqual(ref['role'], 'classical')

    def test_rules_refs_exactly_the_entry_quotes(self):
        # Independent recomputation of the design section 4.2
        # exactness rule (plus the section 10.5 Ding merge).
        expect = {}
        for stem in '甲乙丙丁戊己庚辛壬癸':
            main, branch = {}, {}
            for e in ENTRIES:
                if e['day_master'] != stem:
                    continue
                span = (e['section']['char_start'],
                        e['section']['char_end'])
                main[(span, e['quote_locator']['char_start'])] = (
                    e['source_section_id'], e['quote'])
                for b in e['branches']:
                    loc = b['locator']['char_start']
                    if stem == '丁' and loc == 13510:
                        shared = next(
                            x for x in ENTRIES
                            if (x['section']['char_start'],
                                x['section']['char_end'])
                            == (13476, 13592))
                        branch[(b['quote'], loc)] = (
                            shared['source_section_id'], b['quote'])
                    else:
                        branch[(b['quote'], loc)] = (
                            e['source_section_id'], b['quote'])
            expect[stem] = ({v for v in main.values()}
                            | {v for v in branch.values()})
        total = 0
        for i, stem in enumerate('甲乙丙丁戊己庚辛壬癸'):
            rule = _entity(self.bundle, RULES[i])
            got = {(r['section_id'], r['original_text'])
                   for r in rule['source_refs']}
            self.assertEqual(got, expect[stem], stem)
            self.assertEqual(len(rule['source_refs']),
                             EXPECT_REFS[stem], stem)
            total += len(rule['source_refs'])
            self.assertTrue(all(
                r['role'] == 'classical'
                and r['source_id'] == 'bazi.source.qiongtong'
                for r in rule['source_refs']))
            self.assertEqual(rule['school'], '子平·穷通宝鉴（调候）')
            self.assertEqual(rule['execution_status'],
                             'executable')
            self.assertEqual(rule['term_refs'],
                             ['bazi.term.tiaohou'])
        self.assertEqual(total, 120)

    def test_step_registration(self):
        contract = read_json(
            ROOT / 'data/canonical/bazi/phase2_execution.json')
        step = next(r for r in contract['rules'] if r['id'] == STEP)
        self.assertEqual(step['phase1_rule_refs'], RULES)
        self.assertEqual(step['validation_status'], 'validated')
        self.assertEqual(step['execution_status'], 'executable')
        self.assertEqual(step['regression_test'],
                         'tests/test_phase2_bazitiaohou.py')
        self.assertEqual(len(step['golden_case_ids']), 30)

    def test_exhaustive_entry_binding(self):
        # All 119 main quotes and all 10 encoded branch quotes
        # are substrings of their bound section's text.
        for e in ENTRIES:
            section = _entity(self.bundle, e['source_section_id'])
            self.assertIn(e['quote'], section['text'],
                          (e['day_master'], e['month_branch']))
            for b in e['branches']:
                self.assertIn(b['quote'], section['text'],
                              (e['day_master'], e['month_branch'],
                               b['id']))


class GoldenFireTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.passed = {c['id']: c for c in run_cases(ROOT)}
        cls.golden = read_json(
            ROOT / 'data/canonical/bazi/phase2_golden.json')
        cls.cases = {c['id']: c for c in cls.golden['cases']
                     if c['id'].startswith('bazi.tiaohou-')}

    def test_all_cases_fire_the_step(self):
        self.assertEqual(len(self.cases), 30)
        for cid, case in self.cases.items():
            self.assertIn(cid, self.passed, cid)
            self.assertIn(STEP, self.passed[cid]['rule_ids'], cid)
            self.assertEqual(
                case['input']['tiaohou_variant'],
                'tiaohou-qiongtong-v1')

    def test_g1_to_g6_coverage(self):
        branch_pol = {}
        stems, presence, shared = set(), set(), set()
        spanmap = {}
        for e in ENTRIES:
            spanmap.setdefault(
                (e['section']['char_start'],
                 e['section']['char_end']), []).append(
                     (e['day_master'], e['month_branch']))
        shared_keys = {k for ks in spanmap.values() if len(ks) > 1
                       for k in ks}
        empty_seq = {('丙', '亥'), ('丁', '午'), ('癸', '午')}
        seen_empty = set()
        for case in self.cases.values():
            inp, exp = case['input'], case['expected'][
                'tiaohou_assessment']
            key = (inp['day_ganzhi'][0], inp['month_ganzhi'][1])
            stems.add(key[0])
            if key in shared_keys:
                shared.add(key)
            if key in empty_seq and exp['status'] == 'matched':
                seen_empty.add(key)
            for s in exp.get('sequence', []):
                presence.add(s['presence'])
            for b in exp.get('branches', []):
                branch_pol.setdefault(
                    (key[0], key[1], b['id']), set()).add(
                        b['applied'])
        # G1: every encoded branch, both polarities.
        for e in ENTRIES:
            for b in e['branches']:
                self.assertEqual(
                    branch_pol.get((e['day_master'],
                                    e['month_branch'], b['id'])),
                    {True, False}, b['id'])
        # G2: the absent grid cell fires the step, not_applicable.
        g2 = [c for c in self.cases.values()
              if c['input']['day_ganzhi'][0] == '乙'
              and c['input']['month_ganzhi'][1] == '丑']
        self.assertEqual(len(g2), 1)
        self.assertEqual(g2[0]['expected']['tiaohou_assessment']
                         ['status'], 'not_applicable')
        self.assertEqual(g2[0]['expected']['tiaohou_assessment']
                         ['reason'], 'entry_absent_in_source')
        # G3: all three empty-sequence entries.
        self.assertEqual(seen_empty, empty_seq)
        # G4: all seven shared spans hit.
        hit_spans = {span for span, ks in spanmap.items()
                     if len(ks) > 1 and any(k in shared for k in ks)}
        self.assertEqual(len(hit_spans), 7)
        # G5: all ten stems. G6: all three presence states.
        self.assertEqual(stems, set('甲乙丙丁戊己庚辛壬癸'))
        self.assertEqual(presence, {'visible', 'hidden', 'absent'})


class ForgedNegativeTests(unittest.TestCase):
    """Four forgery classes, each rejected by EvidenceResolver
    (design section 7 item 5 as revised)."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp())
        for sub in ('config', 'schemas'):
            shutil.copytree(ROOT / sub, cls.tmp / sub)
        shutil.copytree(ROOT / 'data', cls.tmp / 'data')
        cls.phase1 = (cls.tmp / 'data/canonical/bazi'
                      '/phase1_knowledge.json')
        cls.pristine = cls.phase1.read_bytes()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def _rejects(self, mutator):
        data = json.loads(self.pristine.decode('utf-8'))
        mutator(data)
        self.phase1.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding='utf-8')
        try:
            with self.assertRaises(ValueError):
                EvidenceResolver(self.tmp, review_sources=True)
        finally:
            self.phase1.write_bytes(self.pristine)

    def test_entry_quote_altered(self):
        def mutate(data):
            rule = next(r for r in data['rules']
                        if r['id'] == 'bazi.rule.r042')
            ref = rule['source_refs'][0]
            ref['original_text'] = ('改' + ref['original_text'][1:])
        self._rejects(mutate)

    def test_ref_rebound_to_other_stem_section(self):
        def mutate(data):
            rule = next(r for r in data['rules']
                        if r['id'] == 'bazi.rule.r042')
            other = next(r for r in data['rules']
                         if r['id'] == 'bazi.rule.r043')
            rule['source_refs'][0]['section_id'] = (
                other['source_refs'][0]['section_id'])
        self._rejects(mutate)

    def test_branch_quote_posing_as_main(self):
        def mutate(data):
            jia = next(e for e in ENTRIES
                       if e['day_master'] == '甲'
                       and e['month_branch'] == '午')
            branch_quote = jia['branches'][0]['quote']
            rule = next(r for r in data['rules']
                        if r['id'] == 'bazi.rule.r042')
            first = rule['source_refs'][0]
            self.assertNotEqual(first['section_id'],
                                jia['source_section_id'])
            first['original_text'] = branch_quote
        self._rejects(mutate)

    def test_anchor_quote_altered(self):
        def mutate(data):
            term = next(t for t in data['terms']
                        if t['id'] == 'bazi.term.tiaohou')
            ref = term['source_refs'][0]
            ref['original_text'] = ('改' + ref['original_text'][1:])
        self._rejects(mutate)


if __name__ == '__main__':
    unittest.main()
