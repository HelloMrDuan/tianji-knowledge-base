"""TJ-012.3《子平真詮》准入＋Ch16 平行登记：密封专项。

只在组装后的离线验收环境运行（公开 CI 不执行本文件）：核验密封
Canonical 内 Ch16 建节的真实性与边界——

- 新 classic bazi.classic.zipingzhenquan、新章
  bazi.chapter.ziping_zaqi 与新节 bazi.section.s185 真实建立：
  s185 文本与密封 TXT 正文逐字等值（821 字、零 PUA），20 条核取
  短引全数包含于节文本且各在 TXT 中恰出现一次，locator 逐字
  复核（短引彼此不连续，公开覆盖约三成）；
- 实体计数：classics 6->7、chapters 44->45、sections 184->185，
  terms 39、rules 51、concepts 18 不变；Phase1 无 Ch16 规则、
  Phase2 无任何 ziping 步（注册未发生，与治理登记
  maintained_pending 一致）；
- 密封 TXT 的 SHA256／字节数／字符数与登记钉值一致；来源普查
  103 条（C:97／D:6）；
- validate_knowledge 对组装根全量通过（本批新增实体的全部
  schema／来源／引文校验由既有校验器执行）。
"""
import hashlib
import json
import unittest
from pathlib import Path

from tianji_kb import bazi_ziping_zaqi as zp
from tianji_kb.knowledge import validate_knowledge

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_BAZI = ROOT / 'data' / 'canonical' / 'bazi'
SNAPSHOT_DIR = (ROOT / 'data' / 'quarantine' / 'public_domain_snapshots'
                / 'nlc416')
GOLDEN = json.loads(
    (ROOT / 'tests' / 'golden_tj0123_ziping_zaqi.json').read_text('utf-8'))


def _bundle():
    return json.loads((CANONICAL_BAZI / 'phase1_knowledge.json')
                      .read_text(encoding='utf-8'))


def _by_id(rows, entity_id):
    found = [r for r in rows if r['id'] == entity_id]
    assert len(found) == 1, entity_id
    return found[0]


def _txt_body():
    raw = (SNAPSHOT_DIR / 'zipingzhenquan_1925_ch16.txt').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == zp.ZIPING_TXT_SHA256
    assert len(raw) == zp.ZIPING_TXT_BYTES
    text = raw.decode('utf-8')
    assert text.endswith('\n') and text.count('\n') == 1
    body = text[:-1]
    assert len(body) == zp.ZIPING_TXT_CHARS
    assert not any(0xE000 <= ord(c) <= 0xF8FF for c in body)
    return body


class CanonicalBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = _bundle()
        cls.body = _txt_body()

    def test_counts(self):
        bundle = self.bundle
        # E0382 (TJ-012.3《子平真詮》准入＋Ch16 平行登记): +1 classic
        # (bazi.classic.zipingzhenquan), +1 chapter
        # (bazi.chapter.ziping_zaqi), +1 section (bazi.section.s185);
        # no new terms, rules or concepts.
        self.assertEqual(len(bundle['classics']), 7)
        self.assertEqual(len(bundle['chapters']), 45)
        self.assertEqual(len(bundle['sections']), 185)
        self.assertEqual(len(bundle['terms']), 39)
        self.assertEqual(len(bundle['rules']), 51)
        self.assertEqual(len(bundle['concepts']), 18)

    def test_classic_chapter_section_built_verbatim(self):
        classic = _by_id(self.bundle['classics'],
                         'bazi.classic.zipingzhenquan')
        self.assertEqual(classic['source_id'], 'bazi.source.zipingzhenquan')
        self.assertEqual(classic['body_stage'], 'quarantine')
        chapter = _by_id(self.bundle['chapters'],
                         'bazi.chapter.ziping_zaqi')
        self.assertEqual(chapter['classic_id'],
                         'bazi.classic.zipingzhenquan')
        section = _by_id(self.bundle['sections'], 'bazi.section.s185')
        self.assertEqual(section['chapter_id'], chapter['id'])
        self.assertEqual(section['classic_id'],
                         'bazi.classic.zipingzhenquan')
        self.assertEqual(section['source_id'],
                         'bazi.source.zipingzhenquan')
        self.assertEqual(section['review']['status'], 'approved')
        self.assertIn('evidence_binding', section['review']['scope'])
        self.assertIn('pending', section['review']['scope'])
        # Section text is byte-identical to the TXT body.
        self.assertEqual(section['text'], self.body)
        self.assertEqual(len(section['text']), 821)

    def test_all_twenty_quotes_bound_in_section(self):
        section = _by_id(self.bundle['sections'], 'bazi.section.s185')
        self.assertEqual(len(zp.ZIPING_ZAQI_QUOTES), 20)
        for quote in zp.ZIPING_ZAQI_QUOTES:
            loc = quote['locator']
            self.assertEqual(
                self.body[loc['char_start']:loc['char_end']],
                quote['quote'], quote['id'])
            self.assertEqual(section['text'].count(quote['quote']), 1,
                             quote['id'])
            self.assertEqual(self.body.count(quote['quote']), 1,
                             quote['id'])
            self.assertFalse(
                any(0xE000 <= ord(c) <= 0xF8FF for c in quote['quote']),
                'no PUA may sit inside a registered quote window')

    def test_census(self):
        sources = json.loads((ROOT / 'config' / 'knowledge_sources.json')
                             .read_text(encoding='utf-8'))['sources']
        # TJ-012.3《子平真詮》准入普查同步：登记
        # bazi.source.zipingzhenquan（C 级）后登记表 102→103 条、
        # C:96→C:97，非放宽断言。
        self.assertEqual(len(sources), 103)
        from collections import Counter
        self.assertEqual(
            Counter(s['evidence_level'] for s in sources),
            Counter({'C': 97, 'D': 6}))


class PublicNonReconstructabilityTests(unittest.TestCase):
    """Public files must not jointly reconstruct the sealed chapter.

    Scans the public files present in the assembled backend that may
    name the chapter for maximal
    verbatim substrings (length >= 4) of the sealed TXT body and
    asserts the union stays small, short-run and gapped: no single
    file holds a verbatim span of 25 chars or more, and the full
    body appears in no file. The scan reads the registered kernels
    only through zp / Golden data -- no long chapter string is
    written as a literal anywhere in this file.
    """

    PUBLIC_FILES = (
        'src/tianji_kb/bazi_ziping_zaqi.py',
        'src/tianji_kb/bazi_registration_governance.py',
        'tests/golden_tj0123_ziping_zaqi.json',
        'tests/test_tj0123_ziping_zaqi_public.py',
        'tests/test_tj0123_ziping_zaqi_sealed.py',
        'docs/product/TJ0123_ZIPING_ZHENQUAN_ADMISSION.md',
        'config/knowledge_sources.json',
        'config/phase2_source_audit.json',
        'docs/product/DETAILED_DELIVERY_BACKLOG_V1.md',
        'docs/COVERAGE.md',
        # NOTE: .github/workflows/validate.yml is NOT listed: the
        # assembled backend contains no .github/ directory, so the
        # file cannot be scanned here. It carries no chapter text
        # (longest verbatim span 2 chars, verified by the full
        # 70-file scan in the remediation record).
        'tests/test_knowledge.py',
    )

    @classmethod
    def setUpClass(cls):
        cls.body = _txt_body()

    @staticmethod
    def _longest_at(body, text, start):
        # Longest prefix of body[start:] present in text. Presence
        # is monotone in length, so binary search is exact.
        lo, hi = 0, len(body) - start
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if body[start:start + mid] in text:
                lo = mid
            else:
                hi = mid - 1
        return lo

    def test_public_files_do_not_reconstruct_chapter(self):
        body = self.body
        union = bytearray(len(body))
        for rel in self.PUBLIC_FILES:
            path = ROOT / rel
            self.assertTrue(path.is_file(), rel)
            text = path.read_text(encoding='utf-8')
            self.assertNotIn(body, text, rel)
            longest = 0
            for i in range(len(body)):
                span = self._longest_at(body, text, i)
                longest = max(longest, span)
                if span >= 4:
                    union[i:i + span] = b'\x01' * span
            self.assertLessEqual(longest, 24, rel)
        total = sum(union)
        self.assertLessEqual(total, 320)
        runs = []
        i = 0
        while i < len(union):
            if union[i]:
                j = i
                while j < len(union) and union[j]:
                    j += 1
                runs.append((i, j))
                i = j
            else:
                i += 1
        self.assertLessEqual(max(e - s for s, e in runs), 24)
        self.assertGreaterEqual(len(runs), 20)


class NoRegistrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = _bundle()

    def test_no_phase1_or_phase2_ziping_rule(self):
        rule_ids = [r['id'] for r in self.bundle['rules']]
        self.assertEqual(len(rule_ids), 51)
        self.assertFalse(any('ziping' in r for r in rule_ids))
        for rule in self.bundle['rules']:
            for ref in rule.get('source_refs') or []:
                self.assertNotEqual(ref.get('section_id'),
                                    'bazi.section.s185')
        phase2 = json.loads((CANONICAL_BAZI / 'phase2_execution.json')
                            .read_text(encoding='utf-8'))
        self.assertEqual(len(phase2['rules']), 43)
        self.assertFalse(any('ziping' in r['id']
                             for r in phase2['rules']))

    def test_validate_knowledge_full_pass(self):
        result = validate_knowledge(ROOT)
        entities = result['entities']
        self.assertIn('bazi.section.s185', entities)
        self.assertIn('bazi.chapter.ziping_zaqi', entities)
        self.assertIn('bazi.classic.zipingzhenquan', entities)


if __name__ == '__main__':
    unittest.main()
