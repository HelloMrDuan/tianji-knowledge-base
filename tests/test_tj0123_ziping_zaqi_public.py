"""TJ-012.3《子平真詮》准入＋Ch16 平行登记：公开侧治理登记钉值。

Public CI (no sealed snapshot needed). The sealed-side section
building itself is verified in the assembled acceptance by
tests/test_tj0123_ziping_zaqi_sealed.py; this suite pins the
public record and the registration posture:

- the new source record (library_scan, NLC416) is schema-legal,
  the whole 103-record table still validates, and the census
  moved 102 -> 103 (C:96 -> C:97, D:6 unchanged);
- the audit lineage row, the governance record
  (TJ0123_ZIPING_ZAQI_RECORD) and the inventory row
  (ziping-zaqi-ch16, maintained_pending /
  execution_binding_structure) are internally consistent, with
  the staged manifest pins before/after;
- the 20 Ch16 核取短引 (kernel phrases, one operative phrase per
  item, each ≤14 chars) match the Golden transcription verbatim,
  locator spans equal quote lengths, each kernel occurs exactly
  once in the sealed TXT, and the kernels are non-contiguous
  (min gap 4 chars, total coverage 174 of 821 chars) so the
  chapter cannot be reconstructed from the public record --
  the B-16-19 print form (no 如 after 又, no 。 after 並透) is
  the registered form; the evidence table's two wrong characters
  appear nowhere in the module or the Golden, and the public
  side registers only the kernel 「透戊為食」;
- the 7 variants are recorded as printed + doubtful reading +
  evidence, never silently corrected;
- the 11 Slice B oppositions are recorded as a parallel
  conflict (never auto-resolved), determination stays None,
  evidence_binding stays pending, research_only with public /
  ai disabled;
- no sealed section text leaks into the public record files:
  the retained kernels are short and non-contiguous (a
  boundary-crossing probe spanning the gap between two kernels
  appears in none of the module, Golden, governance register or
  governance document; the Ch17 body opening, the wrong
  B-16-19 forms and the wrong prior transcription are absent
  from the module and the Golden); a sealed-side scan in the
  companion suite asserts the same over the public files present in
  the assembled backend (the workflow file is not assembled, so the
  sealed scan does not cover it — it carries no chapter text);
- the module has no execution wiring: no production module
  imports it, so no chart / API output can carry a ziping_zaqi
  key.
"""
import json
import unittest
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator

from tianji_kb import bazi_registration_governance as gov
from tianji_kb import bazi_ziping_zaqi as zp

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / 'tests' / 'golden_tj0123_ziping_zaqi.json').read_text('utf-8'))
DOC = ROOT / 'docs' / 'product' / 'TJ0123_ZIPING_ZHENQUAN_ADMISSION.md'
TXT = (ROOT / 'data' / 'quarantine' / 'public_domain_snapshots'
       / 'nlc416' / 'zipingzhenquan_1925_ch16.txt')
# Boundary-crossing probe: 8 chars spanning the gap [24,32) between
# the B-16-01 kernel [16,24) and the B-16-02 kernel [32,44). It is a
# contiguous substring of the sealed TXT but must not appear in any
# public file (kernels are registered per item, never joined across
# the gap between them).
LEAK_PROBE = '謂之雜氣也。如辰'
WRONG_B1619_A = '又如丙生辰月'
WRONG_B1619_B = '並透。而'
CH17_BODY = '辰戌丑未。最喜刑沖'
WRONG_DANGBU = '當而不貴者也'


def _sources():
    return json.loads((ROOT / 'config' / 'knowledge_sources.json')
                      .read_text(encoding='utf-8'))['sources']


class SourceRecordTests(unittest.TestCase):
    def test_new_source_record_fields(self):
        sources = _sources()
        by_id = {s['source_id']: s for s in sources}
        rec = by_id['bazi.source.zipingzhenquan']
        self.assertEqual(rec['title'], '子平真詮（1925 上海世界圖書館版）')
        self.assertEqual(rec['repository'], 'National Library of China')
        self.assertEqual(rec['provenance_kind'], 'library_scan')
        self.assertIsNone(rec['commit'])
        self.assertEqual(rec['catalog_id'], 'NLC416-11jh010455-35296')
        self.assertEqual(
            rec['pdf_sha256'],
            '71402a780b0351b54edf121a51bc4a4a4ce5896496c35b954563ee06f1a6f620')
        self.assertEqual(rec['url'],
                         'https://upload.wikimedia.org/wikipedia/commons/f/fe/NLC416-11jh010455-35296_%E5%AD%90%E5%B9%B3%E7%9C%9F%E8%A9%AE.pdf')
        self.assertEqual(rec['path'], 'NLC416-11jh010455-35296_子平真詮.pdf')
        self.assertEqual(
            rec['content_path'],
            'data/quarantine/public_domain_snapshots/nlc416/zipingzhenquan_1925_ch16.txt')
        self.assertEqual(
            rec['sha256'],
            '98576342cd8c4fb092a7bec5c1e86b7b02c051cb14a9c6a7f632f5a42b647966')
        self.assertIsNone(rec['blob_sha'])
        self.assertEqual(rec['license'], 'Public-Domain (pre-modern text only)')
        self.assertTrue(rec['public_domain'])
        self.assertEqual(rec['evidence_level'], 'C')
        self.assertEqual(rec['kind'], 'classical')
        self.assertEqual(rec['content_format'], 'text')
        self.assertEqual(rec['author'], '沈孝瞻')
        self.assertIn('《耕寸集》', rec['era'])
        self.assertIn('1925', rec['era'])
        self.assertIn('仅第 16 章', rec['review_scope'])
        self.assertEqual(rec['retrieved_at'], '2026-11-05')

    def test_schema_legal_and_census(self):
        schema = json.loads((ROOT / 'schemas' / 'knowledge'
                             / 'sources.schema.json').read_text('utf-8'))
        obj = json.loads((ROOT / 'config' / 'knowledge_sources.json')
                         .read_text(encoding='utf-8'))
        Draft202012Validator(schema).validate(obj)
        # TJ-012.3《子平真詮》准入普查同步：登记
        # bazi.source.zipingzhenquan（《子平真詮》1925 上海世界圖書館版，
        # C 级）后来源普查由 C:96 变 C:97（登记表共 103 条），同上口径。
        self.assertEqual(len(obj['sources']), 103)
        self.assertEqual(
            Counter(s['evidence_level'] for s in obj['sources']),
            Counter({'C': 97, 'D': 6}))
        self.assertEqual(
            len({s['source_id'] for s in obj['sources']}), 103)

    def test_audit_lineage_row(self):
        audit = json.loads((ROOT / 'config' / 'phase2_source_audit.json')
                           .read_text(encoding='utf-8'))
        rows = {r['source_id']: r for r in audit['lineages']}
        self.assertEqual(len(rows), 103)
        row = rows['bazi.source.zipingzhenquan']
        self.assertEqual(row['lineage_group'], 'NLC416-11jh010455-35296')
        self.assertEqual(row['edition_status'], 'unverified')
        self.assertEqual(row['authority_status'], 'unverified')
        self.assertEqual(row['grade_ceiling'], 'C')
        self.assertIn('bazi.section.s185', row['review_basis'])


class TranscriptionTests(unittest.TestCase):
    def test_quotes_match_golden_transcription(self):
        self.assertEqual(zp.ZIPING_VARIANT, GOLDEN['variant'])
        self.assertEqual(zp.ZIPING_SOURCE_ID, GOLDEN['source_id'])
        self.assertEqual(zp.ZIPING_SECTION_ID, GOLDEN['source_section_id'])
        golden_quotes = {q['id']: q for q in GOLDEN['quotes']}
        self.assertEqual({q['id'] for q in zp.ZIPING_ZAQI_QUOTES},
                         set(golden_quotes))
        self.assertEqual(len(zp.ZIPING_ZAQI_QUOTES), 20)
        for quote in zp.ZIPING_ZAQI_QUOTES:
            want = golden_quotes[quote['id']]
            self.assertEqual(quote['quote'], want['quote'])
            self.assertEqual(quote['locator'], want['locator'])
            self.assertEqual(quote['source_id'], want['source_id'])
            self.assertEqual(quote['layer'], want['layer'])
            loc = quote['locator']
            self.assertEqual(loc['char_end'] - loc['char_start'],
                             len(quote['quote']),
                             'locator span must equal the verbatim quote')
            self.assertLessEqual(len(quote['quote']), 14,
                                 'kernel quotes only, ≤14 chars')
            self.assertFalse(
                any(0xE000 <= ord(c) <= 0xF8FF for c in quote['quote']),
                'no PUA may sit inside a registered quote window')

    def test_locators_do_not_tile_chapter(self):
        locs = sorted((q['locator']['char_start'], q['locator']['char_end'])
                      for q in zp.ZIPING_ZAQI_QUOTES)
        # Kernels start at 16 and end at 804: the head [0,16) and the
        # tail [804,821) are never publicly quoted.
        self.assertEqual(locs[0][0], 16)
        self.assertEqual(locs[-1][1], 804)
        total = 0
        for (s0, e0), (s1, e1) in zip(locs, locs[1:]):
            # Every gap between consecutive kernels is at least 4
            # chars of unquoted text; no two kernels are adjacent.
            self.assertGreaterEqual(s1 - e0, 4)
            total += e0 - s0
        total += locs[-1][1] - locs[-1][0]
        self.assertEqual(total, 174)


    def test_notes_conflicts_variants_match_golden(self):
        self.assertEqual(list(zp.ZIPING_ZAQI_ADJUDICATION_NOTES),
                         GOLDEN['adjudication_notes'])
        self.assertEqual(list(zp.ZIPING_ZAQI_CONFLICT_POINTS),
                         GOLDEN['conflict_points'])
        self.assertEqual(list(zp.ZIPING_ZAQI_LIMITATIONS),
                         GOLDEN['limitations'])
        self.assertEqual([dict(v) for v in zp.ZIPING_ZAQI_VARIANTS],
                         GOLDEN['variants'])
        self.assertEqual([dict(v) for v in zp.ZIPING_ZAQI_ITEM_VERDICTS],
                         GOLDEN['item_verdicts'])
        self.assertEqual(dict(zp.ZIPING_ZAQI_REGISTRATION),
                         GOLDEN['registration'])

    def test_b1619_print_form_registered(self):
        record = zp.ziping_zaqi_quote('B-16-19')
        # Print form: the public side registers only the kernel.
        self.assertEqual(record['quote'], '透戊為食')
        self.assertEqual(record['locator'],
                         {'char_start': 734, 'char_end': 738})
        module_text = (ROOT / 'src' / 'tianji_kb'
                       / 'bazi_ziping_zaqi.py').read_text(encoding='utf-8')
        golden_text = (ROOT / 'tests'
                       / 'golden_tj0123_ziping_zaqi.json').read_text(
                           encoding='utf-8')
        for text in (module_text, golden_text):
            self.assertNotIn(WRONG_B1619_A, text)
            self.assertNotIn(WRONG_B1619_B, text)

    def test_variants_not_silently_corrected(self):
        variants = {v['id']: v for v in zp.ZIPING_ZAQI_VARIANTS}
        # Print forms stay in the VARIANTS table; doubtful readings
        # never replace them.
        self.assertIn('會何全局', variants['V-01']['original'])
        self.assertNotIn('會合全局', variants['V-01']['original'])
        self.assertIn('似又清辰中之戊', variants['V-02']['original'])
        self.assertIn('月規用官', variants['V-03']['original'])
        self.assertNotIn('月令用官', variants['V-03']['original'])
        self.assertIn('在即此為例', variants['V-04']['original'])
        self.assertNotIn('祇即此為例', variants['V-04']['original'])
        self.assertIn('戌竝', variants['V-05']['original'])
        self.assertIn('朋沖', variants['V-06']['original'])
        self.assertIn('下成', variants['V-06']['original'])
        self.assertIn('月劫', variants['V-07']['original'])
        self.assertEqual(
            sorted(v['status'] for v in variants.values()).count('doubtful'),
            4)
        self.assertEqual(
            sorted(v['status'] for v in variants.values()).count('as_printed'),
            3)


class NonReconstructabilityTests(unittest.TestCase):
    def test_quotes_short_noncontiguous_and_capped(self):
        locs = sorted((q['locator']['char_start'], q['locator']['char_end'])
                      for q in zp.ZIPING_ZAQI_QUOTES)
        self.assertEqual(len(locs), 20)
        self.assertEqual(max(e - s for s, e in locs), 14)
        self.assertTrue(all(len(q['quote']) <= 14
                            for q in zp.ZIPING_ZAQI_QUOTES))
        self.assertEqual(locs[0][0], 16)
        self.assertEqual(locs[-1][1], 804)
        gaps = [s1 - e0 for (s0, e0), (s1, e1) in zip(locs, locs[1:])]
        self.assertGreaterEqual(min(gaps), 4)
        self.assertEqual(sum(e - s for s, e in locs), 174)

    def test_variant_originals_bounded(self):
        # Variant originals are evidence, kept as printed; each is a
        # single short span (longest is V-02 at 19 chars).
        for variant in zp.ZIPING_ZAQI_VARIANTS:
            self.assertLessEqual(len(variant['original']), 21,
                                 variant['id'])
        self.assertEqual(
            max(len(v['original']) for v in zp.ZIPING_ZAQI_VARIANTS), 19)


class ConflictTests(unittest.TestCase):
    def test_eleven_oppositions_recorded_not_resolved(self):
        verdicts = {v['id']: v for v in zp.ZIPING_ZAQI_ITEM_VERDICTS}
        opposing = [i for i, v in verdicts.items()
                    if v['slice_b'] == 'contradict']
        self.assertEqual(
            opposing,
            ['B-16-03', 'B-16-04', 'B-16-05', 'B-16-06', 'B-16-07',
             'B-16-08', 'B-16-09', 'B-16-10', 'B-16-12', 'B-16-13',
             'B-16-14'])
        self.assertEqual(zp.ZIPING_ZAQI_CONFLICT_SUMMARY[
            'oppositions_to_slice_b'], 11)
        self.assertEqual(
            zp.ZIPING_ZAQI_CONFLICT_SUMMARY['consistent_items'],
            ['B-16-01', 'B-16-02'])
        self.assertEqual(
            zp.ZIPING_ZAQI_CONFLICT_SUMMARY['sanming_tension_items'],
            ['B-16-17'])
        self.assertEqual(
            zp.ZIPING_ZAQI_CONFLICT_SUMMARY['unusable_mechanism_items'],
            ['B-16-10', 'B-16-16', 'B-16-18'])
        reg = zp.ziping_zaqi_registration()
        self.assertTrue(reg['conflict_present'])
        self.assertTrue(reg['research_only'])
        self.assertFalse(reg['public_enabled'])
        self.assertFalse(reg['ai_enabled'])
        self.assertIsNone(reg['determination'])
        self.assertEqual(reg['evidence_binding'], 'pending')
        self.assertEqual(reg['source_section_id'], 'bazi.section.s185')

    def test_lookup_fails_closed(self):
        with self.assertRaises(ValueError):
            zp.ziping_zaqi_quote('B-16-21')
        with self.assertRaises(ValueError):
            zp.ziping_zaqi_verdict('B-16-00')
        self.assertEqual(zp.ziping_zaqi_quote('B-16-03')['quote'],
                         '透干會支。取其清者用之。')


class RecordConsistencyTests(unittest.TestCase):
    def test_record_entities(self):
        record = gov.TJ0123_ZIPING_ZAQI_RECORD
        self.assertEqual(record['event'], 'E0382')
        self.assertEqual(record['date'], '2026-11-06')
        self.assertEqual(record['document'],
                         'docs/product/TJ0123_ZIPING_ZHENQUAN_ADMISSION.md')
        self.assertEqual(record['canonical_chapters_added'],
                         ['bazi.chapter.ziping_zaqi'])
        self.assertEqual(record['canonical_sections_added'],
                         ['bazi.section.s185'])
        self.assertEqual(record['canonical_terms_added'], [])
        self.assertEqual(record['classic_source_ids_added'],
                         {'bazi.classic.zipingzhenquan':
                          ['bazi.source.zipingzhenquan']})
        self.assertEqual(len(record['public_config_registrations']), 2)
        self.assertEqual(record['phase1_rules_added'], [])
        self.assertEqual(record['phase2_rules_added'], [])
        self.assertEqual(record['golden_cases_added'], [])
        self.assertEqual(len(record['quotes_verified']), 20)
        self.assertEqual(record['quotes_verified'][0], 'B-16-01')
        self.assertEqual(record['quotes_verified'][-1], 'B-16-20')
        self.assertIn('maintained_pending',
                      record['registration_disposition'])
        self.assertIn('execution_binding_structure',
                      record['registration_disposition'])

    def test_manifest_and_file_pins(self):
        record = gov.TJ0123_ZIPING_ZAQI_RECORD
        self.assertEqual(record['snapshot_files_before'], 237)
        self.assertEqual(record['snapshot_files_after'], 239)
        self.assertEqual(record['snapshot_bytes_before'], 16722816)
        self.assertEqual(record['snapshot_bytes_after'], 16739253)
        self.assertEqual(
            record['manifest_sha256_before'],
            '26b63e64bed736b08a7dcd686f6a75de733fd44ba9eec9195248e69730485329')
        self.assertEqual(
            record['manifest_sha256_after'],
            'eca717ef4b8bf8e08de00e2b24ac4ecddfa2dbe815a141b7e19d63668699d2ff')
        self.assertEqual(len(record['sealed_files_changed']), 3)
        self.assertIn('data/canonical/bazi/phase1_knowledge.json',
                      record['sealed_files_changed'])
        self.assertEqual(
            record['sealed_file_sha256_after'],
            {'data/quarantine/public_domain_snapshots/nlc416/'
             'zipingzhenquan_1925_ch16.txt':
             '98576342cd8c4fb092a7bec5c1e86b7b02c051cb14a9c6a7f632f5a42b647966'})
        self.assertIn('eca717ef', record['sealed_file_sha256_note'])

    def test_inventory_row_maintained_pending(self):
        rows = [r for r in gov.REGISTRATION_INVENTORY
                if r['item'] == 'ziping-zaqi-ch16']
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row['disposition'], 'maintained_pending')
        self.assertEqual(row['reason_class'], 'execution_binding_structure')
        self.assertEqual(row['disclosure_sites'],
                         ['src/tianji_kb/bazi_ziping_zaqi.py'])
        self.assertTrue(row['unlock_path'])
        self.assertIn('bazi.section.s185', row['reason'])
        # E0382: the maintained set grows from three to four.
        self.assertEqual(len(gov.MAINTAINED_ITEMS), 4)
        self.assertEqual(gov.MAINTAINED_ITEMS,
                         ['dayun-compose', 'dayun-timeline-view',
                          'siling-yin-pilot', 'ziping-zaqi-ch16'])


class DocumentAndLeakTests(unittest.TestCase):
    def test_document_names_entities_pins_and_gap(self):
        text = DOC.read_text(encoding='utf-8')
        for needle in ('bazi.chapter.ziping_zaqi',
                       'bazi.section.s185',
                       'bazi.classic.zipingzhenquan',
                       'bazi.source.zipingzhenquan',
                       '26b63e64', 'eca717ef',
                       'execution_binding_structure',
                       'B-16-19', '准入 ≠ 裁定'):
            self.assertIn(needle, text)
        self.assertIn('印本無此二字', text)
        self.assertIn('多一「如」字', text)
        self.assertNotIn(CH17_BODY, text)
        # The doc records the correction, so it names the wrong prior
        # transcription once (as the corrected-away form), never as a
        # registered quote.
        self.assertIn('作「而不貴者也」非「當而不貴者也」', text)

    def test_no_sealed_section_text_in_public_records(self):
        gov_text = (ROOT / 'src' / 'tianji_kb'
                    / 'bazi_registration_governance.py').read_text(
                        encoding='utf-8')
        doc_text = DOC.read_text(encoding='utf-8')
        module_text = (ROOT / 'src' / 'tianji_kb'
                       / 'bazi_ziping_zaqi.py').read_text(encoding='utf-8')
        golden_text = (ROOT / 'tests'
                       / 'golden_tj0123_ziping_zaqi.json').read_text(
                           encoding='utf-8')
        for text in (gov_text, doc_text, module_text, golden_text):
            self.assertNotIn(LEAK_PROBE, text)
        for text in (module_text, golden_text):
            self.assertNotIn(CH17_BODY, text)
            self.assertNotIn(WRONG_DANGBU, text)

    def test_no_execution_wiring(self):
        # The module is pure registration data: no production module
        # may import it, so no chart / API output can carry a
        # ziping_zaqi key. The governance register may name it as
        # data (its disclosure ledger) but must never import it.
        src = ROOT / 'src' / 'tianji_kb'
        for path in sorted(src.rglob('*.py')):
            if path.name in ('bazi_ziping_zaqi.py',
                             'bazi_registration_governance.py'):
                continue
            self.assertNotIn('bazi_ziping_zaqi', path.read_text(
                encoding='utf-8'), path.name)
        gov_text = (src / 'bazi_registration_governance.py').read_text(
            encoding='utf-8')
        self.assertNotIn('import bazi_ziping_zaqi', gov_text)
        self.assertNotIn('from .bazi_ziping_zaqi', gov_text)
        self.assertNotIn('ziping_zaqi_quote(', gov_text)
        self.assertNotIn('ziping_zaqi_registration(', gov_text)


class SealedLocatorTests(unittest.TestCase):
    @unittest.skipIf(not TXT.exists(),
                     'sealed snapshot absent in public CI; the sealed '
                     'companion verifies locators in offline acceptance')
    def test_quotes_equal_sealed_txt_slices(self):
        raw = TXT.read_bytes()
        import hashlib
        self.assertEqual(
            hashlib.sha256(raw).hexdigest(), zp.ZIPING_TXT_SHA256)
        self.assertEqual(len(raw), zp.ZIPING_TXT_BYTES)
        text = raw.decode('utf-8')
        self.assertTrue(text.endswith('\n'))
        body = text[:-1]
        self.assertEqual(len(body), zp.ZIPING_TXT_CHARS)
        for quote in zp.ZIPING_ZAQI_QUOTES:
            loc = quote['locator']
            self.assertEqual(body[loc['char_start']:loc['char_end']],
                             quote['quote'], quote['id'])
            self.assertEqual(body.count(quote['quote']), 1, quote['id'])


if __name__ == '__main__':
    unittest.main()
