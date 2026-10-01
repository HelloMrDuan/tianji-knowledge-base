import unittest
from itertools import product
from tianji_kb.foundations import hexagram,seed
from tianji_kb.golden import run_cases
from tianji_kb.operations.yijing import transform
from tianji_kb.operations.yijing_chart import chart

class YijingExecutionTests(unittest.TestCase):
    def test_fixed_named_cases(self):
        self.assertEqual(len(run_cases(domain='yijing')),3)
    def test_all_64_hexagrams_and_involutions(self):
        seen=set()
        for values in product('01',repeat=6):
            bits=''.join(values);h=hexagram(bits);seen.add(h['number'])
            for operation in ['opposite','inverse']:
                self.assertEqual(transform(transform(bits,operation),operation),bits)
            self.assertEqual(transform(transform(bits,'opposite'),'inverse'),transform(transform(bits,'inverse'),'opposite'))
            self.assertEqual(transform(bits,'nuclear'),bits[1:4]+bits[2:5])
            self.assertEqual(hexagram(transform(bits,'inverse'))['lower'],next(t['name'] for t in seed()['trigrams'] if t['binary_bottom_to_top']==bits[3:][::-1]))
        self.assertEqual(seen,set(range(1,65)))
    def test_all_4096_change_masks_are_reversible(self):
        for values in product('01',repeat=6):
            bits=''.join(values)
            for mask in product((False,True),repeat=6):
                lines=[i+1 for i,x in enumerate(mask) if x]
                changed=transform(bits,'change',lines)
                self.assertEqual(transform(changed,'change',lines),bits)
                self.assertEqual(sum(a!=b for a,b in zip(bits,changed)),len(lines))
    def test_invalid_input_and_variant_fail(self):
        for bits,lines in [('101',[]),('10x010',[]),('111111',[1,1]),('111111',[True]),('111111',[0])]:
            with self.assertRaises(ValueError):chart(bits,lines)
        with self.assertRaises(ValueError):chart('111111',variant='unreviewed')
