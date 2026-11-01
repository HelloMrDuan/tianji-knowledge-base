"""TJ-025.2 (E0362): life-overview dayun exit copy matches registered facts.

The E0358 remainder audit (§8) found the integrated_reading dayun exit
sentence stale after the E0346/E0348 dayun registrations: direction and
start-of-luck conversions already have registered Phase1 rules, validated
Phase2 steps and Golden cases, while luck-cycle efficacy remains unbuilt
and the overview composition remains unapproved. These public pins assert
the corrected wording verbatim and guard the no-logic-change boundary
(flags and reason category untouched, registration never worded as public
opening). Source-text pins are used because the wording is built inside
_life(), whose end-to-end run needs the sealed runtime (offline
acceptance); the sealed marker suite covers the live consistency.

Assembly guard (E0360 precedent): the assembled backend tree has no
web/ directory by construction, so the frontend sweep below skips
honestly there and runs in full on real checkouts (public CI / local);
the E0359 batch's unguarded web read failed the pipeline acceptance
four times before this guard pattern was established.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = (ROOT / "src" / "tianji_kb" / "scenario_engine.py").read_text(
    encoding="utf-8")
DAYUN_CLASSICAL = (
    ROOT / "src" / "tianji_kb" / "bazi_dayun_classical.py").read_text(
    encoding="utf-8")

OLD_DAYUN = ("大运方向、起运岁数、交运日期及岁运效力尚无完成审核的生产规则，"
             "本总览不推算或伪造大运时间线。")
NEW_DAYUN = ("大运方向与起运换算已有完成审核的注册规则（方向据三命分段；"
             "起运换算有三命、神峰两套口径分别注册，只给出交运时刻区间，"
             "不折算单点岁数或日期），但尚未批准接入本总览；"
             "岁运效力仍无完成审核的生产规则，本总览不推算或伪造大运时间线。")


class DayunCopyE0362Tests(unittest.TestCase):
    def test_new_wording_present_verbatim_in_engine_source(self):
        chunks = re.findall(r'"([^"]*)"', ENGINE)
        joined = "".join(chunks)
        self.assertIn(NEW_DAYUN, joined)

    def test_old_wording_absent_from_engine(self):
        self.assertNotIn(OLD_DAYUN, ENGINE)

    def test_old_wording_absent_from_frontend(self):
        web_src = ROOT / "web" / "visual-prototype" / "src"
        if not web_src.is_dir():
            self.skipTest(
                "web tree not present in assembled backend; this pin "
                "runs on real checkouts (public CI / local)")
        for path in web_src.rglob("*"):
            if path.is_file() and path.suffix in (".ts", ".tsx"):
                self.assertNotIn(
                    OLD_DAYUN, path.read_text(encoding="utf-8"), str(path))

    def test_registered_and_unbuilt_faces_are_distinguished(self):
        self.assertIn("大运方向与起运换算已有完成审核的注册规则", NEW_DAYUN)
        self.assertIn("只给出交运时刻区间，不折算单点岁数或日期", NEW_DAYUN)
        self.assertIn("岁运效力仍无完成审核的生产规则", NEW_DAYUN)

    def test_not_open_substance_is_preserved(self):
        # Registration must never be worded as public opening or wiring.
        self.assertIn("但尚未批准接入本总览", NEW_DAYUN)
        self.assertIn("本总览不推算或伪造大运时间线。", NEW_DAYUN)
        for forbidden in ("已接入本总览", "已开放", "现已提供大运时间线"):
            self.assertNotIn(forbidden, NEW_DAYUN)

    def test_registration_facts_behind_the_wording_exist(self):
        # The wording's claim rests on the in-repo registration record:
        # Sanming direction + conversion and Shenfeng conversion steps.
        for step in ("bazi.phase2.dayun_classical_direction",
                     "bazi.phase2.dayun_sanming_conversion",
                     "bazi.phase2.dayun_shenfeng_conversion"):
            self.assertIn(step, DAYUN_CLASSICAL)

    def test_no_logic_change_boundary_flags_and_reason_category(self):
        # The composition flags stay hard-coded False and the dayun marker
        # keeps its reason category: this batch changes wording only.
        self.assertEqual(
            ENGINE.count('"dayun_timeline_approved": False'), 2)
        self.assertIn('"no_approved_production_rule"', ENGINE)
        self.assertIn("dayun_timeline_approved", ENGINE)


if __name__ == "__main__":
    unittest.main()
