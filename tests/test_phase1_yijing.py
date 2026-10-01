import unittest
from pathlib import Path
from tianji_kb.knowledge import read_json
from tianji_kb.operations.yijing import transform

ROOT = Path(__file__).resolve().parents[1]
class YijingPhase1Tests(unittest.TestCase):
    def test_all_64_relations_match_independent_preexisting_table(self):
        records = read_json(ROOT / 'data/canonical/yijing/hexagram_relations_v1.json')['records']
        by_number = {r['number']: r for r in records}
        for record in records:
            bits = record['binary_bottom_to_top']
            for operation, key in [('opposite', 'opposite'), ('inverse', 'reversed'), ('nuclear', 'nuclear')]:
                self.assertEqual(transform(bits, operation), by_number[record[key]['number']]['binary_bottom_to_top'])
            for line in record['line_changes']:
                self.assertEqual(transform(bits, 'change', [line['line']]), line['target']['binary_bottom_to_top'])
            self.assertEqual(transform(transform(bits,'inverse'),'inverse'),bits)
            self.assertEqual(transform(transform(bits,'opposite'),'opposite'),bits)

    def test_standard_entities_preserve_existing_text(self):
        bundle = read_json(ROOT / 'data/canonical/yijing/phase1_knowledge.json')
        hexagrams = [c['attributes'] for c in bundle['concepts'] if c['kind']=='hexagram']
        self.assertEqual(len(hexagrams),64)
        self.assertEqual(len({h['binary'] for h in hexagrams}),64)
        self.assertEqual(sum(len(h['lines']) for h in hexagrams),384)
        core = read_json(ROOT / 'data/canonical/yijing/zhouyi_classic_core.json')['records']
        for entity, original in zip(hexagrams,core):
            self.assertEqual(entity['judgment'],original['judgment'])
            self.assertEqual(entity['lines'],original['lines'])
        self.assertEqual(len([x for x in bundle['concepts'] if x['kind']=='trigram']),8)
        self.assertIn('乾坤无互之文本例外',[r['name'] for r in bundle['rules']])

    def test_invalid_line_changes_are_rejected(self):
        for bits, operation, lines in [('11111','change',[]),('11111x','change',[]),('111111','change',[0]),('111111','change',[1,1]),('111111','opposite',[1]),('111111','change',[True])]:
            with self.subTest(bits=bits,lines=lines),self.assertRaises(ValueError):
                transform(bits,operation,lines)
