"""B008 / TJ-024.1: compatibility A/B swap consistency.

Runs the real scenario engine twice with the two birth inputs exchanged
and asserts the results are exact mirrors. This is the test the existing
bidirectional test does NOT cover: test_scenario_engine.py only checks
that a single run has both directions present, never that swapping the
inputs swaps the outputs.

Requires the reviewed production runtime + knowledge data (same as
test_scenario_engine.py). It is discovered and executed by the offline
controlled acceptance suite (scripts/accept_offline.py --suite all) and
by private CI. It is NOT wired into public validate.yml, and public CI
must never be claimed to have executed it.
"""

import unittest

from tianji_kb.scenario_engine import execute_scenario

A_BIRTH = "2000-01-07T12:00:00+08:00"
B_BIRTH = "2000-02-01T12:00:00+08:00"


def _run(a_birth, b_birth):
    output = execute_scenario(
        "compatibility",
        {
            "person_a_birth_value": a_birth,
            "person_b_birth_value": b_birth,
        },
    )
    assert output["status"] == "production_limited", output.get("status")
    return output["result"]


def _mirror_key(hit, swapped):
    """Normalised key for one cross-matrix hit.

    When swapped=True, returns the key that hit must have in the
    opposite run (pillars exchanged, branches/stems reversed).
    Stem five-combinations are symmetric, so stems compare as a set.
    """
    pa = hit["person_b_pillar"] if swapped else hit["person_a_pillar"]
    pb = hit["person_a_pillar"] if swapped else hit["person_b_pillar"]
    if "branches" in hit:
        seq = tuple(reversed(hit["branches"])) if swapped else tuple(hit["branches"])
        return (
            hit["tier"],
            hit["relation_type"],
            hit["rule_id"],
            pa,
            pb,
            ("branches", seq),
        )
    seq = frozenset(hit["stems"])
    return (
        hit["tier"],
        hit["relation_type"],
        hit["rule_id"],
        pa,
        pb,
        ("stems", seq),
    )


class CompatibilitySwapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.forward = _run(A_BIRTH, B_BIRTH)
        cls.swapped = _run(B_BIRTH, A_BIRTH)

    def test_day_master_relations_mirror_exactly(self):
        fwd = self.forward["day_master_relations"]
        swp = self.swapped["day_master_relations"]
        self.assertEqual(
            fwd["a_sees_b"]["ten_god"],
            swp["b_sees_a"]["ten_god"],
        )
        self.assertEqual(
            fwd["b_sees_a"]["ten_god"],
            swp["a_sees_b"]["ten_god"],
        )

    def test_spouse_palace_day_branches_mirror_exactly(self):
        self.assertEqual(
            self.forward["person_a"]["spouse_palace"]["day_branch"],
            self.swapped["person_b"]["spouse_palace"]["day_branch"],
        )
        self.assertEqual(
            self.forward["person_b"]["spouse_palace"]["day_branch"],
            self.swapped["person_a"]["spouse_palace"]["day_branch"],
        )

    def test_cross_matrix_hits_mirror_in_both_directions(self):
        fwd_hits = self.forward["cross_relation_matrix"]["hits"]
        swp_hits = self.swapped["cross_relation_matrix"]["hits"]
        self.assertEqual(len(fwd_hits), len(swp_hits))
        swp_keys = {_mirror_key(h, swapped=False) for h in swp_hits}
        for hit in fwd_hits:
            self.assertIn(
                _mirror_key(hit, swapped=True),
                swp_keys,
                msg=f"no mirror in swapped run for {hit}",
            )
        fwd_keys = {_mirror_key(h, swapped=False) for h in fwd_hits}
        for hit in swp_hits:
            self.assertIn(
                _mirror_key(hit, swapped=True),
                fwd_keys,
                msg=f"no mirror in forward run for {hit}",
            )

    def test_cross_matrix_summary_counts_are_identical(self):
        self.assertEqual(
            self.forward["cross_relation_matrix"]["summary"],
            self.swapped["cross_relation_matrix"]["summary"],
        )

    def test_evidence_matrix_ids_match_and_xianchi_evidence_mirrors(self):
        fwd = {item["id"]: item for item in self.forward["relation_evidence_matrix"]}
        swp = {item["id"]: item for item in self.swapped["relation_evidence_matrix"]}
        self.assertEqual(set(fwd), set(swp))
        self.assertTrue(
            all(item["interpretation_allowed"] is False for item in fwd.values())
        )
        self.assertTrue(
            all(item["interpretation_allowed"] is False for item in swp.values())
        )
        self.assertEqual(
            set(fwd["xianchi-a-to-b"]["evidence_ids"]),
            set(swp["xianchi-b-to-a"]["evidence_ids"]),
        )
        self.assertEqual(
            set(fwd["xianchi-b-to-a"]["evidence_ids"]),
            set(swp["xianchi-a-to-b"]["evidence_ids"]),
        )


if __name__ == "__main__":
    unittest.main()
