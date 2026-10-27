"""TJ-013.1 S3（扶抑三段登记）的公开结构测试：滴天髓扶抑证据登记。

本模块（``bazi_ditiansui_fuyi``）是纯数据证据登记、零计算逻辑；
本测试只钉登记结构与红线（三段登记形制与层属、判句清单与量化
词未阈值化标注、输出性质为取用方向非分类、方向表十行逐行转写
与顺序重演、疑讹登记无校定读法、同文传录交叉注记不作独立见证、
禁止扶抑判定语义键），不验证任何扶抑判定（不存在此种代码路
径）。引文逐字等值与快照复核在密封专项
``tests/test_tj0131_ditiansui_fuyi_sealed.py``（仅离线验收）。
"""

from __future__ import annotations

import inspect
import json
import unittest
from pathlib import Path

from tianji_kb import bazi_ditiansui_fuyi as fy

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / "tests" / "golden_tj0131_ditiansui_fuyi.json").read_text(
        encoding="utf-8"))

FORBIDDEN_KEYS = {
    "determination", "true_false", "verdict", "threshold",
    "quantifier_threshold", "fuyi_result", "support_suppress_result",
    "扶抑结果", "扶抑判定", "用神裁定",
}

UQ = "quantifier_unthresholded"
DIR = "direction_not_classification"


def _walk_keys(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield k
            yield from _walk_keys(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _walk_keys(v)


def _all_quantifier_entries():
    for q in fy.FUYI_QUOTES:
        for s in q["judgment_sentences"]:
            yield from s["quantifiers"]
    for r in fy.FUYI_DIRECTION_TABLE["rows"]:
        yield from r["condition_quantifiers"]


class MirrorTest(unittest.TestCase):
    def test_module_mirrors_golden(self) -> None:
        self.assertEqual(fy.DITIANSHUI_SNAPSHOT, GOLDEN["snapshot"])
        self.assertEqual(fy.CROSS_SNAPSHOTS, GOLDEN["cross_snapshots"])
        self.assertEqual(fy.FUYI_PASSAGES, GOLDEN["passages"])
        self.assertEqual(fy.FUYI_QUOTES, GOLDEN["quotes"])
        self.assertEqual(fy.FUYI_DIRECTION_TABLE,
                         GOLDEN["direction_table"])
        self.assertEqual(fy.FUYI_GLYPH_NOTES, GOLDEN["glyph_notes"])
        self.assertEqual(fy.FUYI_CROSS_REFERENCES,
                         GOLDEN["cross_references"])
        self.assertEqual(fy.FUYI_NOTES, GOLDEN["notes"])
        self.assertEqual(fy.FUYI_LIMITATIONS, GOLDEN["limitations"])

    def test_module_is_pure_data_no_functions(self) -> None:
        funcs = [n for n, _ in inspect.getmembers(fy, inspect.isfunction)]
        classes = [n for n, _ in inspect.getmembers(fy, inspect.isclass)]
        self.assertEqual(funcs, [])
        self.assertEqual(classes, [])


class PassageRegistrationTest(unittest.TestCase):
    def test_three_passages_registered(self) -> None:
        passages = {p["passage_id"]: p for p in fy.FUYI_PASSAGES}
        self.assertEqual(set(passages), {
            "ditiansui.fuyi_shaiwang",
            "ditiansui.fuyi_xingxiang",
            "ditiansui.fuyi_tiyong",
        })
        self.assertEqual(passages["ditiansui.fuyi_shaiwang"]["chapter"],
                         "十七、衰旺")
        self.assertEqual(passages["ditiansui.fuyi_xingxiang"]["chapter"],
                         "十、形象")
        self.assertEqual(passages["ditiansui.fuyi_tiyong"]["chapter"],
                         "十三、体用")
        for p in passages.values():
            self.assertEqual(p["source_id"],
                             "bazi.source.ditiansui-spouse")
            self.assertEqual(
                {q["id"] for q in fy.FUYI_QUOTES
                 if q["passage_id"] == p["passage_id"]},
                set(p["quote_ids"]))

    def test_quotes_inside_passage_spans(self) -> None:
        spans = {p["passage_id"]: p["span"] for p in fy.FUYI_PASSAGES}
        self.assertEqual(len(fy.FUYI_QUOTES), 10)
        for q in fy.FUYI_QUOTES:
            span = spans[q["passage_id"]]
            self.assertGreaterEqual(q["locator"]["char_start"],
                                    span["char_start"], q["id"])
            self.assertLessEqual(q["locator"]["char_end"],
                                 span["char_end"], q["id"])
            self.assertEqual(
                q["locator"]["char_end"] - q["locator"]["char_start"],
                len(q["quote"]), q["id"])
            self.assertEqual(q["source_id"],
                             "bazi.source.ditiansui-spouse")

    def test_layers_explicit_per_quote(self) -> None:
        layers = {q["id"]: q["layer"] for q in fy.FUYI_QUOTES}
        self.assertEqual(layers["fy.shaiwang_yuanzhu"], "原注")
        self.assertEqual(layers["fy.shaiwang_u2"], "任氏曰")
        self.assertEqual(layers["fy.xingxiang_verse"], "诗句")
        self.assertEqual(layers["fy.xingxiang_yuanzhu"], "原注")
        self.assertEqual(layers["fy.xingxiang_renshi_restatement"],
                         "任氏曰")
        self.assertEqual(layers["fy.xingxiang_renshi_differentiation"],
                         "任氏曰")
        for qid in ("fy.tiyong_general_rule", "fy.tiyong_tigang",
                    "fy.tiyong_table_para"):
            self.assertEqual(layers[qid], "任氏曰", qid)


class AnnotationTest(unittest.TestCase):
    def test_judgment_sentences_are_verbatim_substrings(self) -> None:
        total = 0
        for q in fy.FUYI_QUOTES:
            for s in q["judgment_sentences"]:
                total += 1
                off = s["locator"]["char_start"] - q["locator"]["char_start"]
                self.assertEqual(
                    q["quote"][off:off + len(s["text"])], s["text"],
                    (q["id"], s["text"]))
                self.assertEqual(
                    s["locator"]["char_end"] - s["locator"]["char_start"],
                    len(s["text"]))
        # F-1 7 + U2 1 + verse 2 + xingxiang yuanzhu 3 + restatement 3
        # + differentiation 10 + tiyong general 6 + tigang 3 + table 2
        self.assertEqual(total, 37)

    def test_every_quantifier_marked_unthresholded(self) -> None:
        entries = list(_all_quantifier_entries())
        self.assertEqual(len(entries), 27)
        for e in entries:
            self.assertEqual(e["status"], UQ)
            self.assertTrue(e["term"])

    def test_output_nature_is_direction_not_classification(self) -> None:
        for q in fy.FUYI_QUOTES:
            if q["role"] == "chapter_head":
                self.assertEqual(q["output_nature"],
                                 "chapter_framing_not_a_rule")
            elif q["id"] == "fy.shaiwang_u2":
                self.assertEqual(
                    q["output_nature"],
                    "capability_statement_not_classification")
            elif q["id"] == "fy.xingxiang_yuanzhu":
                self.assertEqual(
                    q["output_nature"],
                    "form_classification_partial_enumeration")
            else:
                self.assertEqual(q["output_nature"], DIR, q["id"])

    def test_counter_clauses_registered_with_f1(self) -> None:
        f1 = next(q for q in fy.FUYI_QUOTES
                  if q["id"] == "fy.shaiwang_yuanzhu")
        kinds = [s["kind"] for s in f1["judgment_sentences"]]
        self.assertEqual(kinds.count("general_rule"), 2)
        self.assertEqual(
            sum(1 for k in kinds if k.startswith("counter_clause")), 5)

    def test_u2_registered_as_unplaced_capability_statement(self) -> None:
        u2 = next(q for q in fy.FUYI_QUOTES if q["id"] == "fy.shaiwang_u2")
        self.assertEqual(u2["role"], "capability_statement_unplaced")
        self.assertIn("无此陈述的落点", u2["note"])
        self.assertEqual(len(u2["judgment_sentences"]), 1)
        self.assertEqual(u2["judgment_sentences"][0]["kind"],
                         "capability_statement")


class DirectionTableTest(unittest.TestCase):
    def test_ten_rows_measured_not_eight(self) -> None:
        table = fy.FUYI_DIRECTION_TABLE
        self.assertEqual(table["scout_row_count"], 8)
        self.assertEqual(table["measured_row_count"], 10)
        self.assertEqual(len(table["rows"]), 10)
        self.assertIn("以实测为准", table["note"])

    def test_rows_replay_the_table_body_verbatim(self) -> None:
        para = next(q for q in fy.FUYI_QUOTES
                    if q["id"] == "fy.tiyong_table_para")
        table = fy.FUYI_DIRECTION_TABLE
        lead = table["lead_in"] + ","
        start = para["quote"].index(lead) + len(lead)
        end = para["quote"].index(table["closing"])
        body = para["quote"][start:end]
        self.assertEqual("".join(r["text"] for r in table["rows"]), body)
        # rows tile contiguously at their registered locators
        base = table["body_locator"]["char_start"]
        self.assertEqual(base, para["locator"]["char_start"] + start)
        cursor = base
        for r in table["rows"]:
            self.assertEqual(r["locator"]["char_start"], cursor)
            cursor = r["locator"]["char_end"]
            self.assertEqual(
                r["locator"]["char_end"] - r["locator"]["char_start"],
                len(r["text"]))
        self.assertEqual(cursor, table["body_locator"]["char_end"])

    def test_row_directions_and_premises(self) -> None:
        rows = fy.FUYI_DIRECTION_TABLE["rows"]
        self.assertEqual([r["direction_god"] for r in rows],
                         ["财星", "财星", "食伤", "食伤", "财星",
                          "印绶", "印绶", "比劫", "食伤", "印比"])
        self.assertEqual([r["premise_day_master_state"] for r in rows],
                         ["旺"] * 5 + ["弱"] * 3 + ["两停", "均敌"])
        for r in rows:
            self.assertEqual(r["output_nature"], DIR)
            self.assertTrue(r["condition_quantifiers"])

    def test_two_bijie_rows_kept_separate(self) -> None:
        rows = fy.FUYI_DIRECTION_TABLE["rows"]
        bijie = [r for r in rows if "比劫多" in r["text"]]
        self.assertEqual(len(bijie), 2)
        self.assertIn("耐我财星", bijie[0]["text"])
        self.assertIn("而财星轻", bijie[1]["text"])


class GlyphNotesTest(unittest.TestCase):
    def test_eight_glyph_notes_all_unresolved(self) -> None:
        self.assertEqual(len(fy.FUYI_GLYPH_NOTES), 8)
        for g in fy.FUYI_GLYPH_NOTES:
            self.assertIsNone(g["mapped_reading"], g["id"])
            self.assertTrue(
                g["status"].endswith("_preserved"), g["id"])

    def test_glyph_positions_inside_their_quotes(self) -> None:
        quotes = {q["id"]: q for q in fy.FUYI_QUOTES}
        for g in fy.FUYI_GLYPH_NOTES:
            q = quotes[g["quote_id"]]
            if "position" in g:
                off = g["position"] - q["locator"]["char_start"]
                self.assertEqual(q["quote"][off], g["char"], g["id"])
            else:
                a = g["span"]["char_start"] - q["locator"]["char_start"]
                b = g["span"]["char_end"] - q["locator"]["char_start"]
                self.assertEqual(q["quote"][a:b],
                                 "衰之极者不可所当损者而损之", g["id"])


class CrossReferenceTest(unittest.TestCase):
    def test_four_cross_references_not_independent(self) -> None:
        self.assertEqual(len(fy.FUYI_CROSS_REFERENCES), 4)
        for x in fy.FUYI_CROSS_REFERENCES:
            self.assertEqual(x["witness_status"],
                             "same_text_transmission_not_independent")
            self.assertFalse(x["scope_expanded"])

    def test_same_text_pair_substance_equal(self) -> None:
        xrefs = {x["id"]: x for x in fy.FUYI_CROSS_REFERENCES}
        sanming = xrefs["fy-xref-01"]["quote"]
        shenfeng = xrefs["fy-xref-02"]["quote"]
        self.assertEqual(shenfeng.replace("。", ""), sanming)
        self.assertNotEqual(shenfeng, sanming)  # 神峰本有句读

    def test_xiaoxi_notes_are_luck_not_original_chart(self) -> None:
        xrefs = {x["id"]: x for x in fy.FUYI_CROSS_REFERENCES}
        self.assertEqual(xrefs["fy-xref-03"]["kind"],
                         "xiaoxi_fu_commentary_on_luck")
        self.assertIn("运之支神", xrefs["fy-xref-04"]["segments"][0]["quote"])
        self.assertIn("亦未善", xrefs["fy-xref-04"]["segments"][1]["quote"])


class DisciplineTest(unittest.TestCase):
    def test_no_determination_or_threshold_semantics(self) -> None:
        data = [fy.FUYI_PASSAGES, fy.FUYI_QUOTES, fy.FUYI_DIRECTION_TABLE,
                fy.FUYI_GLYPH_NOTES, fy.FUYI_CROSS_REFERENCES]
        for blob in data:
            for key in _walk_keys(blob):
                self.assertNotIn(key, FORBIDDEN_KEYS)
        self.assertIn("登记≠可执行", fy.FUYI_NOTES[0])
        self.assertIn("双重受阻", fy.FUYI_NOTES[0])

    def test_limitations_keep_fuyi_unbuilt(self) -> None:
        joined = "".join(fy.FUYI_LIMITATIONS)
        self.assertIn("扶抑判定未建", joined)
        self.assertIn("S4", joined)
        self.assertIn("S2", joined)


if __name__ == "__main__":
    unittest.main()
