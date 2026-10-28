"""TJ-012.3 证据登记批（滴天髓《化象》章整章登记，E0270 待办 B4）的
公开结构测试。

本模块（``bazi_ditiansui_huaxiang``）是纯数据证据登记、零计算逻辑；
本测试只钉登记结构与红线（整章登记形制、13 段平铺、引文 19 条分层、
层属覆盖、两套条件表述要素结构、同题异述关系登记、字形疑点落账、
禁止 determination 语义键、E0270 登记册不改口径），不验证任何化气/
从化判定（不存在此种代码路径）。引文逐字等值与快照复核在密封专项
``tests/test_tj0123_ditiansui_huaxiang_sealed.py``（仅离线验收）。
"""

from __future__ import annotations

import inspect
import json
import unittest
from pathlib import Path

from tianji_kb import bazi_ditiansui_huaxiang as hx

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / "tests" / "golden_tj0123_ditiansui_huaxiang.json").read_text(
        encoding="utf-8"))

FORBIDDEN_KEYS = {
    "determination", "true_false", "pattern_established", "verdict",
    "useful_god", "success_failure", "purity",
    "真格", "假格", "成格", "破格", "清浊", "用神",
}

ELEMENT_KEYS = {
    "subject", "month_condition", "hour_condition", "third_stem_blocker",
    "multiplicity", "wangqi", "root_qi", "commander", "chen_factor",
    "strength_polarity", "result_element", "huashen_xiji",
}


def _walk_keys(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield k
            yield from _walk_keys(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _walk_keys(v)


class MirrorTest(unittest.TestCase):
    def test_module_mirrors_golden(self) -> None:
        self.assertEqual(hx.DITIANSHUI_SNAPSHOT, GOLDEN["snapshot"])
        self.assertEqual(hx.HUAXIANG_CHAPTER, GOLDEN["chapter"])
        self.assertEqual(hx.HUAXIANG_SEGMENTS, GOLDEN["segments"])
        self.assertEqual(hx.HUAXIANG_QUOTES, GOLDEN["quotes"])
        self.assertEqual(hx.HUAXIANG_CONDITION_STRUCTURE,
                         GOLDEN["condition_structure"])
        self.assertEqual(hx.HUAXIANG_RELATIONS, GOLDEN["relations"])
        self.assertEqual(hx.HUAXIANG_GLYPH_NOTES, GOLDEN["glyph_notes"])
        self.assertEqual(hx.HUAXIANG_NOTES, GOLDEN["notes"])
        self.assertEqual(hx.HUAXIANG_LIMITATIONS, GOLDEN["limitations"])
        self.assertEqual(hx.HUAXIANG_REGISTRATION_STATUS,
                         GOLDEN["registration_status"])

    def test_module_is_pure_data_no_functions(self) -> None:
        funcs = [n for n, _ in inspect.getmembers(hx, inspect.isfunction)]
        classes = [n for n, _ in inspect.getmembers(hx, inspect.isclass)]
        self.assertEqual(funcs, [])
        self.assertEqual(classes, [])


class ChapterRegistrationTest(unittest.TestCase):
    def test_chapter_registered_full(self) -> None:
        ch = hx.HUAXIANG_CHAPTER
        self.assertEqual(ch["section_id"], "ditiansui.huaxiang")
        self.assertEqual(ch["registration_mode"], "full_chapter")
        self.assertEqual(ch["locator"],
                         {"char_start": 98297, "char_end": 99943})
        self.assertEqual(ch["title_locator"],
                         {"char_start": 98297, "char_end": 98302})
        self.assertEqual(len(ch["full_text"]), 1646)
        self.assertTrue(ch["full_text"].startswith("十三、化象\n"))
        self.assertEqual(ch["placeholder_count_in_chapter"], 0)
        self.assertEqual(ch["pua_count_in_chapter"], 0)
        self.assertNotIn("?", ch["full_text"])
        self.assertEqual(ch["audit_ref"],
                         "docs/product/BAZI_PATTERN_AUDIT.md P05")

    def test_layer_markers_at_pinned_offsets(self) -> None:
        text = hx.HUAXIANG_CHAPTER["full_text"]
        base = hx.HUAXIANG_CHAPTER["locator"]["char_start"]
        self.assertEqual(text[98320 - base:98323 - base], "原注:")
        self.assertEqual(text[98508 - base:98512 - base], "任氏曰:")


class SegmentTilingTest(unittest.TestCase):
    def test_thirteen_segments_tile_the_chapter(self) -> None:
        segs = hx.HUAXIANG_SEGMENTS
        self.assertEqual(len(segs), 13)
        pos = 98297
        for s in segs:
            loc = s["locator"]
            self.assertEqual(loc["char_start"], pos, s["segment_id"])
            self.assertGreater(loc["char_end"], loc["char_start"],
                               s["segment_id"])
            pos = loc["char_end"]
        self.assertEqual(pos, 99943)

    def test_layers_cover_all_four_kinds(self) -> None:
        layers = [s["layer"] for s in hx.HUAXIANG_SEGMENTS]
        self.assertEqual(layers.count("原注"), 1)
        self.assertEqual(layers.count("任氏曰"), 1)
        self.assertEqual(layers.count("任氏曰（例造）"), 5)
        self.assertEqual(layers.count("空白填充"), 5)
        self.assertEqual(layers.count("章题＋章题句"), 1)

    def test_segment_slices_rebuild_full_text(self) -> None:
        text = hx.HUAXIANG_CHAPTER["full_text"]
        base = hx.HUAXIANG_CHAPTER["locator"]["char_start"]
        for s in hx.HUAXIANG_SEGMENTS:
            loc = s["locator"]
            piece = text[loc["char_start"] - base:loc["char_end"] - base]
            if s["layer"] == "空白填充":
                self.assertLessEqual(set(piece), {" ", "\n"},
                                     s["segment_id"])
            else:
                self.assertTrue(piece.strip(), s["segment_id"])

    def test_example_segments_carry_nine_chart_lines(self) -> None:
        examples = [s for s in hx.HUAXIANG_SEGMENTS
                    if s["layer"] == "任氏曰（例造）"]
        self.assertEqual(len(examples), 5)
        quote_ids = {q["id"] for q in hx.HUAXIANG_QUOTES}
        for s in examples:
            self.assertEqual(len(s["chart_lines"]), 9, s["segment_id"])
            self.assertIn(s["commentary_quote_id"], quote_ids)
            seg = s["locator"]
            for line in s["chart_lines"]:
                loc = line["locator"]
                self.assertGreaterEqual(loc["char_start"],
                                        seg["char_start"])
                self.assertLessEqual(loc["char_end"], seg["char_end"])
                self.assertEqual(loc["char_end"] - loc["char_start"],
                                 len(line["text"]))


class QuoteRegistrationTest(unittest.TestCase):
    def test_nineteen_quotes_layered(self) -> None:
        quotes = hx.HUAXIANG_QUOTES
        self.assertEqual(len(quotes), 19)
        by_layer = {}
        for q in quotes:
            by_layer[q["layer"]] = by_layer.get(q["layer"], 0) + 1
        self.assertEqual(by_layer, {"章题句": 1, "原注": 4, "任氏曰": 9,
                                    "任氏曰（例造）": 5})

    def test_quotes_slice_equal_against_registered_full_text(self) -> None:
        text = hx.HUAXIANG_CHAPTER["full_text"]
        base = hx.HUAXIANG_CHAPTER["locator"]["char_start"]
        seen = set()
        for q in hx.HUAXIANG_QUOTES:
            self.assertNotIn(q["id"], seen)
            seen.add(q["id"])
            self.assertEqual(q["source_id"],
                             "bazi.source.ditiansui-spouse")
            loc = q["locator"]
            self.assertEqual(loc["char_end"] - loc["char_start"],
                             len(q["quote"]), q["id"])
            self.assertEqual(
                text[loc["char_start"] - base:loc["char_end"] - base],
                q["quote"], q["id"])

    def test_quotes_stay_inside_their_segments(self) -> None:
        segs = {s["segment_id"]: s for s in hx.HUAXIANG_SEGMENTS}
        for q in hx.HUAXIANG_QUOTES:
            seg = segs[q["segment_id"]]
            self.assertGreaterEqual(q["locator"]["char_start"],
                                    seg["locator"]["char_start"], q["id"])
            self.assertLessEqual(q["locator"]["char_end"],
                                 seg["locator"]["char_end"], q["id"])
            self.assertEqual(q["layer"], seg["layer"]
                             if seg["layer"] != "章题＋章题句" else "章题句",
                             q["id"])
        for s in hx.HUAXIANG_SEGMENTS:
            if "quote_ids" in s:
                self.assertEqual(
                    s["quote_ids"],
                    [q["id"] for q in hx.HUAXIANG_QUOTES
                     if q["segment_id"] == s["segment_id"]],
                    s["segment_id"])

    def test_p05_anchor_quote(self) -> None:
        verse = next(q for q in hx.HUAXIANG_QUOTES
                     if q["id"] == "hx.head_verse")
        self.assertEqual(verse["locator"],
                         {"char_start": 98303, "char_end": 98319})
        self.assertEqual(verse["quote"], "化得真者只论化,化神还有几般话。")


class ConditionStructureTest(unittest.TestCase):
    def test_two_formulations_registered_unadjudicated(self) -> None:
        forms = hx.HUAXIANG_CONDITION_STRUCTURE["formulations"]
        self.assertEqual([f["id"] for f in forms], ["F5", "F6"])
        self.assertEqual([f["layer"] for f in forms], ["原注", "任氏曰"])
        for f in forms:
            self.assertTrue(f["registered_in_this_batch"], f["id"])
            self.assertIsNone(f["adjudication"], f["id"])
            self.assertEqual(f["status"], "registered_unadjudicated")
            self.assertEqual(set(f["elements"]), ELEMENT_KEYS, f["id"])

    def test_element_evidence_quotes_resolve(self) -> None:
        quote_ids = {q["id"] for q in hx.HUAXIANG_QUOTES}
        glyph_ids = {g["id"] for g in hx.HUAXIANG_GLYPH_NOTES}
        for f in hx.HUAXIANG_CONDITION_STRUCTURE["formulations"]:
            for name, elem in f["elements"].items():
                for qid in elem["evidence"]:
                    self.assertIn(qid, quote_ids, (f["id"], name))
                for gid in elem.get("glyph_refs", []):
                    self.assertIn(gid, glyph_ids, (f["id"], name))

    def test_commander_absent_in_both_formulations(self) -> None:
        for f in hx.HUAXIANG_CONDITION_STRUCTURE["formulations"]:
            self.assertTrue(
                f["elements"]["commander"]["text"].startswith("absent"),
                f["id"])

    def test_relation_to_f1_f4_is_same_topic_only(self) -> None:
        cs = hx.HUAXIANG_CONDITION_STRUCTURE
        self.assertEqual(cs["relation_to_sanming_f1_f4"],
                         "same_topic_different_statements")
        self.assertFalse(cs["merged_into_hehua_conflict_structure"])


class RelationsTest(unittest.TestCase):
    def test_four_relations_recorded_e0270_unchanged(self) -> None:
        rels = hx.HUAXIANG_RELATIONS
        self.assertEqual([r["id"] for r in rels],
                         ["hx-rel-01", "hx-rel-02", "hx-rel-03",
                          "hx-rel-04"])
        for r in rels:
            self.assertFalse(r["e0270_conclusions_changed"], r["id"])
        kinds = {r["id"]: r["relation"] for r in rels}
        self.assertEqual(kinds["hx-rel-01"],
                         "same_topic_different_statements")
        self.assertEqual(kinds["hx-rel-02"],
                         "registration_basis_now_supplied")
        self.assertEqual(kinds["hx-rel-03"],
                         "different_adjudication_object")
        self.assertEqual(kinds["hx-rel-04"],
                         "audit_entry_superseded_by_registration")
        self.assertIn("P-D1", rels[2]["note"])
        self.assertIn("P-D2", rels[2]["note"])


class GlyphRegisterTest(unittest.TestCase):
    def test_ten_glyph_notes_all_unresolved(self) -> None:
        notes = hx.HUAXIANG_GLYPH_NOTES
        self.assertEqual(len(notes), 10)
        self.assertEqual([g["id"] for g in notes],
                         [f"hx-glyph-{i:02d}" for i in range(1, 11)])
        quote_ids = {q["id"] for q in hx.HUAXIANG_QUOTES}
        for g in notes:
            self.assertIsNone(g["mapped_reading"], g["id"])
            self.assertIn(g["quote_id"], quote_ids, g["id"])
            if "position" in g:
                self.assertTrue(98297 <= g["position"] < 99943, g["id"])
            else:
                span = g["span"]
                self.assertTrue(98297 <= span["char_start"]
                                < span["char_end"] <= 99943, g["id"])

    def test_quote_glyph_refs_resolve(self) -> None:
        glyph_ids = {g["id"] for g in hx.HUAXIANG_GLYPH_NOTES}
        for q in hx.HUAXIANG_QUOTES:
            for gid in q.get("glyph_refs", []):
                self.assertIn(gid, glyph_ids, q["id"])


class DisciplineTest(unittest.TestCase):
    def test_no_determination_semantics_anywhere(self) -> None:
        data = [hx.HUAXIANG_CHAPTER, hx.HUAXIANG_SEGMENTS,
                hx.HUAXIANG_QUOTES, hx.HUAXIANG_CONDITION_STRUCTURE,
                hx.HUAXIANG_RELATIONS, hx.HUAXIANG_GLYPH_NOTES]
        for blob in data:
            for key in _walk_keys(blob):
                self.assertNotIn(key, FORBIDDEN_KEYS)
        self.assertIn("登记≠可判", hx.HUAXIANG_NOTES[0])

    def test_registration_status_red_lines(self) -> None:
        st = hx.HUAXIANG_REGISTRATION_STATUS
        self.assertTrue(st["research_only"])
        self.assertFalse(st["public_enabled"])
        self.assertFalse(st["ai_enabled"])
        self.assertFalse(st["determination_surface_changed"])
        self.assertFalse(st["hehua_register_changed"])
        self.assertEqual(st["transformation_status"], "unresolved")
        self.assertEqual(st["canonical_phase1_registration"], "pending")
        self.assertEqual(st["pending_decisions_unchanged"],
                         ["P-D1", "P-D2"])


if __name__ == "__main__":
    unittest.main()
