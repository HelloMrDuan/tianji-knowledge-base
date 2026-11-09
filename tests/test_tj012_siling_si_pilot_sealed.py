"""TJ-012.3 Slice C 巳月试点 sealed-environment suite: 巳月司令试点.

Runs ONLY in the assembled offline acceptance environment (public CI
does not execute this file; see the validate.yml note beside the
public suite). Verifies, against the sealed snapshot and the pinned
provider in the assembled runtime:

- the pilot's provenance quote (the 巳-month clause of the T1 table,
  19 chars) equals the sealed snapshot slice [48056, 48075) verbatim
  and occurs exactly once in the full snapshot text; the full
  twelve-month table quote stays in the registration and is never
  repeated in the pilot output;
- the provider replay of the 2025 / 2026 / 1988 立夏 and 芒种 instants
  in the assembled environment equals the independently recorded Golden
  anchors (1988 instants carry the DST-era +09:00 offset);
- one real birth instant end to end: its month pillar from the
  production calendar chain is 辛巳 (巳月) and the pilot's commander
  matches the hand-derived segment for that instant;
- the full public Golden case table re-run in the assembled env.
"""

from __future__ import annotations

import json
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from tianji_kb.bazi_siling_si_pilot import _provider_jie_instant, si_siling_pilot
from tianji_kb.calendar import calendar

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = (ROOT / "data" / "quarantine" / "public_domain_snapshots"
            / "daizhigev20" / "sanming_tonghui.txt")
GOLDEN = json.loads(
    (ROOT / "tests/golden_tj012_siling_si_pilot.json").read_text("utf-8"))
CHINA = ZoneInfo("Asia/Shanghai")


def _facts(year_key):
    window = GOLDEN["jie_windows"][year_key]
    return {"provider": dict(GOLDEN["provider"]),
            "lixia": dict(window["lixia"]),
            "next_jie": dict(window["next_jie"])}


class SnapshotQuoteTest(unittest.TestCase):
    def test_pilot_provenance_quote_matches_sealed_snapshot(self) -> None:
        text = SNAPSHOT.read_bytes().decode("utf-8")
        out = si_siling_pilot("2025-05-05T05:57:13+00:00",
                              version_id="sanming-t1",
                              jie_facts=_facts("2025"))
        self.assertEqual(out["status"], "computed")
        prov = out["provenance"]
        locator = prov["quote_locator"]
        self.assertEqual((locator["char_start"], locator["char_end"]),
                         (48056, 48075))
        self.assertEqual(text[locator["char_start"]:locator["char_end"]],
                         prov["quote"])
        self.assertEqual(text.count(prov["quote"]), 1)
        self.assertIsNone(prov["text_layer"])

    def test_full_table_quote_is_not_repeated_in_output(self) -> None:
        # The full T1 table quote (316 chars) lives only in the
        # registration; the pilot output carries just the 19-char
        # 巳-month clause.
        out = si_siling_pilot("2025-05-05T05:57:13+00:00",
                              version_id="sanming-t1",
                              jie_facts=_facts("2025"))
        self.assertEqual(len(out["provenance"]["quote"]), 19)
        self.assertEqual(out["segment"]["registered_basis"], "戊土七日")


class AssembledProviderReplayTest(unittest.TestCase):
    def test_replay_matches_golden_anchors(self) -> None:
        for year_key, year in (("2025", 2025), ("2026", 2026),
                               ("1988", 1988)):
            window = GOLDEN["jie_windows"][year_key]
            for term, key in (("立夏", "lixia"), ("芒种", "next_jie")):
                replayed = _provider_jie_instant(year, term)
                claimed = datetime.fromisoformat(window[key]["at"])
                self.assertEqual(replayed, claimed, (year_key, term))


class RealBirthEndToEndTest(unittest.TestCase):
    def test_real_birth_in_si_window(self) -> None:
        # Real birth instant 2025-05-10 03:00 +08:00. Hand derivation:
        # month pillar after 立夏 in 乙巳 year is 辛巳 (巳月); elapsed
        # since t0 = 4d 13h 2m 47s < 7d -> first segment 戊.
        birth = datetime(2025, 5, 10, 3, 0, 0, tzinfo=CHINA)
        cal = calendar(birth)
        self.assertEqual(cal["month_ganzhi"], "辛巳")
        out = si_siling_pilot(birth, version_id="sanming-t1",
                              jie_facts=_facts("2025"))
        self.assertEqual(out["status"], "computed")
        self.assertEqual(out["commander"], "戊")
        self.assertEqual(out["elapsed_seconds"],
                         4 * 86400 + 13 * 3600 + 2 * 60 + 47)
        self.assertEqual(out["month_branch"], "巳")

    def test_golden_table_reruns_in_assembled_env(self) -> None:
        for case in GOLDEN["cases"]:
            window = GOLDEN["jie_windows"][case["window"]]
            facts = {"provider": dict(GOLDEN["provider"]),
                     "lixia": dict(window["lixia"]),
                     "next_jie": dict(window["next_jie"])}
            override = case.get("jie_override") or {}
            if override.get("drop_next_jie"):
                facts.pop("next_jie")
            if "lixia_at" in override:
                facts["lixia"]["at"] = override["lixia_at"]
            if "lixia_precision" in override:
                facts["lixia"]["precision"] = override["lixia_precision"]
            if "provider_version" in override:
                facts["provider"]["version"] = override["provider_version"]
            if "provider_identity_verified" in override:
                facts["provider"]["identity_verified"] = \
                    override["provider_identity_verified"]
            if "precision_warning" in override:
                facts["precision_warning"] = override["precision_warning"]
            if "source_ref" in override:
                facts["source_ref"] = override["source_ref"]
            with self.subTest(case=case["id"]):
                out = si_siling_pilot(
                    case["birth"], version_id=case["version_id"],
                    jie_facts=facts,
                    birth_time_precision=case.get(
                        "birth_time_precision", "second"))
                self.assertEqual(out["status"], case["expected_status"])
                self.assertEqual(out["commander"],
                                 case["expected_commander"])


if __name__ == "__main__":
    unittest.main()
