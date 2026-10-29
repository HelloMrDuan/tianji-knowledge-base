"""TJ-018.3 晋级 P2 残余「防」处置登记册公开结构测试（不依赖密封资产）。

只核对登记册自身的形制、盘点完备性、分类计数对账、处置规则
与与既有公开登记册（应用记录）的交叉一致；769 位点对密封
原文的全量复核与密封文件逐字未动验证在密封专项
``test_tj0183_sanming_fang_disposition_sealed`` 中执行。
首批（E0302）43 条处置与 769 行盘点（除 disposition 字段）
以规范化 JSON 哈希钉断言逐字不变；第二分册（E0304）为卷首/
卷一/卷二/卷三节外 86 处；第三分册（E0306）为卷四节外
118 处，前两册 129 条处置另以哈希钉断言逐字不变；第四
分册（E0308）为卷五节外 65 处（RD-12 两处只标记未处置），
前三册 247 条处置另以哈希钉断言逐字不变；第五分册
（E0310）为卷六节外 130 处，前四册 312 条处置另以哈希钉
断言逐字不变；第六分册（E0312）为卷七节外 73 处（RD-12
两处只标记未处置），前五册 442 条处置另以哈希钉断言逐字
不变；第七分册（E0314）为卷八节外 61 处（本册无 RD-12
标记位点），前六册 515 条处置另以哈希钉断言逐字不变；
第八分册（E0316）为卷九 94 处（本册无 RD-12 标记位点），
前七册 576 条处置另以哈希钉断言逐字不变；第九分册（E0318）
为卷十 25 处（另 RD-12 seq 824 一处只标记未处置），前八册
670 条处置另以哈希钉断言逐字不变；第十分册（E0320）
为卷十一 43 处（另 RD-12 seq 873/933 两处只标记未处置），
前九册 695 条处置另以哈希钉断言逐字不变；第十一分册
（E0322，末册）为卷十二 24 处（本册无 RD-12 标记位点），
前十册 738 条处置另以哈希钉断言逐字不变；P2 收官后
pending 恰 7 处、全为 RD-12 只标记位点（归 P3）。
"""
from __future__ import annotations

import ast
import hashlib
import json
import unittest
from collections import Counter
from pathlib import Path

from tianji_kb import bazi_sanming_application_record as ar
from tianji_kb import bazi_sanming_fang_disposition as fd

ROOT = Path(__file__).resolve().parents[1]
REG = fd.FANG_DISPOSITION_REGISTER
INV = REG["inventory"]
DISP = REG["dispositions"]
SIKU = {"kanripo/KR3g0042", "mikkokotila/Sanming-Tongshui"}
MODERN = {"NiuTrans/Classical-Modern", "youngzs/xuanxue"}
ALL_WIT = SIKU | MODERN | {"Banny-Gao"}

# 首批（E0302）冻结钉：43 条节内处置的规范化 JSON 哈希，与
# 769 行盘点去掉 disposition 字段后的规范化 JSON 哈希。
BATCH1_DISP_SHA256 = ("ca860d0877eef2ceb71b8c068ac0e8d91345b7124e74e05776c846a5"
                      "564b1ac1")
INVENTORY_NODISP_SHA256 = ("2f131ab4bedd9123dc717e1e4ea1ce32f0cbd695d55e725c"
                           "4d6f912a72f00b89")
# 前两册（E0302+E0304）冻结钉：129 条处置的规范化 JSON 哈希
# （第三分册 118 条以所在卷为卷四区分，余者皆属前两册）。
BATCH12_DISP_SHA256 = ("f4001f499988c3736cea45633b46430d66d330992d7bb607dd53"
                       "c4a420ae8b7c")
# 前三册（E0302+E0304+E0306）冻结钉：247 条处置的规范化
# JSON 哈希（第四分册 65 条以所在卷为卷五且原 pending 区分，
# 余者皆属前三册；卷五另有首批节内 22 条属前三册，以 s0
# 位点集合区分，见 test_batch123_entries_verbatim）。
BATCH123_DISP_SHA256 = ("a690ecaaafe846a2c450ffadb5d9171594f5aef881179a56e6db"
                        "95c62350d1c8")
# 第四分册（E0308）范围：卷五节外 65 处 s0 位点（基线盘点
# 中卷五 pending 且非 RD-12 者；RD-12 seq 361/385 两处不在
# 其内、保持 pending）。
BATCH4_S0 = frozenset({
    148636, 149947, 151346, 152142, 152155, 152818, 153455,
    153460, 154979, 155128, 155245, 155477, 155929, 155935,
    156199, 156244, 156287, 156463, 156677, 157717, 158217,
    158886, 158895, 158928, 158933, 158954, 158967, 159009,
    161345, 162241, 163028, 164471, 165134, 165323, 168046,
    168059, 168151, 168165, 168336, 168345, 168392, 168616,
    168901, 169057, 169415, 169702, 169719, 170550, 170739,
    174934, 174940, 175574, 177088, 177441, 177497, 177601,
    177885, 178901, 178980, 179218, 179225, 180330, 185380,
    185427, 185571})
assert len(BATCH4_S0) == 65
# 前四册（E0302+E0304+E0306+E0308）冻结钉：312 条处置的
# 规范化 JSON 哈希（第五分册 130 条以 s0 位点集合区分，
# 见 test_batch1234_entries_verbatim）。
BATCH1234_DISP_SHA256 = ("125ea32474526aa3d32a4e26f96a5ff3e642820660e28a6745ea6d332b17d261")
# 第五分册（E0310）范围：卷六节外 130 处 s0 位点（基线盘点
# 中卷六 pending 全部；本册无 RD-12 标记位点）。
BATCH5_S0 = frozenset({
    186546, 186868, 188010, 188121, 188556, 190153, 190231,
    190310, 190362, 190368, 191038, 191139, 191539, 191588,
    191677, 191748, 192407, 192941, 193151, 193167, 193388,
    194156, 194973, 195008, 195064, 195327, 195439, 195455,
    195582, 195826, 195875, 196506, 196566, 196833, 197319,
    197387, 197418, 197792, 198182, 199534, 199922, 200125,
    200250, 200270, 200308, 200355, 200656, 200755, 200907,
    201279, 201433, 201737, 201982, 202407, 202426, 204968,
    205003, 206113, 206432, 206912, 206914, 206964, 207016,
    207031, 207125, 207301, 207881, 208378, 209533, 209567,
    209934, 209946, 210336, 210341, 210379, 210384, 210385,
    210386, 210398, 210407, 210408, 210475, 210542, 210543,
    210563, 210598, 210602, 210603, 210625, 210626, 210631,
    210639, 210729, 210747, 210755, 210969, 211443, 211515,
    212168, 212273, 215083, 215112, 215146, 215436, 215943,
    216120, 216144, 216311, 216583, 216903, 216936, 217138,
    217538, 217607, 217825, 218222, 218248, 218268, 218483,
    219341, 219613, 219724, 220294, 220335, 220740, 222434,
    222445, 222451, 222477, 222482})
assert len(BATCH5_S0) == 130
# 前五册（E0302+E0304+E0306+E0308+E0310）冻结钉：442 条
# 处置的规范化 JSON 哈希（第六分册 73 条以 s0 位点集合
# 区分，见 test_batch12345_entries_verbatim）。
BATCH12345_DISP_SHA256 = ("e2019b3c1eec12c82df4472bae2bb8e8f30c4d55293fb073fbad978b2a8dfe7a")
# 第六分册（E0312）范围：卷七节外 73 处 s0 位点（基线盘点
# 中卷七 pending 75 处除 RD-12 seq 612/616 两处；两处不在
# 其内、保持 pending）。
BATCH6_S0 = frozenset({
    224376, 224675, 224850, 225847, 225897, 225973, 226603,
    226776, 228279, 229609, 230807, 231562, 231925, 231941,
    232186, 232236, 232270, 232756, 233403, 233591, 234350,
    234482, 234690, 235844, 237421, 237551, 238198, 238904,
    239945, 240039, 240732, 240764, 241205, 241543, 241949,
    242271, 242735, 243741, 243743, 243751, 244900, 245316,
    245865, 245945, 247070, 249493, 249527, 249740, 249858,
    250055, 250060, 250069, 250086, 250123, 250176, 252612,
    252646, 252754, 253118, 253633, 253787, 253828, 253836,
    254033, 254311, 255513, 255579, 255601, 255774, 256186,
    256217, 256997, 257500})
assert len(BATCH6_S0) == 73
# 前六册（E0302+E0304+E0306+E0308+E0310+E0312）冻结钉：
# 515 条处置的规范化 JSON 哈希（第七分册 61 条以 s0 位点
# 集合区分，见 test_batch123456_entries_verbatim）。
BATCH123456_DISP_SHA256 = ("11ac8fa1844a50c4158dba36be93e910c565976d2cca2a979105c31bac7616e3")
# 第七分册（E0314）范围：卷八节外 61 处 s0 位点（基线盘点
# 中卷八 pending 全部；本册无 RD-12 标记位点）。
BATCH7_S0 = frozenset({
    257537, 258500, 260023, 260367, 261108, 261130, 261144,
    261979, 262582, 262695, 263353, 263422, 263635, 264033,
    266498, 267631, 268463, 269097, 270849, 270885, 271013,
    271305, 271629, 272104, 272529, 273955, 274978, 276317,
    277068, 277313, 277562, 278647, 278876, 279203, 280259,
    282582, 282829, 283464, 283476, 283513, 283949, 284528,
    284532, 287004, 288515, 289183, 289512, 289737, 289986,
    291757, 292646, 293312, 293451, 294653, 294747, 297467,
    300970, 301363, 302090, 302489, 305444})
assert len(BATCH7_S0) == 61
# 第七分册 kanripo bracket 名录栏式编排致未定位的 18 处
# （候选只据 mikkokotila 一家、一律 deferred）。
KAN_MISSING7_S0 = frozenset({
    260367, 261108, 261144, 266498, 269097, 274978, 277068,
    279203, 282829, 283513, 288515, 289512, 291757, 292646,
    293451, 294747, 300970, 302090})
assert len(KAN_MISSING7_S0) == 18
assert KAN_MISSING7_S0 <= BATCH7_S0
# 前七册（E0302+E0304+E0306+E0308+E0310+E0312+E0314）冻结钉：
# 576 条处置的规范化 JSON 哈希（第八分册 94 条以 s0 位点
# 集合区分，见 test_batch1234567_entries_verbatim）。
BATCH1234567_DISP_SHA256 = ("28ef4dfe285d517f33d51a889a25a6b778fb6de9a8374ca8d7f16ff04a57dbbf")
# 第八分册（E0316）范围：卷九 94 处 s0 位点（基线盘点中
# 卷九 pending 全部；本册无 RD-12 标记位点）。
BATCH8_S0 = frozenset({
    306793, 308023, 308097, 308163, 308909, 309094, 309452,
    310836, 311149, 311221, 311961, 313059, 313709, 314836,
    314956, 314963, 315136, 315277, 316742, 316806, 318003,
    318098, 320174, 321164, 321649, 322031, 322065, 322401,
    322525, 322739, 322977, 322982, 323287, 323349, 324615,
    324699, 324706, 324983, 325074, 325173, 325177, 325426,
    325758, 326785, 326924, 327205, 327474, 327805, 328001,
    329898, 330666, 331330, 332658, 332677, 332797, 332813,
    333768, 333959, 334348, 334475, 334733, 334739, 334772,
    335227, 335989, 336503, 337747, 338002, 338051, 339003,
    340074, 341431, 342011, 342584, 342858, 343797, 343964,
    344416, 344470, 344550, 345494, 345647, 345811, 345929,
    346053, 346439, 347559, 347576, 348711, 348962, 349212,
    350711, 351535, 352663})
assert len(BATCH8_S0) == 94
# 第八分册 kanripo 未定位的 32 处（多位于 bracket 名录
# 条目内，候选只据 mikkokotila 一家、一律 deferred）。
KAN_MISSING8_S0 = frozenset({
    306793, 309094, 309452, 315277, 318098, 320174, 321649,
    322401, 322977, 322982, 323349, 325074, 325426, 325758,
    326785, 326924, 327205, 332658, 332813, 334348, 334733,
    334739, 335989, 338002, 339003, 340074, 342584, 342858,
    343797, 345811, 347559, 349212})
assert len(KAN_MISSING8_S0) == 32
assert KAN_MISSING8_S0 <= BATCH8_S0
# 前八册（E0302+E0304+E0306+E0308+E0310+E0312+E0314+E0316）
# 冻结钉：670 条处置的规范化 JSON 哈希（第九分册 25 条以
# s0 位点集合区分，见 test_batch12345678_entries_verbatim）。
BATCH12345678_DISP_SHA256 = ("659be91d447ffa3a05a9b4f2a7c482627f24afd42b854f2545e8ccd1c0b7e9da")
# 第九分册（E0318）范围：卷十 25 处 s0 位点（基线盘点中
# 卷十 pending 且非 RD-12 者；RD-12 seq 824 一处不在其内、
# 保持 pending）。
BATCH9_S0 = frozenset({
    352700, 352714, 357674, 358009, 358300, 359024, 362550,
    363439, 366079, 368063, 368737, 369196, 369493, 369729,
    372338, 372482, 373161, 373533, 374543, 377126, 378807,
    378862, 380626, 384318, 386900})
assert len(BATCH9_S0) == 25
# 第九分册 RD-12 只标记位点（seq 824，保持 pending 归 P3）。
RD12_JUAN10_S0 = 374132
# 前九册（E0302+E0304+E0306+E0308+E0310+E0312+E0314+E0316
# +E0318）冻结钉：695 条处置的规范化 JSON 哈希（第十分册
# 43 条以 s0 位点集合区分，见
# test_batch123456789_entries_verbatim）。
BATCH123456789_DISP_SHA256 = ("ecc00d441a61cc7dbcbda709e6d7f68bb205aa09f2f7e71d3edf5efcc2c4c090")
# 第十分册（E0320）范围：卷十一 43 处 s0 位点（基线盘点中
# 卷十一 pending 且非 RD-12 者；RD-12 seq 873/933 两处不
# 在其内、保持 pending）。
BATCH10_S0 = frozenset({
    386937, 388136, 389304, 389379, 389786, 390420, 390493,
    391492, 391957, 392037, 393341, 396327, 399255, 399924,
    400798, 401868, 403390, 404534, 404659, 404668, 404742,
    404744, 404765, 404767, 404910, 405895, 406120, 406160,
    410323, 410412, 411336, 411566, 411652, 412299, 414636,
    416841, 416928, 422162, 425202, 425892, 426461, 430415,
    431900})
assert len(BATCH10_S0) == 43
# 第十分册 RD-12 只标记位点（seq 873/933，保持 pending 归 P3）。
RD12_JUAN11_S0 = frozenset({395587, 423787})
# 前十册（E0302+E0304+E0306+E0308+E0310+E0312+E0314+E0316
# +E0318+E0320）冻结钉：738 条处置的规范化 JSON 哈希
# （第十一分册 24 条以 s0 位点集合区分，见
# test_batch12345678910_entries_verbatim）。
BATCH12345678910_DISP_SHA256 = ("459d16bdbdea8d5a3ee5d255c617c8ca3f12fe85f"
                                "5c22889dec7ff974a380c73")
# 第十一分册（E0322，末册）范围：卷十二 24 处 s0 位点
# （基线盘点中卷十二 pending 全部；本册无 RD-12 位点）。
BATCH11_S0 = frozenset({
    431938, 436495, 439050, 442799, 442962, 444391, 448977,
    448985, 449551, 449851, 451826, 452418, 452422, 452620,
    452817, 455285, 455290, 455405, 457635, 459587, 460125,
    460336, 460492, 461152})
assert len(BATCH11_S0) == 24
# P2 收官后 pending 全集：7 处 RD-12 只标记位点（归 P3）。
RD12_PENDING_S0 = frozenset({157779, 164133, 228261, 228869,
                             374132, 395587, 423787})


def _canon_sha(obj) -> str:
    return hashlib.sha256(
        json.dumps(obj, ensure_ascii=False, sort_keys=True)
        .encode("utf-8")).hexdigest()


class TestFangDispositionPublic(unittest.TestCase):
    def test_golden_mirror(self):
        golden = json.loads(
            (ROOT / "tests" / "golden_tj0183_sanming_fang_disposition.json")
            .read_text(encoding="utf-8"))
        self.assertEqual(golden, REG)

    def test_register_is_pure_data(self):
        tree = ast.parse(Path(fd.__file__).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            self.assertNotIsInstance(
                node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        self.assertEqual(REG["ledger_event"], "E0322")
        self.assertEqual(REG["ledger_events"], ["E0302", "E0304", "E0306", "E0308", "E0310", "E0312", "E0314", "E0316", "E0318", "E0320", "E0322"])
        self.assertEqual(REG["ledger_row"], "TJ-018.2")
        self.assertEqual(
            REG["baseline_main_sha"],
            "27bd2238bfa07778896c4f3431cf1eba4be6eaff")
        self.assertEqual(
            REG["register_id"],
            "sanming-residual-fang-disposition-register-v1")

    def test_batch1_entries_verbatim(self):
        in_section = sorted((d for d in DISP
                             if d["section_id"] is not None),
                            key=lambda d: d["s0_offset"])
        self.assertEqual(len(in_section), 43)
        self.assertEqual(_canon_sha(in_section), BATCH1_DISP_SHA256)
        nodisp = [{k: v for k, v in x.items() if k != "disposition"}
                  for x in INV]
        self.assertEqual(_canon_sha(nodisp), INVENTORY_NODISP_SHA256)

    def test_batch12_entries_verbatim(self):
        by_s0 = {x["s0_offset"]: x for x in INV}
        prior = sorted((d for d in DISP
                        if by_s0[d["s0_offset"]]["volume"] != "卷四"
                        and d["s0_offset"] not in BATCH4_S0
                        and d["s0_offset"] not in BATCH5_S0
                        and d["s0_offset"] not in BATCH6_S0
                        and d["s0_offset"] not in BATCH7_S0
                        and d["s0_offset"] not in BATCH8_S0
                        and d["s0_offset"] not in BATCH9_S0
                        and d["s0_offset"] not in BATCH10_S0
                        and d["s0_offset"] not in BATCH11_S0),
                       key=lambda d: d["s0_offset"])
        self.assertEqual(len(prior), 129)
        self.assertEqual(_canon_sha(prior), BATCH12_DISP_SHA256)

    def test_batch123_entries_verbatim(self):
        # 前三册 247 条 = 全部处置减去第四分册冻结位点集
        # BATCH4_S0（65 条）；本册范围另由 test_tranche4_scope
        # 以卷/分类计数锁定。
        prior = sorted((d for d in DISP
                        if d["s0_offset"] not in BATCH4_S0
                        and d["s0_offset"] not in BATCH5_S0
                        and d["s0_offset"] not in BATCH6_S0
                        and d["s0_offset"] not in BATCH7_S0
                        and d["s0_offset"] not in BATCH8_S0
                        and d["s0_offset"] not in BATCH9_S0
                        and d["s0_offset"] not in BATCH10_S0
                        and d["s0_offset"] not in BATCH11_S0),
                       key=lambda d: d["s0_offset"])
        self.assertEqual(len(prior), 247)
        self.assertEqual(_canon_sha(prior), BATCH123_DISP_SHA256)

    def test_batch1234_entries_verbatim(self):
        # 前四册 312 条 = 全部处置减去第五分册冻结位点集
        # BATCH5_S0（130 条）；本册范围另由 test_tranche5_scope
        # 以卷/分类计数锁定。
        prior = sorted((d for d in DISP
                        if d["s0_offset"] not in BATCH5_S0
                        and d["s0_offset"] not in BATCH6_S0
                        and d["s0_offset"] not in BATCH7_S0
                        and d["s0_offset"] not in BATCH8_S0
                        and d["s0_offset"] not in BATCH9_S0
                        and d["s0_offset"] not in BATCH10_S0
                        and d["s0_offset"] not in BATCH11_S0),
                       key=lambda d: d["s0_offset"])
        self.assertEqual(len(prior), 312)
        self.assertEqual(_canon_sha(prior), BATCH1234_DISP_SHA256)

    def test_batch12345_entries_verbatim(self):
        # 前五册 442 条 = 全部处置减去第六分册冻结位点集
        # BATCH6_S0（73 条）；本册范围另由 test_tranche6_scope
        # 以卷/分类计数锁定。
        prior = sorted((d for d in DISP
                        if d["s0_offset"] not in BATCH6_S0
                        and d["s0_offset"] not in BATCH7_S0
                        and d["s0_offset"] not in BATCH8_S0
                        and d["s0_offset"] not in BATCH9_S0
                        and d["s0_offset"] not in BATCH10_S0
                        and d["s0_offset"] not in BATCH11_S0),
                       key=lambda d: d["s0_offset"])
        self.assertEqual(len(prior), 442)
        self.assertEqual(_canon_sha(prior), BATCH12345_DISP_SHA256)

    def test_batch123456_entries_verbatim(self):
        # 前六册 515 条 = 全部处置减去第七分册冻结位点集
        # BATCH7_S0（61 条）；本册范围另由 test_tranche7_scope
        # 以卷/分类计数锁定。
        prior = sorted((d for d in DISP
                        if d["s0_offset"] not in BATCH7_S0
                        and d["s0_offset"] not in BATCH8_S0
                        and d["s0_offset"] not in BATCH9_S0
                        and d["s0_offset"] not in BATCH10_S0
                        and d["s0_offset"] not in BATCH11_S0),
                       key=lambda d: d["s0_offset"])
        self.assertEqual(len(prior), 515)
        self.assertEqual(_canon_sha(prior), BATCH123456_DISP_SHA256)

    def test_batch1234567_entries_verbatim(self):
        # 前七册 576 条 = 全部处置减去第八分册冻结位点集
        # BATCH8_S0（94 条）；本册范围另由 test_tranche8_scope
        # 以卷/分类计数锁定。
        prior = sorted((d for d in DISP
                        if d["s0_offset"] not in BATCH8_S0
                        and d["s0_offset"] not in BATCH9_S0
                        and d["s0_offset"] not in BATCH10_S0
                        and d["s0_offset"] not in BATCH11_S0),
                       key=lambda d: d["s0_offset"])
        self.assertEqual(len(prior), 576)
        self.assertEqual(_canon_sha(prior), BATCH1234567_DISP_SHA256)

    def test_batch12345678_entries_verbatim(self):
        # 前八册 670 条 = 全部处置减去第九分册冻结位点集
        # BATCH9_S0（25 条）；本册范围另由 test_tranche9_scope
        # 以卷/分类计数锁定。
        prior = sorted((d for d in DISP
                        if d["s0_offset"] not in BATCH9_S0
                        and d["s0_offset"] not in BATCH10_S0
                        and d["s0_offset"] not in BATCH11_S0),
                       key=lambda d: d["s0_offset"])
        self.assertEqual(len(prior), 670)
        self.assertEqual(_canon_sha(prior), BATCH12345678_DISP_SHA256)

    def test_batch123456789_entries_verbatim(self):
        # 前九册 695 条 = 全部处置减去第十分册冻结位点集
        # BATCH10_S0（43 条）；本册范围另由
        # test_tranche10_scope 以卷/分类计数锁定。
        prior = sorted((d for d in DISP
                        if d["s0_offset"] not in BATCH10_S0
                        and d["s0_offset"] not in BATCH11_S0),
                       key=lambda d: d["s0_offset"])
        self.assertEqual(len(prior), 695)
        self.assertEqual(_canon_sha(prior), BATCH123456789_DISP_SHA256)

    def test_batch12345678910_entries_verbatim(self):
        # 前十册 738 条 = 全部处置减去第十一分册冻结位点集
        # BATCH11_S0（24 条）；本册范围另由
        # test_tranche11_scope 以卷/分类计数锁定。
        prior = sorted((d for d in DISP
                        if d["s0_offset"] not in BATCH11_S0),
                       key=lambda d: d["s0_offset"])
        self.assertEqual(len(prior), 738)
        self.assertEqual(_canon_sha(prior),
                         BATCH12345678910_DISP_SHA256)

    def test_input_pins_cross_checked(self):
        inp = REG["inputs"]
        self.assertEqual(inp["snapshot"]["sha256"],
                         "00e2a7db8bb59b259b99938033bb1bb77947e04a15dafc111"
                         "e62b59378010c86")
        self.assertEqual(inp["snapshot"]["chars"], 461157)
        self.assertEqual(inp["applied_text"]["sha256"],
                         ar.PRODUCTS["applied_text"]["sha256"])
        self.assertEqual(inp["applied_text"]["bytes"],
                         ar.PRODUCTS["applied_text"]["bytes"])
        self.assertEqual(inp["application_report"]["file_sha256"],
                         ar.PRODUCTS["application_report"]["file_sha256"])
        self.assertEqual(inp["snapshot_manifest"]["file_count"], 237)
        self.assertEqual(inp["snapshot_manifest"]["total_bytes"], 15883200)
        self.assertEqual(
            inp["snapshot_manifest"]["manifest_sha256"],
            "5ea551f5ffe3e3abbe42f4edf03dfe9d973fd7bc49ab7207180dc454ea874cbc")
        # 残余扫描与应用记录登记册同值
        self.assertEqual(ar.RESIDUAL_SCAN["fang"], 769)
        self.assertEqual(REG["summary"]["total_residual_fang_s3"],
                         ar.RESIDUAL_SCAN["fang"])

    def test_categories_defined(self):
        self.assertEqual(set(REG["categories"]),
                         {"disposed_confirmed", "disposed_kept",
                          "disposed_parallel", "deferred_no_witness",
                          "pending_later_tranche"})
        for text in REG["categories"].values():
            self.assertTrue(text)

    def test_inventory_completeness(self):
        self.assertEqual(len(INV), 769)
        self.assertEqual([x["seq"] for x in INV], list(range(1, 770)))
        s3s = [x["s3_offset"] for x in INV]
        self.assertEqual(s3s, sorted(s3s))
        self.assertEqual(len(set(s3s)), 769)
        self.assertTrue(all(0 <= o < 461156 for o in s3s))
        for x in INV:
            # ±6 语境；全文末尾的位点（s3 461151）语境被文本
            # 末端截断为 11 字，位点仍在索引 6
            self.assertTrue(11 <= len(x["context_s3"]) <= 13)
            self.assertEqual(x["context_s3"][6], "防")
            self.assertRegex(x["context_s3_sha256"], r"^[0-9a-f]{64}$")
            self.assertTrue(x["origin_kind"] == "identity"
                            or x["origin_kind"].startswith("correction:"))
        self.assertEqual(
            Counter(x["origin_kind"].split(":")[0] for x in INV),
            Counter({"identity": 739, "correction": 30}))
        self.assertEqual(sum(1 for x in INV if x["candidate_site"]), 518)
        rd = sorted(x["rd12_seq"] for x in INV if x["rd12_seq"])
        self.assertEqual(rd, [361, 385, 450, 612, 616, 824, 873, 933])

    def test_summary_reconciliation(self):
        s = REG["summary"]
        counts = Counter(x["disposition"] for x in INV)
        self.assertEqual(counts["disposed_confirmed"],
                         s["disposed_confirmed"])
        self.assertEqual(counts["disposed_kept"], s["disposed_kept"])
        self.assertEqual(counts["disposed_parallel"],
                         s["disposed_parallel"])
        self.assertEqual(counts["deferred_no_witness"],
                         s["deferred_no_witness"])
        self.assertEqual(counts["pending_later_tranche"],
                         s["pending_later_tranche"])
        self.assertEqual(s["disposed_total"],
                         s["disposed_confirmed"] + s["disposed_kept"]
                         + s["disposed_parallel"])
        self.assertEqual(s["disposed_total"], 161)
        self.assertEqual(s["disposed_total"] + s["deferred_no_witness"]
                         + s["pending_later_tranche"], 769)
        self.assertEqual(s["cumulative_disposed_fraction"], "161/769")
        self.assertEqual(s["in_registered_sections"], 43)
        self.assertEqual(s["inventory_rows_with_collation_note"], 40)
        self.assertEqual(s["rd12_sites_in_inventory"], 8)
        self.assertEqual(s["rd12_sites_in_pending_tranches"], 7)

    def test_dispositions_coverage(self):
        non_pending = {x["s0_offset"] for x in INV
                       if x["disposition"] != "pending_later_tranche"}
        self.assertEqual(len(DISP), 762)
        self.assertEqual({d["s0_offset"] for d in DISP}, non_pending)
        by_s0 = {x["s0_offset"]: x for x in INV}
        for d in DISP:
            row = by_s0[d["s0_offset"]]
            self.assertEqual(row["disposition"], d["category"])
            self.assertEqual(row["s3_offset"], d["s3_offset"])
            self.assertEqual(row["section_id"], d["section_id"])
            self.assertEqual(row["collation_note_id"],
                             d["collation_note_id"])
        in_section = [d for d in DISP if d["section_id"] is not None]
        self.assertEqual(len(in_section), 43)
        noted = [d for d in DISP if d["collation_note_id"]]
        self.assertEqual(len(noted), 40)
        self.assertEqual(
            sorted(d["s0_offset"] for d in in_section
                   if not d["collation_note_id"]),
            [49021, 58542, 76988])

    def test_tranche2_scope(self):
        t2 = [d for d in DISP if d["section_id"] is None
              and d["volume"] in ("卷首", "卷一", "卷二", "卷三")]
        self.assertEqual(len(t2), 86)
        self.assertEqual({d["volume"] for d in t2},
                         {"卷首", "卷一", "卷二", "卷三"})
        self.assertEqual(Counter(d["category"] for d in t2),
                         Counter({"deferred_no_witness": 67,
                                  "disposed_kept": 15,
                                  "disposed_confirmed": 3,
                                  "disposed_parallel": 1}))
        self.assertEqual(Counter(d["volume"] for d in t2),
                         Counter({"卷三": 49, "卷二": 26, "卷一": 10,
                                  "卷首": 1}))
        # 本册四卷已无 pending；后续分册自卷四起（第三分册
        # 已处卷四，见 test_tranche3_scope）
        self.assertEqual(
            [x for x in INV if x["disposition"] == "pending_later_tranche"
             and x["volume"] in ("卷首", "卷一", "卷二", "卷三")], [])
        # 本册范围内无 RD-12 位点
        self.assertTrue(all(by_rd is None for by_rd in
                            (x["rd12_seq"] for x in INV
                             if x["s0_offset"]
                             in {d["s0_offset"] for d in t2})))

    def test_tranche3_scope(self):
        t3 = [d for d in DISP if d["volume"] == "卷四"]
        self.assertEqual(len(t3), 118)
        self.assertEqual(Counter(d["category"] for d in t3),
                         Counter({"deferred_no_witness": 112,
                                  "disposed_kept": 4,
                                  "disposed_confirmed": 2}))
        # 卷四已无 pending；后续分册自卷五起
        self.assertEqual(
            [x for x in INV if x["disposition"] == "pending_later_tranche"
             and x["volume"] == "卷四"], [])
        # 本册范围内无 RD-12 位点
        self.assertTrue(all(x["rd12_seq"] is None for x in INV
                            if x["s0_offset"]
                            in {d["s0_offset"] for d in t3}))

    def test_tranche3_witness_standard(self):
        by_s0 = {d["s0_offset"]: d for d in DISP}
        # 平行源文本旁证：本册 24 处、全部为 youngzs
        # 《五行精纪》文档命中，不计现代方（全册累计 25
        # 处，第四分册 1 处见 test_tranche4_witness_standard）
        ps = [(d, e) for d in DISP for e in d["witness_evidence"]
              if e["attestation"] == "attested_parallel_source"
              and d["volume"] == "卷四"]
        self.assertEqual(len(ps), 24)
        for d, e in ps:
            self.assertEqual(e["witness"], "youngzs/xuanxue")
            self.assertIn("五行精纪", e["locator"])
            self.assertEqual(d["volume"], "卷四")
        # 旁证不得单独支撑 confirmed：两处定案均有计方现代
        # 见证（attested 且定位于三命通会转录）
        for o, word in ((114728, "凶"), (122205, "微")):
            d = by_s0[o]
            self.assertEqual(d["category"], "disposed_confirmed")
            counted = [e for e in d["witness_evidence"]
                       if e["witness"] in MODERN
                       and e["attestation"] == "attested"
                       and "三命通会" in e["locator"]
                       and e["site_reading"] == word]
            self.assertEqual(len(counted), 2, o)
        # 146688：四库读䄂、源文本读福，两读并录、归 deferred
        d = by_s0[146688]
        self.assertEqual(d["category"], "deferred_no_witness")
        self.assertEqual(d["candidate_reading_glyph"], "䄂")
        ev = {e["witness"]: e for e in d["witness_evidence"]}
        self.assertEqual(ev["youngzs/xuanxue"]["attestation"],
                         "attested_parallel_source")
        self.assertEqual(ev["youngzs/xuanxue"]["site_reading"], "福")
        # 126098：kanripo 全文无此段，仅 mikkokotila 定位
        d = by_s0[126098]
        self.assertEqual(d["category"], "deferred_no_witness")
        self.assertEqual(d["candidate_reading_glyph"], "㤗")
        ev = {e["witness"]: e for e in d["witness_evidence"]}
        self.assertEqual(ev["kanripo/KR3g0042"]["attestation"],
                         "not_located")
        self.assertEqual(
            ev["mikkokotila/Sanming-Tongshui"]["site_reading"], "㤗")
        # 130766/131317：kanripo 句段锚定定位
        for o, glyph in ((130766, "㐫"), (131317, "㓙")):
            ev = {e["witness"]: e
                  for e in by_s0[o]["witness_evidence"]}
            self.assertEqual(ev["kanripo/KR3g0042"]["attestation"],
                             "attested")
            self.assertEqual(ev["kanripo/KR3g0042"]["match_mode"],
                             "segment_anchored")
            self.assertEqual(ev["kanripo/KR3g0042"]["site_reading"],
                             glyph)

    def test_tranche4_scope(self):
        by_s0 = {x["s0_offset"]: x for x in INV}
        t4 = [d for d in DISP if d["s0_offset"] in BATCH4_S0]
        self.assertEqual(len(t4), 65)
        self.assertEqual(Counter(d["category"] for d in t4),
                         Counter({"deferred_no_witness": 50,
                                  "disposed_confirmed": 9,
                                  "disposed_kept": 6}))
        self.assertTrue(all(d["volume"] == "卷五" for d in t4))
        # 卷五 pending 恰余 RD-12 两处（seq 361/385），只
        # 标记、未处置，处置随 P3
        rest = [x for x in INV
                if x["disposition"] == "pending_later_tranche"
                and x["volume"] == "卷五"]
        self.assertEqual(len(rest), 2)
        self.assertEqual({x["rd12_seq"] for x in rest}, {361, 385})
        self.assertEqual({x["s0_offset"] for x in rest},
                         {157779, 164133})
        self.assertTrue(all(x["rd12_seq"] is None for x in INV
                            if x["s0_offset"] in BATCH4_S0))

    def test_tranche4_witness_standard(self):
        by_s0 = {d["s0_offset"]: d for d in DISP}
        # 全册平行源文本旁证累计 31 处（卷四 24 + 卷五 1
        # + 卷六 1 + 卷九 2，第五分册 1 处见
        # test_tranche5_witness_standard、卷九 2 处见
        # test_tranche8_witness_standard）
        ps = [(d, e) for d in DISP for e in d["witness_evidence"]
              if e["attestation"] == "attested_parallel_source"]
        self.assertEqual(len(ps), 31)
        # 154979：四库读㸃、源文本读直，两读并录、归 deferred
        d = by_s0[154979]
        self.assertEqual(d["category"], "deferred_no_witness")
        self.assertEqual(d["candidate_reading_glyph"], "㸃")
        ev = {e["witness"]: e for e in d["witness_evidence"]}
        self.assertEqual(ev["youngzs/xuanxue"]["attestation"],
                         "attested_parallel_source")
        self.assertEqual(ev["youngzs/xuanxue"]["site_reading"], "直")
        self.assertIn("五行精纪", ev["youngzs/xuanxue"]["locator"])
        # 三处 kanripo bracket 未定位：候选只据 mikkokotila
        for o in (149947, 161345, 175574):
            d = by_s0[o]
            self.assertEqual(d["category"], "deferred_no_witness")
            self.assertEqual(d["candidate_reading_glyph"], "㸔")
            ev = {e["witness"]: e for e in d["witness_evidence"]}
            self.assertEqual(ev["kanripo/KR3g0042"]["attestation"],
                             "not_located")
            self.assertEqual(
                ev["mikkokotila/Sanming-Tongshui"]["attestation"],
                "attested")
            self.assertEqual(
                ev["mikkokotila/Sanming-Tongshui"]["site_reading"],
                "㸔")
        # 本册 9 处定案均有计方现代见证同读（attested 且
        # 定位于三命通会转录，含同文赋文的跨卷转录位点）
        for d in (x for x in DISP if x["s0_offset"] in BATCH4_S0
                  and x["category"] == "disposed_confirmed"):
            counted = [e for e in d["witness_evidence"]
                       if e["witness"] in MODERN
                       and e["attestation"] == "attested"
                       and "三命通会" in e["locator"]
                       and e["site_reading"] in (
                           d["reading_word"],
                           d["reading_word_simplified"])]
            self.assertTrue(counted, d["s0_offset"])

    def test_tranche5_scope(self):
        t5 = [d for d in DISP if d["s0_offset"] in BATCH5_S0]
        self.assertEqual(len(t5), 130)
        self.assertEqual(Counter(d["category"] for d in t5),
                         Counter({"deferred_no_witness": 118,
                                  "disposed_confirmed": 7,
                                  "disposed_kept": 5}))
        self.assertTrue(all(d["volume"] == "卷六" for d in t5))
        # 卷六已无 pending；后续分册自卷七起
        self.assertEqual(
            [x for x in INV if x["disposition"] == "pending_later_tranche"
             and x["volume"] == "卷六"], [])
        # 本册范围内无 RD-12 位点
        self.assertTrue(all(x["rd12_seq"] is None for x in INV
                            if x["s0_offset"] in BATCH5_S0))

    def test_tranche5_witness_standard(self):
        by_s0 = {d["s0_offset"]: d for d in DISP}
        # 全册平行源文本旁证累计 31 处（卷四 24 + 卷五 1 + 卷六 1
        # + 卷九 2）
        ps = [(d, e) for d in DISP for e in d["witness_evidence"]
              if e["attestation"] == "attested_parallel_source"]
        self.assertEqual(len(ps), 31)
        # 218248：四库读䨇、源文本同读双，旁证同读亦不计方、
        # 归 deferred，两读并录
        d = by_s0[218248]
        self.assertEqual(d["category"], "deferred_no_witness")
        self.assertEqual(d["candidate_reading_glyph"], "䨇")
        ev = {e["witness"]: e for e in d["witness_evidence"]}
        self.assertEqual(ev["youngzs/xuanxue"]["attestation"],
                         "attested_parallel_source")
        self.assertEqual(ev["youngzs/xuanxue"]["site_reading"], "双")
        self.assertIn("五行精纪", ev["youngzs/xuanxue"]["locator"])
        # 四库两家本册 130/130 全定位（无 kanripo 缺位）；
        # mikkokotila 于 212273 为单侧锚定
        for o in BATCH5_S0:
            ev = {e["witness"]: e
                  for e in by_s0[o]["witness_evidence"]}
            for wname in ("kanripo/KR3g0042",
                          "mikkokotila/Sanming-Tongshui"):
                self.assertEqual(ev[wname]["attestation"], "attested",
                                 (o, wname))
        ev = {e["witness"]: e for e in by_s0[212273]["witness_evidence"]}
        self.assertEqual(
            ev["mikkokotila/Sanming-Tongshui"]["match_mode"],
            "side_anchored")
        # 两处跨卷同文计方见证：NiuTrans 定位于其卷十二
        # 《四言独步》转录的同文位点
        for o, word in ((193388, "凶"), (196506, "双")):
            d = by_s0[o]
            self.assertEqual(d["category"], "disposed_confirmed")
            ev = {e["witness"]: e for e in d["witness_evidence"]}
            n = ev["NiuTrans/Classical-Modern"]
            self.assertEqual(n["attestation"], "attested")
            self.assertIn("四言独步", n["locator"])
            self.assertEqual(n["site_reading"], word)
        # 本册 7 处定案均有计方现代见证同读（attested 且
        # 定位于三命通会转录，含《四言独步》跨卷同文位点）
        for d in (x for x in DISP if x["s0_offset"] in BATCH5_S0
                  and x["category"] == "disposed_confirmed"):
            counted = [e for e in d["witness_evidence"]
                       if e["witness"] in MODERN
                       and e["attestation"] == "attested"
                       and "三命通会" in e["locator"]
                       and e["site_reading"] in (
                           d["reading_word"],
                           d["reading_word_simplified"])]
            self.assertTrue(counted, d["s0_offset"])

    def test_tranche6_scope(self):
        t6 = [d for d in DISP if d["s0_offset"] in BATCH6_S0]
        self.assertEqual(len(t6), 73)
        self.assertEqual(Counter(d["category"] for d in t6),
                         Counter({"deferred_no_witness": 61,
                                  "disposed_kept": 8,
                                  "disposed_confirmed": 4}))
        self.assertTrue(all(d["volume"] == "卷七" for d in t6))
        # 卷七 pending 恰余 RD-12 两处（seq 612/616），只
        # 标记、未处置，处置随 P3；后续分册自卷八起
        rest = [x for x in INV
                if x["disposition"] == "pending_later_tranche"
                and x["volume"] == "卷七"]
        self.assertEqual(len(rest), 2)
        self.assertEqual({x["rd12_seq"] for x in rest}, {612, 616})
        self.assertEqual({x["s0_offset"] for x in rest},
                         {228261, 228869})
        self.assertTrue(all(x["rd12_seq"] is None for x in INV
                            if x["s0_offset"] in BATCH6_S0))

    def test_tranche6_witness_standard(self):
        by_s0 = {d["s0_offset"]: d for d in DISP}
        # 全册平行源文本旁证累计 31 处（卷四 24 + 卷五 1
        # + 卷六 1 + 卷九 2）；本册无新命中
        ps = [(d, e) for d in DISP for e in d["witness_evidence"]
              if e["attestation"] == "attested_parallel_source"]
        self.assertEqual(len(ps), 31)
        self.assertTrue(all(d["s0_offset"] not in BATCH6_S0
                            for d, e in ps))
        # 四库两家本册 73/73 全定位（无 kanripo 缺位）
        for o in BATCH6_S0:
            ev = {e["witness"]: e
                  for e in by_s0[o]["witness_evidence"]}
            for wname in ("kanripo/KR3g0042",
                          "mikkokotila/Sanming-Tongshui"):
                self.assertEqual(ev[wname]["attestation"], "attested",
                                 (o, wname))
        # 245945：紧邻字异体（底本妝、两家粧）致标准捕获
        # 失败，变体锚定定位、两家同读䑓，归 deferred
        d = by_s0[245945]
        self.assertEqual(d["category"], "deferred_no_witness")
        self.assertEqual(d["candidate_reading_glyph"], "䑓")
        ev = {e["witness"]: e for e in d["witness_evidence"]}
        for wname in ("kanripo/KR3g0042",
                      "mikkokotila/Sanming-Tongshui"):
            self.assertEqual(ev[wname]["match_mode"],
                             "variant_anchored", wname)
            self.assertEqual(ev[wname]["site_reading"], "䑓")
        # 本册其余位点不得用变体锚定
        for o in BATCH6_S0 - {245945}:
            ev = {e["witness"]: e
                  for e in by_s0[o]["witness_evidence"]}
            for wname in ("kanripo/KR3g0042",
                          "mikkokotila/Sanming-Tongshui"):
                self.assertNotEqual(ev[wname].get("match_mode"),
                                    "variant_anchored", (o, wname))
        # 226603：四库字形膞、词从膊（同词异体以词为准）
        d = by_s0[226603]
        self.assertEqual(d["category"], "disposed_confirmed")
        self.assertEqual(d["reading_glyph"], "膞")
        self.assertEqual(d["reading_word"], "膊")
        # 本册 4 处定案均有计方现代见证同读（attested 且
        # 定位于三命通会转录）
        for d in (x for x in DISP if x["s0_offset"] in BATCH6_S0
                  and x["category"] == "disposed_confirmed"):
            counted = [e for e in d["witness_evidence"]
                       if e["witness"] in MODERN
                       and e["attestation"] == "attested"
                       and "三命通会" in e["locator"]
                       and e["site_reading"] in (
                           d["reading_word"],
                           d["reading_word_simplified"])]
            self.assertTrue(counted, d["s0_offset"])

    def test_tranche7_scope(self):
        t7 = [d for d in DISP if d["s0_offset"] in BATCH7_S0]
        self.assertEqual(len(t7), 61)
        self.assertEqual(Counter(d["category"] for d in t7),
                         Counter({"deferred_no_witness": 47,
                                  "disposed_kept": 7,
                                  "disposed_confirmed": 5,
                                  "disposed_parallel": 2}))
        self.assertTrue(all(d["volume"] == "卷八" for d in t7))
        # 卷八 pending 清零；本册无 RD-12 标记位点，后续
        # 分册自卷九起
        rest = [x for x in INV
                if x["disposition"] == "pending_later_tranche"
                and x["volume"] == "卷八"]
        self.assertEqual(rest, [])
        self.assertTrue(all(x["rd12_seq"] is None for x in INV
                            if x["s0_offset"] in BATCH7_S0))

    def test_tranche7_witness_standard(self):
        by_s0 = {d["s0_offset"]: d for d in DISP}
        # 全册平行源文本旁证累计 31 处（卷四 24 + 卷五 1
        # + 卷六 1 + 卷九 2）；本册无新命中
        ps = [(d, e) for d in DISP for e in d["witness_evidence"]
              if e["attestation"] == "attested_parallel_source"]
        self.assertEqual(len(ps), 31)
        self.assertTrue(all(d["s0_offset"] not in BATCH7_S0
                            for d, e in ps))
        # mikkokotila 本册 61/61 全定位；kanripo 43 处定位、
        # 18 处 bracket 名录栏式编排致未定位（逐字登记
        # not_located，候选只据 mikkokotila 一家、一律
        # deferred）；本册四库证据无 variant_anchored
        for o in BATCH7_S0:
            ev = {e["witness"]: e
                  for e in by_s0[o]["witness_evidence"]}
            self.assertEqual(
                ev["mikkokotila/Sanming-Tongshui"]["attestation"],
                "attested", o)
            for wname in ("kanripo/KR3g0042",
                          "mikkokotila/Sanming-Tongshui"):
                self.assertNotEqual(ev[wname].get("match_mode"),
                                    "variant_anchored", (o, wname))
            if o in KAN_MISSING7_S0:
                self.assertEqual(ev["kanripo/KR3g0042"]["attestation"],
                                 "not_located", o)
                self.assertEqual(by_s0[o]["category"],
                                 "deferred_no_witness", o)
            else:
                self.assertEqual(ev["kanripo/KR3g0042"]["attestation"],
                                 "attested", o)
                self.assertEqual(
                    ev["kanripo/KR3g0042"]["site_reading"],
                    ev["mikkokotila/Sanming-Tongshui"]["site_reading"],
                    o)
        # 两处并列：272529 綵对采、277562 㑹对合——双方
        # 读法并列登记、reading 字段全 None
        for o, glyph, word, rival in (
                (272529, "綵", "綵", "采"), (277562, "㑹", "會", "合")):
            d = by_s0[o]
            self.assertEqual(d["category"], "disposed_parallel")
            self.assertIsNone(d["reading_glyph"])
            self.assertIsNone(d["reading_word"])
            self.assertEqual(d["candidate_reading_glyph"], glyph)
            self.assertEqual(d["candidate_reading_word"], word)
            pr = d["parallel_readings"]
            self.assertEqual(pr[0]["reading_glyph"], glyph)
            self.assertEqual(pr[0]["attested_by"], ["siku_lineage"])
            self.assertEqual(pr[1]["reading_glyph"], rival)
            self.assertEqual(pr[1]["attested_by"],
                             ["modern_lineage_niutrans",
                              "modern_lineage_youngzs"])
        # 本册 5 处定案均有计方现代见证同读（attested 且
        # 定位于三命通会转录）
        for d in (x for x in DISP if x["s0_offset"] in BATCH7_S0
                  and x["category"] == "disposed_confirmed"):
            counted = [e for e in d["witness_evidence"]
                       if e["witness"] in MODERN
                       and e["attestation"] == "attested"
                       and "三命通会" in e["locator"]
                       and e["site_reading"] in (
                           d["reading_word"],
                           d["reading_word_simplified"])]
            self.assertTrue(counted, d["s0_offset"])

    def test_tranche8_scope(self):
        t8 = [d for d in DISP if d["s0_offset"] in BATCH8_S0]
        self.assertEqual(len(t8), 94)
        self.assertEqual(Counter(d["category"] for d in t8),
                         Counter({"deferred_no_witness": 71,
                                  "disposed_confirmed": 16,
                                  "disposed_kept": 7}))
        self.assertTrue(all(d["volume"] == "卷九" for d in t8))
        # 卷九 pending 清零；本册无 RD-12 标记位点，后续
        # 分册自卷十起
        rest = [x for x in INV
                if x["disposition"] == "pending_later_tranche"
                and x["volume"] == "卷九"]
        self.assertEqual(rest, [])
        self.assertTrue(all(x["rd12_seq"] is None for x in INV
                            if x["s0_offset"] in BATCH8_S0))

    def test_tranche8_witness_standard(self):
        by_s0 = {d["s0_offset"]: d for d in DISP}
        # 全册平行源文本旁证累计 31 处（卷四 24 + 卷五 1
        # + 卷六 1 + 本册 2）；本册 2 处为 324699/324706，
        # youngzs《五行精纪》转录同读「凶」、不计现代方，
        # 两处归 deferred
        ps = [(d, e) for d in DISP for e in d["witness_evidence"]
              if e["attestation"] == "attested_parallel_source"]
        self.assertEqual(len(ps), 31)
        ps8 = [(d, e) for d, e in ps
               if d["s0_offset"] in BATCH8_S0]
        self.assertEqual({d["s0_offset"] for d, e in ps8},
                         {324699, 324706})
        for d, e in ps8:
            self.assertEqual(e["witness"], "youngzs/xuanxue")
            self.assertEqual(e["site_reading"], "凶")
            self.assertIn("五行精纪", e["locator"])
            self.assertEqual(d["category"], "deferred_no_witness")
            self.assertEqual(d["candidate_reading_glyph"], "㐫")
        # mikkokotila 本册 94/94 全定位；kanripo 62 处定位、
        # 32 处未定位（逐字登记 not_located，候选只据
        # mikkokotila 一家、一律 deferred）；本册四库证据
        # 无 variant_anchored
        for o in BATCH8_S0:
            ev = {e["witness"]: e
                  for e in by_s0[o]["witness_evidence"]}
            self.assertEqual(
                ev["mikkokotila/Sanming-Tongshui"]["attestation"],
                "attested", o)
            for wname in ("kanripo/KR3g0042",
                          "mikkokotila/Sanming-Tongshui"):
                self.assertNotEqual(ev[wname].get("match_mode"),
                                    "variant_anchored", (o, wname))
            if o in KAN_MISSING8_S0:
                self.assertEqual(ev["kanripo/KR3g0042"]["attestation"],
                                 "not_located", o)
                self.assertEqual(by_s0[o]["category"],
                                 "deferred_no_witness", o)
            else:
                self.assertEqual(ev["kanripo/KR3g0042"]["attestation"],
                                 "attested", o)
                self.assertEqual(
                    ev["kanripo/KR3g0042"]["site_reading"],
                    ev["mikkokotila/Sanming-Tongshui"]["site_reading"],
                    o)
        # 本册无并列：BATCH8 内无 disposed_parallel
        self.assertTrue(all(
            d["category"] != "disposed_parallel"
            for d in DISP if d["s0_offset"] in BATCH8_S0))
        # 本册 16 处定案均为㐫读凶且有计方现代见证同读
        # （attested 且定位于三命通会转录）
        for d in (x for x in DISP if x["s0_offset"] in BATCH8_S0
                  and x["category"] == "disposed_confirmed"):
            self.assertEqual(d["reading_glyph"], "㐫")
            self.assertEqual(d["reading_word"], "凶")
            counted = [e for e in d["witness_evidence"]
                       if e["witness"] in MODERN
                       and e["attestation"] == "attested"
                       and "三命通会" in e["locator"]
                       and e["site_reading"] in (
                           d["reading_word"],
                           d["reading_word_simplified"])]
            self.assertTrue(counted, d["s0_offset"])

    def test_tranche9_scope(self):
        t9 = [d for d in DISP if d["s0_offset"] in BATCH9_S0]
        self.assertEqual(len(t9), 25)
        self.assertEqual(Counter(d["category"] for d in t9),
                         Counter({"disposed_kept": 11,
                                  "deferred_no_witness": 11,
                                  "disposed_confirmed": 3}))
        self.assertTrue(all(d["volume"] == "卷十" for d in t9))
        # 卷十 pending 只余 RD-12 seq 824 一处（只标记、
        # 保持 pending、处置随 P3）
        rest = [x for x in INV
                if x["disposition"] == "pending_later_tranche"
                and x["volume"] == "卷十"]
        self.assertEqual([x["s0_offset"] for x in rest],
                         [RD12_JUAN10_S0])
        self.assertEqual(rest[0]["rd12_seq"], 824)
        self.assertTrue(all(x["rd12_seq"] is None for x in INV
                            if x["s0_offset"] in BATCH9_S0))

    def test_tranche9_witness_standard(self):
        by_s0 = {d["s0_offset"]: d for d in DISP}
        # 全册平行源文本旁证累计 31 处（卷四 24 + 卷五 1
        # + 卷六 1 + 卷九 2 + 本册 2）；本册 2 处为
        # 357674/359024，youngzs《五行精纪》转录同读
        # （防/灭）、不计现代方：357674 无异读依 kept
        # 标准定案、359024 归 deferred
        ps = [(d, e) for d in DISP for e in d["witness_evidence"]
              if e["attestation"] == "attested_parallel_source"]
        self.assertEqual(len(ps), 31)
        ps9 = [(d, e) for d, e in ps
               if d["s0_offset"] in BATCH9_S0]
        self.assertEqual({d["s0_offset"] for d, e in ps9},
                         {357674, 359024})
        for d, e in ps9:
            self.assertEqual(e["witness"], "youngzs/xuanxue")
            self.assertIn("五行精纪", e["locator"])
        self.assertEqual(by_s0[357674]["category"], "disposed_kept")
        self.assertEqual(by_s0[359024]["category"],
                         "deferred_no_witness")
        # 四库谱系本册 25/25 两家全定位、读法逐处一致；
        # 本册四库证据无 variant_anchored、无 kanripo
        # 未定位
        for o in BATCH9_S0:
            ev = {e["witness"]: e
                  for e in by_s0[o]["witness_evidence"]}
            for wname in ("kanripo/KR3g0042",
                          "mikkokotila/Sanming-Tongshui"):
                self.assertEqual(ev[wname]["attestation"],
                                 "attested", (o, wname))
                self.assertNotEqual(ev[wname].get("match_mode"),
                                    "variant_anchored", (o, wname))
            self.assertEqual(
                ev["kanripo/KR3g0042"]["site_reading"],
                ev["mikkokotila/Sanming-Tongshui"]["site_reading"],
                o)
        # 本册无并列：BATCH9 内无 disposed_parallel
        self.assertTrue(all(
            d["category"] != "disposed_parallel"
            for d in DISP if d["s0_offset"] in BATCH9_S0))
        # 本册 3 处定案（㡬读幾、㸔读看、㓛读功）均有计方
        # 现代见证同读（attested 且定位于三命通会转录）
        for d in (x for x in DISP if x["s0_offset"] in BATCH9_S0
                  and x["category"] == "disposed_confirmed"):
            self.assertIn((d["reading_glyph"], d["reading_word"]),
                          {("㡬", "幾"), ("㸔", "看"), ("㓛", "功")})
            counted = [e for e in d["witness_evidence"]
                       if e["witness"] in MODERN
                       and e["attestation"] == "attested"
                       and "三命通会" in e["locator"]
                       and e["site_reading"] in (
                           d["reading_word"],
                           d["reading_word_simplified"])]
            self.assertTrue(counted, d["s0_offset"])

    def test_tranche10_scope(self):
        t10 = [d for d in DISP if d["s0_offset"] in BATCH10_S0]
        self.assertEqual(len(t10), 43)
        self.assertEqual(Counter(d["category"] for d in t10),
                         Counter({"disposed_confirmed": 9,
                                  "disposed_kept": 9,
                                  "disposed_parallel": 1,
                                  "deferred_no_witness": 24}))
        self.assertTrue(all(d["volume"] == "卷十一" for d in t10))
        # 卷十一 pending 只余 RD-12 seq 873/933 两处
        # （只标记、保持 pending、处置随 P3）
        rest = [x for x in INV
                if x["disposition"] == "pending_later_tranche"
                and x["volume"] == "卷十一"]
        self.assertEqual({x["s0_offset"] for x in rest},
                         RD12_JUAN11_S0)
        self.assertEqual({x["rd12_seq"] for x in rest},
                         {873, 933})
        self.assertTrue(all(x["rd12_seq"] is None for x in INV
                            if x["s0_offset"] in BATCH10_S0))

    def test_tranche10_witness_standard(self):
        by_s0 = {d["s0_offset"]: d for d in DISP}
        # 全册平行源文本旁证累计 31 处（卷四 24 + 卷五 1
        # + 卷六 1 + 卷九 2 + 卷十 2 + 本册 1）；本册
        # 1 处为 411566，youngzs《五行精纪》转录同读
        # 「防」、不计现代方；该处四库与 NiuTrans 亦同
        # 读防、依 kept 标准定案
        ps = [(d, e) for d in DISP for e in d["witness_evidence"]
              if e["attestation"] == "attested_parallel_source"]
        self.assertEqual(len(ps), 31)
        ps10 = [(d, e) for d, e in ps
                if d["s0_offset"] in BATCH10_S0]
        self.assertEqual({d["s0_offset"] for d, e in ps10},
                         {411566})
        for d, e in ps10:
            self.assertEqual(e["witness"], "youngzs/xuanxue")
            self.assertIn("五行精纪", e["locator"])
            self.assertEqual(e["site_reading"], "防")
        self.assertEqual(by_s0[411566]["category"],
                         "disposed_kept")
        # 四库谱系本册 43/43 两家全定位、读法逐处一致；
        # 本册四库证据无 variant_anchored、无 kanripo
        # 未定位
        for o in BATCH10_S0:
            ev = {e["witness"]: e
                  for e in by_s0[o]["witness_evidence"]}
            for wname in ("kanripo/KR3g0042",
                          "mikkokotila/Sanming-Tongshui"):
                self.assertEqual(ev[wname]["attestation"],
                                 "attested", (o, wname))
                self.assertNotEqual(ev[wname].get("match_mode"),
                                    "variant_anchored", (o, wname))
            self.assertEqual(
                ev["kanripo/KR3g0042"]["site_reading"],
                ev["mikkokotila/Sanming-Tongshui"]["site_reading"],
                o)
            # youngzs 三命子集本册全数未定位：其证据至多
            # 为平行源旁证（411566）或未载
            self.assertIn(ev["youngzs/xuanxue"]["attestation"],
                          ("not_located",
                           "attested_parallel_source"), o)
        # 本册并列恰 1 处：396327 四库作䲭（鴟）、现代
        # 计方仅 NiuTrans 一家读鸥（鷗）——并列条目的
        # 现代侧 attested_by 只列 niutrans
        par10 = [d for d in DISP if d["s0_offset"] in BATCH10_S0
                 and d["category"] == "disposed_parallel"]
        self.assertEqual([d["s0_offset"] for d in par10],
                         [396327])
        pr = par10[0]["parallel_readings"]
        self.assertEqual((pr[0]["reading_glyph"],
                          pr[0]["reading_word"],
                          pr[0]["attested_by"]),
                         ("䲭", "鴟", ["siku_lineage"]))
        self.assertEqual((pr[1]["reading_glyph"],
                          pr[1]["reading_word"],
                          pr[1]["attested_by"]),
                         ("鸥", "鷗", ["modern_lineage_niutrans"]))
        # 本册 9 处定案均有计方现代见证同读（本册计方由
        # NiuTrans 一家构成，attested 且定位于三命通会
        # 转录）
        for d in (x for x in DISP if x["s0_offset"] in BATCH10_S0
                  and x["category"] == "disposed_confirmed"):
            self.assertIn((d["reading_glyph"], d["reading_word"]),
                          {("㡬", "幾"), ("㪚", "散"), ("㑹", "會"),
                           ("㧞", "拔"), ("㓜", "幼"), ("䑕", "鼠")})
            counted = [e for e in d["witness_evidence"]
                       if e["witness"] in MODERN
                       and e["attestation"] == "attested"
                       and "三命通会" in e["locator"]
                       and e["site_reading"] in (
                           d["reading_word"],
                           d["reading_word_simplified"])]
            self.assertTrue(counted, d["s0_offset"])

    def test_tranche11_scope(self):
        t11 = [d for d in DISP if d["s0_offset"] in BATCH11_S0]
        self.assertEqual(len(t11), 24)
        self.assertEqual(Counter(d["category"] for d in t11),
                         Counter({"disposed_confirmed": 6,
                                  "disposed_kept": 7,
                                  "deferred_no_witness": 11}))
        self.assertTrue(all(d["volume"] == "卷十二" for d in t11))
        self.assertTrue(all(x["rd12_seq"] is None for x in INV
                            if x["s0_offset"] in BATCH11_S0))
        # 卷十二 pending 清零
        self.assertEqual([x for x in INV
                          if x["disposition"] == "pending_later_tranche"
                          and x["volume"] == "卷十二"], [])
        # P2 收官：全册 pending 恰为 7 处 RD-12 只标记位点
        rest = [x for x in INV
                if x["disposition"] == "pending_later_tranche"]
        self.assertEqual({x["s0_offset"] for x in rest},
                         RD12_PENDING_S0)
        self.assertTrue(all(x["rd12_seq"] is not None for x in rest))

    def test_tranche11_witness_standard(self):
        by_s0 = {d["s0_offset"]: d for d in DISP}
        # 全册平行源文本旁证累计仍 31 处；本册无新命中
        ps = [(d, e) for d in DISP for e in d["witness_evidence"]
              if e["attestation"] == "attested_parallel_source"]
        self.assertEqual(len(ps), 31)
        self.assertEqual([d for d, e in ps
                          if d["s0_offset"] in BATCH11_S0], [])
        # 四库谱系本册 24/24 两家全定位、读法逐处一致；
        # 本册四库证据无 variant_anchored
        for o in BATCH11_S0:
            ev = {e["witness"]: e
                  for e in by_s0[o]["witness_evidence"]}
            for wname in ("kanripo/KR3g0042",
                          "mikkokotila/Sanming-Tongshui"):
                self.assertEqual(ev[wname]["attestation"],
                                 "attested", (o, wname))
                self.assertNotEqual(ev[wname].get("match_mode"),
                                    "variant_anchored", (o, wname))
            self.assertEqual(
                ev["kanripo/KR3g0042"]["site_reading"],
                ev["mikkokotila/Sanming-Tongshui"]["site_reading"],
                o)
            # youngzs 三命子集与全语料本册全数未定位
            self.assertEqual(ev["youngzs/xuanxue"]["attestation"],
                             "not_located", o)
        # 本册无并列
        self.assertEqual([d for d in DISP
                          if d["s0_offset"] in BATCH11_S0
                          and d["category"] == "disposed_parallel"],
                         [])
        # 本册 6 处 confirmed 均有计方现代见证同读（本册
        # 计方由 NiuTrans 一家构成，attested 且定位于
        # 三命通会转录）
        for d in (x for x in DISP if x["s0_offset"] in BATCH11_S0
                  and x["category"] == "disposed_confirmed"):
            self.assertIn((d["reading_glyph"], d["reading_word"]),
                          {("㓙", "凶"), ("㣲", "微"), ("㸔", "看"),
                           ("䧟", "陷")})
            counted = [e for e in d["witness_evidence"]
                       if e["witness"] in MODERN
                       and e["attestation"] == "attested"
                       and "三命通会" in e["locator"]
                       and e["site_reading"] in (
                           d["reading_word"],
                           d["reading_word_simplified"])]
            self.assertTrue(counted, d["s0_offset"])
        # 本册 11 处 deferred：计方现代见证（NiuTrans）
        # 一律未定位（Banny-Gao 旁证同读不计方）
        for d in (x for x in DISP if x["s0_offset"] in BATCH11_S0
                  and x["category"] == "deferred_no_witness"):
            ev = {e["witness"]: e for e in d["witness_evidence"]}
            self.assertEqual(
                ev["NiuTrans/Classical-Modern"]["attestation"],
                "not_located", d["s0_offset"])

    def test_witness_evidence_shape(self):
        for d in DISP:
            ev = d["witness_evidence"]
            self.assertEqual({e["witness"] for e in ev}, ALL_WIT,
                             d["s0_offset"])
            for e in ev:
                if e["witness"] in SIKU:
                    # 四库两家必须在位点定位（定案的证据基座）：
                    # 首批 43/43、第二分册捕获式 86/86、第三
                    # 分册 117/118（余 126098 处 kanripo 全文
                    # 无此段）、第四分册 62/65（余三处 kanripo
                    # 卷首喜忌 bracket 栏式编排致未定位）、第五
                    # 分册 130/130 两家全定位、第六分册
                    # 73/73 两家全定位（245945 一处为变体
                    # 锚定）、第七分册 mikkokotila 61/61
                    # 全定位而 kanripo 43/61（18 处 bracket
                    # 名录次序致未定位，见
                    # test_tranche4_witness_standard、
                    # test_tranche5_witness_standard、
                    # test_tranche6_witness_standard、
                    # test_tranche7_witness_standard）、第八
                    # 分册 mikkokotila 94/94 全定位而 kanripo
                    # 62/94（32 处未定位、多位于 bracket 名录
                    # 条目，见 test_tranche8_witness_standard）、
                    # 第九分册四库两家 26/26 全定位（见
                    # test_tranche9_witness_standard）、第十
                    # 分册四库两家于处置范围 43/43 全定位
                    # （见 test_tranche10_witness_standard）、第十
                    # 一分册四库两家 24/24 全定位
                    # （见 test_tranche11_witness_standard）
                    if ((d["s0_offset"] in (126098, 149947, 161345,
                                            175574)
                         or d["s0_offset"] in KAN_MISSING7_S0
                         or d["s0_offset"] in KAN_MISSING8_S0)
                            and e["witness"] == "kanripo/KR3g0042"):
                        self.assertEqual(e["attestation"],
                                         "not_located")
                        continue
                    self.assertEqual(e["attestation"], "attested",
                                     d["s0_offset"])
                    self.assertTrue(e["quote_short"], d["s0_offset"])
                    self.assertTrue(e["locator"], d["s0_offset"])

    def test_confirmed_rule(self):
        conf = [d for d in DISP if d["category"] == "disposed_confirmed"]
        self.assertEqual(len(conf), 73)
        for d in conf:
            # 定案读法与校勘候选一致，且登记为未来应用候选
            self.assertTrue(d["reading_glyph"])
            self.assertTrue(d["reading_word"])
            self.assertEqual(d["candidate_reading_glyph"],
                             d["reading_glyph"])
            self.assertEqual(d["candidate_reading_word"],
                             d["reading_word"])
            self.assertNotEqual(d["reading_word"], "防")
            siku_readings = {e["site_reading"] for e in d["witness_evidence"]
                             if e["witness"] in SIKU}
            self.assertEqual(siku_readings, {d["reading_glyph"]})
            modern_ok = [e for e in d["witness_evidence"]
                         if e["witness"] in MODERN
                         and e["attestation"] in ("attested",
                                                  "attested_title")
                         and e["site_reading"] in (d["reading_word"],
                                                   d["reading_word_simplified"])]
            self.assertTrue(modern_ok, d["s0_offset"])
            rivals = [e for e in d["witness_evidence"]
                      if e["witness"] in MODERN
                      and e["attestation"] == "rival"]
            self.assertEqual(rivals, [], d["s0_offset"])

    def test_kept_rule(self):
        kept = [d for d in DISP if d["category"] == "disposed_kept"]
        self.assertEqual(len(kept), 83)
        for d in kept:
            self.assertEqual(d["reading_glyph"], "防")
            self.assertEqual(d["reading_word"], "防")
            siku_readings = {e["site_reading"] for e in d["witness_evidence"]
                             if e["witness"] in SIKU}
            self.assertEqual(siku_readings, {"防"})

    def test_parallel_rule(self):
        par = [d for d in DISP if d["category"] == "disposed_parallel"]
        self.assertEqual(len(par), 5)
        by_s0 = {d["s0_offset"]: d for d in par}
        # 首批：73703 四库读㸔、现代三家文句在场脱字
        d = by_s0[73703]
        siku_readings = {e["site_reading"] for e in d["witness_evidence"]
                         if e["witness"] in SIKU}
        self.assertEqual(siku_readings, {"㸔"})
        omitted = [e for e in d["witness_evidence"]
                   if e["witness"] in MODERN
                   and e["attestation"] == "word_omitted_at_locus"]
        self.assertEqual(len(omitted), 2)
        # 第二分册：188 四库读㡬（幾）、youngzs 文句在场脱字
        d2 = by_s0[188]
        siku2 = {e["site_reading"] for e in d2["witness_evidence"]
                 if e["witness"] in SIKU}
        self.assertEqual(siku2, {"㡬"})
        self.assertEqual(d2["candidate_reading_glyph"], "㡬")
        self.assertEqual(d2["candidate_reading_word"], "幾")
        omitted2 = [e for e in d2["witness_evidence"]
                    if e["attestation"] == "word_omitted_at_locus"]
        self.assertEqual(len(omitted2), 1)
        self.assertEqual(omitted2[0]["witness"], "youngzs/xuanxue")
        self.assertEqual(
            d2["parallel_readings"][0]["attested_by"], ["siku_lineage"])
        self.assertEqual(d2["parallel_readings"][1]["treatment"],
                         "word_omitted_at_locus")
        self.assertEqual(d2["parallel_readings"][1]["attested_by"],
                         ["modern_lineage_youngzs"])
        # 第七分册：272529 四库读綵、现代计方两家读采；
        # 277562 四库读㑹、现代计方两家读合（字级分歧并列）
        for off, glyph, rival in ((272529, "綵", "采"),
                                  (277562, "㑹", "合")):
            d7 = by_s0[off]
            siku7 = {e["site_reading"] for e in d7["witness_evidence"]
                     if e["witness"] in SIKU}
            self.assertEqual(siku7, {glyph})
            modern7 = {e["site_reading"] for e in d7["witness_evidence"]
                       if e["witness"] in MODERN
                       and e["attestation"] == "attested"}
            self.assertEqual(modern7, {rival})
        for d in par:
            self.assertIsNone(d["reading_glyph"])
            self.assertIsNone(d["reading_word"])

    def test_deferred_rule(self):
        deferred = [d for d in DISP
                    if d["category"] == "deferred_no_witness"]
        self.assertEqual(len(deferred), 601)
        for d in deferred:
            # deferred 不得登记定案读法（校勘候选只在 candidate 栏）
            self.assertIsNone(d["reading_glyph"])
            self.assertIsNone(d["reading_word"])
            # 第二分册 deferred 的缺口形态：现代两家均未载
            if d["section_id"] is None and d["volume"] in (
                    "卷首", "卷一", "卷二", "卷三"):
                modern = [e for e in d["witness_evidence"]
                          if e["witness"] in MODERN]
                self.assertTrue(
                    all(e["attestation"] == "not_located" for e in modern),
                    d["s0_offset"])
            # 第三分册 deferred：计方现代见证（NiuTrans 与
            # youngzs 三命子集）均未定位；youngzs 至多有平行
            # 源文本旁证（attested_parallel_source、不计方）
            if d["volume"] == "卷四":
                ev = {e["witness"]: e for e in d["witness_evidence"]}
                self.assertEqual(
                    ev["NiuTrans/Classical-Modern"]["attestation"],
                    "not_located", d["s0_offset"])
                self.assertIn(
                    ev["youngzs/xuanxue"]["attestation"],
                    ("not_located", "attested_parallel_source"),
                    d["s0_offset"])
            # 第四分册 deferred：缺口形态同第三分册
            if d["s0_offset"] in BATCH4_S0:
                ev = {e["witness"]: e for e in d["witness_evidence"]}
                self.assertEqual(
                    ev["NiuTrans/Classical-Modern"]["attestation"],
                    "not_located", d["s0_offset"])
                self.assertIn(
                    ev["youngzs/xuanxue"]["attestation"],
                    ("not_located", "attested_parallel_source"),
                    d["s0_offset"])
            # 第五分册 deferred：缺口形态同第三、四分册
            if d["s0_offset"] in BATCH5_S0:
                ev = {e["witness"]: e for e in d["witness_evidence"]}
                self.assertEqual(
                    ev["NiuTrans/Classical-Modern"]["attestation"],
                    "not_located", d["s0_offset"])
                self.assertIn(
                    ev["youngzs/xuanxue"]["attestation"],
                    ("not_located", "attested_parallel_source"),
                    d["s0_offset"])
            # 第十一分册 deferred：缺口形态同第三至十分册
            if d["s0_offset"] in BATCH11_S0:
                ev = {e["witness"]: e for e in d["witness_evidence"]}
                self.assertEqual(
                    ev["NiuTrans/Classical-Modern"]["attestation"],
                    "not_located", d["s0_offset"])
                self.assertEqual(
                    ev["youngzs/xuanxue"]["attestation"],
                    "not_located", d["s0_offset"])
            # 第十分册 deferred：缺口形态同第三至九分册
            if d["s0_offset"] in BATCH10_S0:
                ev = {e["witness"]: e for e in d["witness_evidence"]}
                self.assertEqual(
                    ev["NiuTrans/Classical-Modern"]["attestation"],
                    "not_located", d["s0_offset"])
                self.assertIn(
                    ev["youngzs/xuanxue"]["attestation"],
                    ("not_located", "attested_parallel_source"),
                    d["s0_offset"])
            # 第九分册 deferred：缺口形态同第三至八分册
            if d["s0_offset"] in BATCH9_S0:
                ev = {e["witness"]: e for e in d["witness_evidence"]}
                self.assertEqual(
                    ev["NiuTrans/Classical-Modern"]["attestation"],
                    "not_located", d["s0_offset"])
                self.assertIn(
                    ev["youngzs/xuanxue"]["attestation"],
                    ("not_located", "attested_parallel_source"),
                    d["s0_offset"])
            # 第八分册 deferred：缺口形态同第三至七分册
            if d["s0_offset"] in BATCH8_S0:
                ev = {e["witness"]: e for e in d["witness_evidence"]}
                self.assertEqual(
                    ev["NiuTrans/Classical-Modern"]["attestation"],
                    "not_located", d["s0_offset"])
                self.assertIn(
                    ev["youngzs/xuanxue"]["attestation"],
                    ("not_located", "attested_parallel_source"),
                    d["s0_offset"])
            # 第七分册 deferred：缺口形态同第三至六分册
            if d["s0_offset"] in BATCH7_S0:
                ev = {e["witness"]: e for e in d["witness_evidence"]}
                self.assertEqual(
                    ev["NiuTrans/Classical-Modern"]["attestation"],
                    "not_located", d["s0_offset"])
                self.assertIn(
                    ev["youngzs/xuanxue"]["attestation"],
                    ("not_located", "attested_parallel_source"),
                    d["s0_offset"])
            # 第六分册 deferred：缺口形态同第三至五分册
            if d["s0_offset"] in BATCH6_S0:
                ev = {e["witness"]: e for e in d["witness_evidence"]}
                self.assertEqual(
                    ev["NiuTrans/Classical-Modern"]["attestation"],
                    "not_located", d["s0_offset"])
                self.assertIn(
                    ev["youngzs/xuanxue"]["attestation"],
                    ("not_located", "attested_parallel_source"),
                    d["s0_offset"])
        rd = [d for d in deferred if d.get("rd12_seq")]
        self.assertEqual(len(rd), 1)
        self.assertEqual(rd[0]["s0_offset"], 184318)
        self.assertEqual(rd[0]["rd12_seq"], 450)
        self.assertEqual(rd[0]["defer_reason"],
                         "reading_disagreement_rd12_p3_scope")
        # RD-12 双方证据在案：四库䕶 vs 现代获
        ev = {e["witness"]: e for e in rd[0]["witness_evidence"]}
        self.assertEqual(ev["kanripo/KR3g0042"]["site_reading"], "䕶")
        self.assertEqual(
            ev["NiuTrans/Classical-Modern"]["attestation"], "rival")
        self.assertEqual(
            ev["NiuTrans/Classical-Modern"]["site_reading"], "获")

    def test_tranche_plan(self):
        plan = REG["tranche_plan"]
        self.assertEqual(plan["disposed_cumulative"], "161/769")
        self.assertEqual(plan["deferred_in_registered_sections"], 29)
        self.assertEqual(plan["deferred_total"], 601)
        self.assertEqual([t["event"] for t in plan["tranches_done"]],
                         ["E0302", "E0304", "E0306", "E0308", "E0310", "E0312", "E0314", "E0316", "E0318", "E0320", "E0322"])
        self.assertEqual(sum(t["pending"]
                             for t in plan["pending_by_volume"]), 7)
        computed = Counter(x["volume"] for x in INV
                           if x["disposition"] == "pending_later_tranche")
        self.assertEqual({t["volume"]: t["pending"]
                          for t in plan["pending_by_volume"]},
                         dict(computed))

    def test_immutability_statement(self):
        self.assertIn("零文本改动", REG["immutability"])
        self.assertIn("canonical_ready 保持 false", REG["immutability"])


if __name__ == "__main__":
    unittest.main()
