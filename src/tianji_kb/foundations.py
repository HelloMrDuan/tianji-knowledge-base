"""Shared, deterministic traditional symbols; reuse reviewed Canonical tables."""
import json
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STEMS = '甲乙丙丁戊己庚辛壬癸'
BRANCHES = '子丑寅卯辰巳午未申酉戌亥'
ELEMENTS = '木火土金水'
GENERATES = dict(zip(ELEMENTS, '火土金水木'))
CONTROLS = dict(zip(ELEMENTS, '土金水木火'))
CYCLE = tuple(STEMS[i%10]+BRANCHES[i%12] for i in range(60))

@lru_cache(maxsize=1)
def seed():
    return json.loads((ROOT/'data/canonical/seed.json').read_text())

def ganzhi_index(value):
    if value not in CYCLE:
        raise ValueError('Invalid sexagenary pillar')
    return CYCLE.index(value)

def branch_element(branch):
    if branch not in list(BRANCHES):
        raise ValueError('Expected one branch')
    return next(row[2] for row in seed()['earthly_branches'] if row[0]==branch)

def stem_element(stem):
    if stem not in list(STEMS):
        raise ValueError('Expected one stem')
    return ELEMENTS[STEMS.index(stem)//2]

def trigram(bits):
    return dict(next(t for t in seed()['trigrams'] if t['binary_bottom_to_top']==bits))

def hexagram(bits):
    if not isinstance(bits,str) or len(bits)!=6 or set(bits)-set('01'):
        raise ValueError('Expected six binary digits, bottom to top')
    lower,upper=trigram(bits[:3]),trigram(bits[3:])
    row=next(x for x in seed()['hexagrams'] if x[3]==upper['name'] and x[4]==lower['name'])
    return {'number':row[0],'name':row[2],'binary':bits,'lower':lower['name'],'upper':upper['name']}
