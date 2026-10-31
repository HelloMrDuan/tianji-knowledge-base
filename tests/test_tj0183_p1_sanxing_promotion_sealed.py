"""TJ-018.3 P1 三刑 Canonical 建节：密封专项。

只在组装后的离线验收环境运行（公开 CI 不执行本文件）：核验密封
Canonical 内《论三刑》建节的真实性与边界——

- 三命通会 classic 只增 source_ids 绑定 bazi.source.sanmingtonghui，
  主 source_id 与 body_stage（quarantine）逐字不变，整书未被标记
  canonical_ready（classic 记录无此字段、bundle 无整书晋级标记）；
- chapter bazi.chapter.sanming_sanxing 与 section bazi.section.s060
  真实建立：s060 文本与正式应用文本 S3《论三刑》整节切片 [71874,74853)
  逐字等值且 PUA 归零（S0 对应切片 [71874,74856) 含 PUA 8 处），018-B 登记引文 11 条全数包含于节文本；
- term bazi.term.branch_punishments 建立且两条 classical 引文均
  绑定 s060 并逐字在节文本内；
- 实体计数：chapters 20->21、sections 59->60、terms 30->31，
  rules 30 与 concepts 18 不变；Phase1 无 r031、Phase2 无任何
  三刑规则（注册未发生，与治理登记 maintained_pending 一致）；
- 概念 bazi.concept.conflict_three_punishments 语义逐字不变
  （status unresolved、executable_policy 阻断、positions 只引
  s020/s021）；
- validate_knowledge 对组装根全量通过（本批新增实体的全部
  schema/来源/引文校验由既有校验器执行）。
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from tianji_kb import bazi_sanming_juan2_sanxing_collation as cj
from tianji_kb.knowledge import validate_knowledge

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_BAZI = ROOT / 'data' / 'canonical' / 'bazi'
SNAPSHOT_DIR = (ROOT / 'data' / 'quarantine' / 'public_domain_snapshots'
                / 'daizhigev20')
S3 = (71874, 74853)


def _bundle():
    return json.loads((CANONICAL_BAZI / 'phase1_knowledge.json')
                      .read_text(encoding='utf-8'))


def _by_id(rows, entity_id):
    found = [r for r in rows if r['id'] == entity_id]
    assert len(found) == 1, entity_id
    return found[0]


class CanonicalBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = _bundle()

    def test_counts(self):
        bundle = self.bundle
        self.assertEqual(len(bundle['classics']), 4)
        # E0335 (TJ-018.3 execution-binding batch 2): +2 chapters
        # and +2 sections for the two juan-2 ganzhi sections
        # (s061/s062) and +3 rules (r032/r033/r034).
        # E0339 (TJ-018.3 B-2): +2 chapters and +2 sections for the
        # juan-3 lu / juan-5 yangren sections (s063/s064), +1 term
        # (bazi.term.luren_route) and +1 rule (r035).
        # E0342 (zaqi promotion): +2 chapters and +3 sections
        # (s065/s066/s067), +1 term (zaqi_selection), +1 rule (r036).
        # E0344 (ren promotion): no new chapters/sections, +1 term
        # (ren_true_pattern), +1 rule (r037).
        # E0346 (governance dayun Sanming-segment promotion): +2
        # chapters and +3 sections (s068/s069/s070), +2 terms
        # (dayun_direction/dayun_handover), +2 rules (r038/r039).
        self.assertEqual(len(bundle['chapters']), 29)
        self.assertEqual(len(bundle['sections']), 70)
        self.assertEqual(len(bundle['terms']), 36)
        # E0333 (TJ-018.3 execution-binding batch 1): +1 rule for
        # bazi.rule.r031 (sanxing structural facts); E0335 adds
        # r032/r033/r034 on top.
        self.assertEqual(len(bundle['rules']), 39)
        self.assertEqual(len(bundle['concepts']), 18)

    def test_classic_binding_only_source_ids_added(self):
        classic = _by_id(self.bundle['classics'],
                         'bazi.classic.sanming_tonghui')
        self.assertEqual(classic['source_id'],
                         'bazi.source.sanming-xianchi-niutrans')
        self.assertEqual(classic['source_ids'],
                         ['bazi.source.sanmingtonghui',
                          'bazi.source.sanmingtonghui-applied'])
        self.assertEqual(classic['body_stage'], 'quarantine')
        self.assertNotIn('canonical_ready', classic)

    def test_chapter_and_section_built_verbatim(self):
        chapter = _by_id(self.bundle['chapters'],
                         'bazi.chapter.sanming_sanxing')
        self.assertEqual(chapter['classic_id'],
                         'bazi.classic.sanming_tonghui')
        section = _by_id(self.bundle['sections'], 'bazi.section.s060')
        self.assertEqual(section['chapter_id'], chapter['id'])
        self.assertEqual(section['classic_id'],
                         'bazi.classic.sanming_tonghui')
        self.assertEqual(section['source_id'],
                         'bazi.source.sanmingtonghui-applied')
        self.assertEqual(section['review']['status'], 'approved')
        # Text basis is the formally applied text S3, not the S0
        # snapshot: the S0 slice carries 8 PUA codepoints and the
        # Canonical layer's cross-domain invariant forbids PUA in
        # any section text; the S3 slice is PUA-free and still
        # contains all 11 registered quotes verbatim.
        s3 = (SNAPSHOT_DIR / 'sanming_tonghui_applied_v1.txt') \
            .read_bytes().decode('utf-8')
        self.assertEqual(section['text'], s3[S3[0]:S3[1]])
        self.assertEqual(len(section['text']), 2979)
        self.assertFalse(any(0xE000 <= ord(c) <= 0xF8FF
                             for c in section['text']))

    def test_all_eleven_quotes_bound_in_section(self):
        section = _by_id(self.bundle['sections'], 'bazi.section.s060')
        self.assertEqual(len(cj.COLLATION_QUOTES), 11)
        for quote in cj.COLLATION_QUOTES:
            self.assertIn(quote['quote'], section['text'], quote['id'])

    def test_term_built_with_refs_into_section(self):
        term = _by_id(self.bundle['terms'],
                      'bazi.term.branch_punishments')
        section = _by_id(self.bundle['sections'], 'bazi.section.s060')
        self.assertEqual(term['definition'],
                         '子卯一刑也寅巳申二刑也丑未戍三刑也')
        self.assertEqual(len(term['source_refs']), 2)
        for ref in term['source_refs']:
            self.assertEqual(ref['section_id'], 'bazi.section.s060')
            self.assertEqual(ref['source_id'],
                             'bazi.source.sanmingtonghui-applied')
            self.assertEqual(ref['role'], 'classical')
            self.assertIn(ref['original_text'], section['text'])


class NoRegistrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = _bundle()

    def test_no_phase1_or_phase2_sanxing_rule(self):
        # Batch transition (E0333, TJ-018.3 execution-binding batch
        # 1): the P1 batch pinned the ABSENCE of any sanxing rule
        # (registration was structurally impossible then). Batch 1
        # registers exactly the pair this test's name denies:
        # Phase1 bazi.rule.r031 (source_refs only into
        # bazi.section.s060) and its Phase2 fact step. The method
        # name is kept for traceability; the pinned posture is now
        # the registered one, and every rule's Phase1 refs must
        # still resolve.
        rule_ids = [r['id'] for r in self.bundle['rules']]
        self.assertIn('bazi.rule.r031', rule_ids)
        r031 = _by_id(self.bundle['rules'], 'bazi.rule.r031')
        self.assertEqual({ref['section_id']
                          for ref in r031['source_refs']},
                         {'bazi.section.s060'})
        phase2 = json.loads((CANONICAL_BAZI / 'phase2_execution.json')
                            .read_text(encoding='utf-8'))
        # E0335: +3 ganzhi strength steps in this file's rules
        # list (32 + 3).
        # E0339: +1 luren route step (35 + 1).
        # E0342: +1 zaqi statement step (36 + 1).
        # E0344: +1 ren true-pattern step (37 + 1).
        # E0346: +2 dayun Sanming steps (38 + 2: classical
        # direction + Sanming conversion).
        self.assertEqual(len(phase2['rules']), 40)
        punish = [r['id'] for r in phase2['rules']
                  if 'punish' in r['id'] or 'sanxing' in r['id']]
        self.assertEqual(punish,
                         ['bazi.phase2.branch_punishment_facts'])
        for rule in phase2['rules']:
            for ref in rule.get('phase1_rule_refs') or []:
                self.assertIn(ref, rule_ids)

    def test_concept_semantics_unchanged(self):
        concept = _by_id(self.bundle['concepts'],
                         'bazi.concept.conflict_three_punishments')
        attrs = concept['attributes']
        self.assertEqual(attrs['status'], 'unresolved')
        self.assertEqual(attrs['executable_policy'],
                         'blocked_pending_school_resolution')
        position_sections = sorted(
            sid for pos in attrs['positions']
            for sid in pos['section_ids'])
        self.assertEqual(position_sections,
                         ['bazi.section.s020', 'bazi.section.s021'])

    def test_validate_knowledge_full_pass(self):
        result = validate_knowledge(ROOT)
        entities = result['entities']
        self.assertIn('bazi.section.s060', entities)
        self.assertIn('bazi.term.branch_punishments', entities)
        self.assertIn('bazi.chapter.sanming_sanxing', entities)


if __name__ == '__main__':
    unittest.main()
