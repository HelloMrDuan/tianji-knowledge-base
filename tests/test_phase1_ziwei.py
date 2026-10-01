import unittest
from pathlib import Path
from tianji_kb.knowledge import read_json
from tianji_kb.operations.ziwei import lucun,tianma,four_transformations

ROOT=Path(__file__).resolve().parents[1]
class ZiweiPhase1Tests(unittest.TestCase):
    def test_covers_12_palaces_14_major_and_required_auxiliary_stars(self):
        bundle=read_json(ROOT/'data/canonical/ziwei/phase1_knowledge.json')
        terms={t['name']:t for t in bundle['terms']}
        self.assertEqual(sum(t['attributes'].get('category')=='十二宫' for t in terms.values()),12)
        self.assertEqual(sum(t['attributes'].get('category')=='十四主星' for t in terms.values()),14)
        required=['左辅','右弼','文昌','文曲','天魁','天钺','擎羊','陀罗','火星','铃星','地空','地劫','禄存','天马','化禄','化权','化科','化忌','十二长生','庙','旺','陷']
        self.assertTrue(set(required)<=set(terms))
        self.assertIn('其他小星天空',terms['地空']['definition'])

    def test_classical_placement_examples(self):
        self.assertEqual(lucun('甲'),'寅')
        self.assertEqual(lucun('癸'),'子')
        self.assertEqual(tianma('寅'),'申')
        self.assertEqual(tianma('午'),'申')
        self.assertEqual(tianma('亥'),'巳')
        with self.assertRaises(ValueError):
            tianma('甲')

    def test_four_transformations_require_explicit_supported_variant(self):
        self.assertEqual(four_transformations('甲','iztro-default-v2'),{'化禄':'廉贞','化权':'破军','化科':'武曲','化忌':'太阳'})
        self.assertEqual(four_transformations('壬','iztro-default-v2')['化科'],'左辅')
        with self.assertRaises(ValueError):
            four_transformations('壬','unreviewed-quanshu-reading')
        candidates=read_json(ROOT/'data/quarantine/phase1/ziwei/variants.json')
        self.assertEqual(candidates['stage'],'quarantine')
        self.assertIn('壬梁紫府武',candidates['candidates'][0]['original_text'])
