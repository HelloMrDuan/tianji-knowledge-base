"""TJ-018-H 公开结构测试：三命 66 条零匹配订正归因登记册。

本模块（``bazi_sanming_zero_match_attribution``）是纯数据归因
登记册、零计算逻辑；本测试只钉登记形制与归因红线（66 条分类
计数自洽、逐条差异解释完备、材料依赖文件序在先、长锚摘要口径、
「只归因未应用」状态、Golden 镜像逐字一致），不验证任何订正
应用（不存在此种代码路径）。逐条证据对密封快照与密封订正
JSON 的复核在密封专项
``tests/test_tj018h_sanming_zero_match_sealed.py``（仅离线验收）。
"""

from __future__ import annotations

import hashlib
import inspect
import json
import re
import unittest
from collections import Counter
from pathlib import Path

from tianji_kb import bazi_sanming_zero_match_attribution as zm

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / "tests" / "golden_tj018h_sanming_zero_match.json").read_text(
        encoding="utf-8"))

CATEGORIES = {"missing_glyph_context", "chain_dependency",
              "base_text_drift", "unresolved"}
PUA_TAG = re.compile(r"^pua_(mapping|contextual):(U\+[0-9A-F]{4,6})(#\d+)?$")
CORR_TAG = re.compile(r"^correction:(ocr-\d{3})$")
CORRECTION_ID = re.compile(r"^ocr-(\d{3})$")


def _is_pua(ch: str) -> bool:
    cp = ord(ch)
    return (0xE000 <= cp <= 0xF8FF or 0xF0000 <= cp <= 0xFFFFD
            or 0x100000 <= cp <= 0x10FFFD)


def _anchor_len(entry: dict, key: str) -> int:
    return entry[key + "_digest"]["length"]


class RegisterShapeTest(unittest.TestCase):
    def test_module_is_pure_data(self) -> None:
        callables = [name for name, value in vars(zm).items()
                     if callable(value) and not name.startswith("__")]
        self.assertEqual(callables, [])
        self.assertFalse(inspect.getsource(zm).count("def "))

    def test_register_identity_and_status(self) -> None:
        self.assertEqual(zm.ATTRIBUTION_REGISTER_ID,
                         "sanming-zero-match-attribution-register-v1")
        self.assertEqual(zm.ATTRIBUTION_TASK, "TJ-018-H")
        # 只归因、未应用：状态常量不得被读作已应用
        self.assertEqual(zm.APPLICATION_STATUS,
                         "attribution_only_not_applied")
        meta = zm.ATTRIBUTION_SNAPSHOTS["sanming_tonghui.txt"]
        self.assertEqual(meta["chars"], 461157)
        self.assertEqual(meta["bytes"], 1342659)
        self.assertTrue(meta["sha256"].startswith("00e2a7db"))

    def test_pipeline_baseline_self_consistent(self) -> None:
        base = zm.PIPELINE_BASELINE
        tc = base["text_collation"]
        self.assertEqual(tc["corrections_total"], 603)
        self.assertEqual(tc["exact_once_in_snapshot"]
                         + tc["zero_match_in_snapshot"], 603)
        self.assertEqual(tc["more_than_once_in_snapshot"], 0)
        self.assertEqual(base["pua_stage"]["remaining_after"], 0)
        self.assertEqual(base["staged_replay"]["applied"], 603)
        self.assertEqual(base["staged_replay"]["anomalies"], 0)
        fang = base["fang"]
        self.assertEqual(fang["in_snapshot"]
                         - fang["net_removed_by_full_application"],
                         fang["remaining_after_full_application"])

    def test_category_counts_sum_to_66(self) -> None:
        self.assertEqual(zm.CATEGORY_COUNTS,
                         {"missing_glyph_context": 41,
                          "chain_dependency": 25,
                          "base_text_drift": 0,
                          "unresolved": 0})
        actual = Counter(e["category"] for e in zm.ZERO_MATCH_ENTRIES)
        full = {c: actual.get(c, 0) for c in CATEGORIES}
        self.assertEqual(full, zm.CATEGORY_COUNTS)
        self.assertEqual(sum(full.values()), 66)
        self.assertEqual(len(zm.ZERO_MATCH_ENTRIES), 66)


class EntryFormTest(unittest.TestCase):
    def test_ids_unique_and_sequential(self) -> None:
        ids = [e["id"] for e in zm.ZERO_MATCH_ENTRIES]
        self.assertEqual(ids, ["zm-%03d" % i for i in range(1, 67)])
        cids = [e["correction_id"] for e in zm.ZERO_MATCH_ENTRIES]
        self.assertEqual(len(set(cids)), 66)
        nums = [int(CORRECTION_ID.match(c).group(1)) for c in cids]
        self.assertEqual(nums, sorted(nums))
        for n in nums:
            self.assertTrue(1 <= n <= 603)

    def test_anchor_registration_form(self) -> None:
        for e in zm.ZERO_MATCH_ENTRIES:
            for key in ("old", "new"):
                digest = e[key + "_digest"]
                self.assertEqual(len(digest["sha256"]), 64)
                int(digest["sha256"], 16)
                verbatim = e[key]
                if verbatim is None:
                    # 长锚只登记摘要：长度 >60、首尾各 24 字
                    self.assertGreater(digest["length"], 60, e["id"])
                    self.assertEqual(len(digest["head"]), 24)
                    self.assertEqual(len(digest["tail"]), 24)
                else:
                    self.assertLessEqual(len(verbatim), 60, e["id"])
                    self.assertEqual(digest["length"], len(verbatim))
                    self.assertEqual(
                        digest["sha256"],
                        hashlib.sha256(verbatim.encode("utf-8")).hexdigest())
                    self.assertEqual(digest["head"], verbatim[:24])
                    self.assertEqual(digest["tail"], verbatim[-24:])
            self.assertEqual(e["sealed_status"], "confirmed")
            self.assertTrue(e["evidence_repos"], e["id"])

    def test_site_matches_anchor_length(self) -> None:
        for e in zm.ZERO_MATCH_ENTRIES:
            site = e["site"]
            self.assertEqual(site["char_end"] - site["char_start"],
                             _anchor_len(e, "old"), e["id"])
            self.assertGreaterEqual(site["char_start"], 0)
            self.assertLessEqual(site["char_end"], 461157)

    def test_diffs_complete_and_explained(self) -> None:
        total = 0
        kinds = Counter()
        for e in zm.ZERO_MATCH_ENTRIES:
            diffs = e["diffs"]
            self.assertGreaterEqual(len(diffs), 1, e["id"])
            offsets = [d["offset"] for d in diffs]
            self.assertEqual(offsets, sorted(set(offsets)), e["id"])
            for d in diffs:
                total += 1
                self.assertLess(d["offset"], _anchor_len(e, "old"))
                self.assertNotEqual(d["snapshot_char"], d["old_char"])
                tag = d["explained_by"]
                mp = PUA_TAG.match(tag)
                mc = CORR_TAG.match(tag)
                self.assertTrue(mp or mc, (e["id"], tag))
                if mp:
                    kinds["pua"] += 1
                    # PUA 解释的差异位点：快照侧必为 PUA 字且码位对齐
                    self.assertTrue(_is_pua(d["snapshot_char"]), e["id"])
                    self.assertEqual(d["snapshot_codepoint"],
                                     mp.group(2).replace("U+", "U+"))
                    self.assertEqual(
                        "U+%04X" % ord(d["snapshot_char"]),
                        d["snapshot_codepoint"])
                else:
                    kinds["correction"] += 1
                    self.assertIn(mc.group(1),
                                  e["dependencies"]["corrections"], e["id"])
                    self.assertFalse(_is_pua(d["snapshot_char"]), e["id"])
                    self.assertIsNone(d["snapshot_codepoint"])
        self.assertEqual(total, 74)
        self.assertEqual(kinds, {"pua": 47, "correction": 27})

    def test_dependencies_consistent_with_category(self) -> None:
        for e in zm.ZERO_MATCH_ENTRIES:
            deps = e["dependencies"]
            pua_from_diffs = sorted({
                PUA_TAG.match(d["explained_by"]).group(2)
                for d in e["diffs"] if PUA_TAG.match(d["explained_by"])})
            self.assertEqual(deps["pua_codepoints"], pua_from_diffs,
                             e["id"])
            my_num = int(CORRECTION_ID.match(e["correction_id"]).group(1))
            for dep in deps["corrections"]:
                # 材料依赖恒为文件序在先条目（编号即文件序）
                self.assertLess(int(CORRECTION_ID.match(dep).group(1)),
                                my_num, e["id"])
            if e["category"] == "missing_glyph_context":
                self.assertEqual(deps["corrections"], [], e["id"])
                self.assertGreaterEqual(len(deps["pua_codepoints"]), 1,
                                        e["id"])
            if e["category"] == "chain_dependency":
                self.assertGreaterEqual(len(deps["corrections"]), 1,
                                        e["id"])
            self.assertEqual(e["disposition"],
                             "applicable_in_documented_pipeline_order")

    def test_module_matches_golden(self) -> None:
        self.assertEqual(GOLDEN["register_id"], zm.ATTRIBUTION_REGISTER_ID)
        self.assertEqual(GOLDEN["application_status"],
                         zm.APPLICATION_STATUS)
        self.assertEqual(GOLDEN["pipeline_baseline"], zm.PIPELINE_BASELINE)
        self.assertEqual(GOLDEN["category_counts"], zm.CATEGORY_COUNTS)
        self.assertEqual(
            json.loads(json.dumps(zm.ZERO_MATCH_ENTRIES,
                                  ensure_ascii=False)),
            GOLDEN["entries"])


if __name__ == "__main__":
    unittest.main()
