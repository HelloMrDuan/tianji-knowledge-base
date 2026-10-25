"""B018: dream demand matrix view contract (TJ-019.1).

Runs in public CI (validate.yml). Pure file parsing of
web/visual-prototype/src/public/DreamCulturePage.tsx: no backend, no
private data required. This pins the matrix VIEW contract — seven
categories in WBS order, each unreviewed with an explicit
no-interpretation declaration, and no verdict language inside the
matrix section.

The backend no-interpretation discipline (unreviewed topics carry no
original-source text and no omen claim) is covered by
test_public_dream_culture_api.py and the B004 semantics tests; this
test covers only the new matrix view. TJ-019.3 (reviewed scenes) is
already implemented and is NOT touched by this batch.
"""

import re
import unittest
from pathlib import Path

PAGE = (Path(__file__).resolve().parent.parent
        / 'web' / 'visual-prototype' / 'src' / 'public'
        / 'DreamCulturePage.tsx')

# WBS listing order (static priority); no demand-count data exists, so
# no dynamic ranking is claimed anywhere in the matrix.
MATRIX_ORDER = ['被追', '故人', '考试', '结婚', '怀孕', '工作', '死亡']

# Verdict/medical language that must never appear inside the matrix.
FORBIDDEN_IN_MATRIX = ['吉', '凶', '预示', '会发生', '诊断', '治疗']


def _matrix_section(text):
    start = text.find('aria-label="高频梦境需求矩阵"')
    assert start != -1, 'matrix section not found'
    end = text.find('</section>', start)
    assert end != -1, 'matrix section never closes'
    return text[start:end]


class TestB018DreamMatrixView(unittest.TestCase):
    def test_matrix_section_exists(self):
        text = PAGE.read_text(encoding='utf-8')
        self.assertIn('dream-culture-matrix', text)
        self.assertIn('高频梦境需求矩阵', text)
        section = _matrix_section(text)
        self.assertIn('矩阵仅做分类排队，不产解释', section)

    def test_seven_categories_in_wbs_order(self):
        text = PAGE.read_text(encoding='utf-8')
        # The order is pinned in the MATRIX_TOPICS constant, not in the
        # rendered list order alone: labels must appear in WBS order.
        const_start = text.find('MATRIX_TOPICS')
        const_end = text.find('] as const', const_start)
        const_block = text[const_start:const_end]
        positions = [const_block.find(f'"{label}"') for label in MATRIX_ORDER]
        for label, pos in zip(MATRIX_ORDER, positions):
            self.assertNotEqual(pos, -1, f'category missing from matrix: {label}')
        self.assertEqual(positions, sorted(positions),
                         'matrix categories are not in WBS order')

    def test_each_category_declares_unreviewed_and_no_interpretation(self):
        text = PAGE.read_text(encoding='utf-8')
        section = _matrix_section(text)
        # The per-item template carries the declaration (rendered once
        # per item at runtime — the browser spec verifies all seven
        # rendered items); the status marker is in the same template.
        self.assertIn('无精确动作原典，不产解释', section)
        self.assertIn('未审核', section)

    def test_no_verdict_language_inside_matrix(self):
        text = PAGE.read_text(encoding='utf-8')
        section = _matrix_section(text)
        for word in FORBIDDEN_IN_MATRIX:
            self.assertNotIn(word, section,
                             f'verdict language inside matrix: {word}')

    def test_matrix_does_not_touch_unreviewed_list_logic(self):
        text = PAGE.read_text(encoding='utf-8')
        # The existing result-dependent unreviewed aside is untouched.
        self.assertIn('dream-culture-unreviewed', text)
        self.assertIn('result.unreviewed_topics', text)


if __name__ == '__main__':
    unittest.main()
