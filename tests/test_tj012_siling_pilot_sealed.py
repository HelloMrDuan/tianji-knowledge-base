"""TJ-012.3 Slice C step 2 sealed-environment suite: 寅月司令试点.

Runs ONLY in the assembled offline acceptance environment (public CI
does not execute this file; see the validate.yml note beside the
public suite). Verifies, against the sealed snapshot and the pinned
provider in the assembled runtime:

- the pilot's provenance quote (s024, 原注 layer) equals the sealed
  snapshot slice [38056, 38101) verbatim and occurs exactly once in
  the full snapshot text;
- the provider replay of the 2024 / 1987 立春 and 惊蛰 instants in
  the assembled environment equals the independently recorded Golden
  anchors (2024 立春 cross-checked against the TJ-015.2 frozen
  JPL-cited minute reference);
- one real birth instant end to end: its month pillar from the
  production calendar chain is 丙寅 (寅月) and the pilot's commander
  matches the hand-derived segment for that instant;
- the full public Golden case table re-run in the assembled env.
"""

from __future__ import annotations

import json
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from tianji_kb.bazi_siling_pilot import _provider_jie_instant, yin_siling_pilot
from tianji_kb.calendar import calendar

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = (ROOT / "data" / "quarantine" / "public_domain_snapshots"
            / "daizhigev20" / "ditiansui_chanwei.txt")
GOLDEN = json.loads(
    (ROOT / "tests/golden_tj012_siling_pilot.json").read_text("utf-8"))
CHINA = ZoneInfo("Asia/Shanghai")


def _facts(year_key):
    window = GOLDEN["jie_windows"][year_key]
    return {"provider": dict(GOLDEN["provider"]),
            "lichun": dict(window["lichun"]),
            "next_jie": dict(window["next_jie"])}


class SnapshotQuoteTest(unittest.TestCase):
    def test_pilot_provenance_quote_matches_sealed_snapshot(self) -> None:
        text = SNAPSHOT.read_bytes().decode("utf-8")
        out = yin_siling_pilot("2024-02-04T08:27:07+00:00",
                               version_id="ditiansui-yuanshuo",
                               jie_facts=_facts("2024"))
        self.assertEqual(out["status"], "computed")
        prov = out["provenance"]
        locator = prov["quote_locator"]
        self.assertEqual((locator["char_start"], locator["char_end"]),
                         (38056, 38101))
        self.assertEqual(text[locator["char_start"]:locator["char_end"]],
                         prov["quote"])
        self.assertEqual(text.count(prov["quote"]), 1)
        self.assertEqual(prov["text_layer"], "原注")


class AssembledProviderReplayTest(unittest.TestCase):
    def test_replay_matches_golden_anchors(self) -> None:
        for year_key, year in (("2024", 2024), ("1987", 1987)):
            window = GOLDEN["jie_windows"][year_key]
            for term, key in (("立春", "lichun"), ("惊蛰", "next_jie")):
                replayed = _provider_jie_instant(year, term)
                claimed = datetime.fromisoformat(window[key]["at"])
                self.assertEqual(replayed, claimed, (year_key, term))

    def test_2024_lichun_matches_frozen_minute_reference(self) -> None:
        # TJ-015.2 frozen JPL-cited reference: 2024 立春 published at
        # 2024-02-04T08:27:00Z (minute precision). The provider replay
        # must agree at minute precision and carry :07 seconds.
        replayed = _provider_jie_instant(2024, "立春")
        self.assertEqual(replayed.astimezone(ZoneInfo("UTC")).isoformat(),
                         "2024-02-04T08:27:07+00:00")
        self.assertEqual(replayed.replace(second=0).isoformat(),
                         "2024-02-04T16:27:00+08:00")


class RealBirthEndToEndTest(unittest.TestCase):
    def test_real_birth_in_yin_window(self) -> None:
        # Real birth instant 2024-02-10 03:00 +08:00. Hand derivation:
        # month pillar after 立春 in 甲辰 year is 丙寅 (寅月); elapsed
        # since t0 = 5d 10h 32m 53s < 7d -> first segment 戊.
        birth = datetime(2024, 2, 10, 3, 0, 0, tzinfo=CHINA)
        cal = calendar(birth)
        self.assertEqual(cal["month_ganzhi"], "丙寅")
        out = yin_siling_pilot(birth, version_id="ditiansui-yuanshuo",
                               jie_facts=_facts("2024"))
        self.assertEqual(out["status"], "computed")
        self.assertEqual(out["commander"], "戊")
        self.assertEqual(out["elapsed_seconds"],
                         5 * 86400 + 10 * 3600 + 32 * 60 + 53)
        self.assertEqual(out["month_branch"], "寅")

    def test_golden_table_reruns_in_assembled_env(self) -> None:
        for case in GOLDEN["cases"]:
            window = GOLDEN["jie_windows"][case["window"]]
            facts = {"provider": dict(GOLDEN["provider"]),
                     "lichun": dict(window["lichun"]),
                     "next_jie": dict(window["next_jie"])}
            override = case.get("jie_override") or {}
            if override.get("drop_next_jie"):
                facts.pop("next_jie")
            if "lichun_at" in override:
                facts["lichun"]["at"] = override["lichun_at"]
            if "lichun_precision" in override:
                facts["lichun"]["precision"] = override["lichun_precision"]
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
                out = yin_siling_pilot(
                    case["birth"], version_id=case["version_id"],
                    jie_facts=facts,
                    birth_time_precision=case.get(
                        "birth_time_precision", "second"))
                self.assertEqual(out["status"], case["expected_status"])
                self.assertEqual(out["commander"],
                                 case["expected_commander"])


if __name__ == "__main__":
    unittest.main()
