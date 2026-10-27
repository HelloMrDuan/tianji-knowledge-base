"""TJ-011.2 earth-root consumption contract (E0257): sealed checks.

Runs in the offline assembled acceptance only (NOT public CI, same
partition rule as the earlier batches). Pins, against the sealed
environment:

- the sealed policy reviewed_root_branches still carries NO earth
  set (the contract is register-level only; the policy is untouched
  and the runtime still has no earth entry point);
- the contract's per-grade cell counts re-verify against the earth
  register in the sealed environment (same register the public
  contract tests pin, here read alongside the sealed resolver).
"""

import unittest

from tianji_kb import bazi_earth_roots as E
from tianji_kb.resolver import EvidenceResolver


class SealedPolicyUntouchedTests(unittest.TestCase):
    def test_policy_has_no_earth_root_set(self):
        policy = EvidenceResolver().entities[
            'bazi.concept.action_effects_v1'][1]['attributes']
        reviewed = policy['reviewed_root_branches']
        self.assertNotIn('土', reviewed)
        self.assertEqual(set(reviewed), {'木', '水', '金', '火'}
                         & set(reviewed))

    def test_contract_cells_match_register_under_sealed_env(self):
        counts = {}
        for stem in ('戊', '己'):
            for cell in E.EARTH_ROOT_TABLES[stem]:
                counts[cell['grade']] = counts.get(cell['grade'], 0) + 1
        self.assertEqual(counts.get('per_stem_listed'), 2)
        self.assertEqual(counts.get('conflicted_pending'), 8)
        self.assertEqual(counts.get('structural_present_ungraded'), 8)
        self.assertEqual(counts.get('no_root'), 6)
        self.assertNotIn('framework_derived', counts)


if __name__ == '__main__':
    unittest.main()
