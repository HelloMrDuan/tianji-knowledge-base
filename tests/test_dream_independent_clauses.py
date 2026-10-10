"""Fresh first-person dream clauses remain separate from preceding negation."""
import unittest
from tianji_kb.operations.dream_knowledge import retrieve

class DreamIndependentClauseTests(unittest.TestCase):
    def test_separate_independent_clause(self):
        value = '我梦见没有被蛇咬后来我梦见我捡到了钱'
        matches = retrieve(value)['matched_interpretations']
        self.assertEqual([m['term_id'] for m in matches], ['dream.term.money'])
