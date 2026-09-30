#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
canonical = ROOT / "data/canonical"

def load(rel: str):
    return json.loads((canonical / rel).read_text(encoding="utf-8"))

seed = load("seed.json")
zhouyi = load("yijing/zhouyi_classic_core.json")
zhouyi_commentary = load("yijing/tuan_xiang_wenyan_v1.json")
zhouyi_relations = load("yijing/hexagram_relations_v1.json")
bazi_foundations = load("bazi/foundations_v1.json")
dayun = load("bazi/dayun_v1.json")
shensha = load("bazi/shensha_v1.json")
liuyao = load("liuyao/najia_v1.json")
meihua = load("meihua/rules_v1.json")
ziwei = load("ziwei/iztro_rules_v1.json")
qimen = load("qimen/qfdk_maoshan_v1.json")
liuren_catalog = load("liuren/classics_catalog_v1.json")
liuren_rules = load("liuren/rules_v1.json")
taiyi_catalog = load("taiyi/classics_catalog_v1.json")
taiyi_rules = load("taiyi/rules_v1.json")
tarot = load("tarot/rws_cn_v1.json")
zeri = load("zeri/zeri_core_v1.json")
almanac = load("almanac/scoring_v1.json")
fengshui_calc = load("fengshui/calculation_v1.json")
fengshui_schools = load("fengshui/schools_v1.json")
fengshui_mountains = load("fengshui/twenty_four_mountains_v1.json")
hetu_luoshu = load("foundations/hetu_luoshu_v1.json")
yuanhai = load("classics/bazi/yuanhai_ziping_v1.json")
qiongtong = load("classics/bazi/qiongtong_baojian_v1.json")
ditiansui = load("classics/bazi/ditiansui_chanwei_v1.json")

registry = json.loads((ROOT / "config/source_registry.json").read_text(encoding="utf-8"))["sources"]
ingestion = json.loads((ROOT / "config/ingestion_manifest.json").read_text(encoding="utf-8"))
public_domain_manifest = json.loads((ROOT / "config/public_domain_manifest.json").read_text(encoding="utf-8"))

errors: list[str] = []

def check(condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)

# Foundations
check(len(seed.get("wuxing", [])) == 5, "seed.wuxing must contain 5 elements")
check(len(seed.get("heavenly_stems", [])) == 10, "seed.heavenly_stems must contain 10 stems")
check(len(seed.get("earthly_branches", [])) == 12, "seed.earthly_branches must contain 12 branches")
check(len(seed.get("trigrams", [])) == 8, "seed.trigrams must contain 8 trigrams")
check(len(seed.get("hexagrams", [])) == 64, "seed.hexagrams must contain 64 hexagrams")
check(len({x[0] for x in seed.get("hexagrams", [])}) == 64, "seed hexagram numbers must be unique")

# Zhouyi core
records = zhouyi.get("records", [])
check(len(records) == 64, "Zhouyi classic corpus must contain 64 hexagrams")
check({x["number"] for x in records} == set(range(1, 65)), "Zhouyi classic corpus numbers must be 1..64")
line_count = sum(len(x.get("lines", [])) for x in records)
check(line_count == 384, "Zhouyi classic corpus must contain exactly 384 ordinary line texts")
special_uses = [x.get("special_use") for x in records if x.get("special_use")]
check(len(special_uses) == 2, "Zhouyi classic corpus must preserve Qian Yongjiu and Kun Yongliu")
check({x["position"] for x in special_uses} == {"用九", "用六"}, "special uses must be 用九 and 用六")
check(all(x.get("judgment") for x in records), "every Zhouyi hexagram must have a judgment")
check(all(x.get("image") for x in records), "every Zhouyi hexagram must have an image text")

# Tuan / Xiang / Wenyan structured commentary
commentary_records = zhouyi_commentary.get("records", [])
check(len(commentary_records) == 64, "Tuan/Xiang corpus must contain 64 hexagrams")
check(sum(1 for x in commentary_records if x.get("tuan")) == 64, "every hexagram must have Tuan")
check(sum(1 for x in commentary_records if x.get("great_image")) == 64, "every hexagram must have Great Image")
check(sum(len(x.get("line_images", [])) for x in commentary_records) == 386, "Xiang corpus must contain 384 ordinary line images plus 用九/用六")
check({x["number"] for x in commentary_records if x.get("wenyan")} == {1, 2}, "Wenyan must attach to Qian and Kun")

# Deterministic hexagram relations
relation_records = zhouyi_relations.get("records", [])
check(len(relation_records) == 64, "hexagram relation graph must contain 64 records")
check(all(x.get("opposite") and x.get("reversed") and x.get("nuclear") for x in relation_records), "each hexagram must have opposite/reversed/nuclear relations")
check(all(len(x.get("line_changes", [])) == 6 for x in relation_records), "each hexagram must have six one-line change relations")

# Ten Wings general appendices
ten_wings = {
    name: load(f"yijing/ten_wings/{name}.json")
    for name in ("xici_shang", "xici_xia", "shuogua", "xugua", "zagua")
}
min_lengths = {"xici_shang": 2500, "xici_xia": 2500, "shuogua": 1000, "xugua": 1000, "zagua": 350}
for name, obj in ten_wings.items():
    text = obj.get("normalized_text", "")
    check(obj.get("source_level") == "L0-public-domain-classic", f"{name} must be L0 classic")
    check(len(text) >= min_lengths[name], f"{name} text unexpectedly short")
    check("□" not in text and "�" not in text, f"{name} contains unresolved replacement characters")
    check(obj.get("provenance", {}).get("primary", {}).get("commit"), f"{name} lacks pinned source commit")

# Bazi / Liuyao / Meihua
check(len(bazi_foundations.get("heavenly_stems", [])) == 10, "Bazi foundations must have 10 stems")
check(len(bazi_foundations.get("hidden_stems", {})) == 12, "Bazi foundations must have 12 hidden-stem entries")
check(len(dayun.get("direction_rules", [])) == 4, "Dayun must define 4 direction rules")
check(len(shensha.get("items", [])) >= 20, "Shensha rules must contain at least 20 items")
check(len(liuyao.get("najia", {})) == 8, "Liuyao Najia must contain 8 pure trigrams")
check(meihua.get("ruleset") == "classic-implementation-v1", "Meihua ruleset id mismatch")

# Ziwei
check(len(ziwei.get("palaces", [])) == 12, "Ziwei must contain 12 palaces")
check(len(ziwei.get("major_stars", [])) == 14, "Ziwei must contain 14 major stars")
four = ziwei.get("four_transformations", {})
check(len(four) == 10, "Ziwei four-transformations must cover 10 heavenly stems")
check(all(len(v) == 4 for v in four.values()), "every Ziwei stem must map to 4 transformations")

# Qimen
check(len(qimen.get("nine_palaces", {})) == 9, "Qimen must contain 9 palaces")
check(len(qimen.get("nine_stars", {})) == 9, "Qimen must contain 9 stars")
check(len(qimen.get("eight_doors", {})) == 8, "Qimen must contain 8 doors")
check(len(qimen.get("eight_deities", [])) == 8, "Qimen must contain 8 deities")
check(len(qimen.get("solar_term_bureaus", [])) == 24, "Qimen bureau table must contain 24 solar terms")
check(len(qimen.get("canonical_terms", {}).get("san_qi", [])) == 3, "Qimen sanqi must contain 3 stems")
check(len(qimen.get("canonical_terms", {}).get("liu_yi", [])) == 6, "Qimen liuyi must contain 6 stems")

# Daliuren / Taiyi bibliography
check(liuren_catalog.get("record_count", 0) >= 120, "Daliuren bibliography unexpectedly small")
check(taiyi_catalog.get("record_count", 0) >= 90, "Taiyi bibliography unexpectedly small")

# Daliuren rules
check(len(liuren_rules.get("month_general_by_solar_terms", [])) == 12, "Daliuren must contain 12 month-general pairs")
check(len(liuren_rules.get("heavenly_generals", {}).get("order", [])) == 12, "Daliuren must contain 12 heavenly generals")
check(len(liuren_rules.get("three_transmissions", {}).get("engine_selection_precedence", [])) == 8, "Daliuren engine must expose 8 transmission selection methods")
check(len(liuren_rules.get("day_night", {}).get("day_branches", [])) == 6, "Daliuren day branches must contain 6 branches")
check(len(liuren_rules.get("day_night", {}).get("night_branches", [])) == 6, "Daliuren night branches must contain 6 branches")
check(set(liuren_rules.get("branch_relations", {}).get("clash", {}).keys()) == set("子丑寅卯辰巳午未申酉戌亥"), "Daliuren clash table must cover 12 branches")

# Taiyi rules
check(len(taiyi_rules.get("classical_methods", {})) == 4, "Taiyi must contain 4 main classical methods")
check(len(taiyi_rules.get("taiyi_palace", {}).get("yang_72", [])) == 72, "Taiyi Yang Dun palace sequence must contain 72 bureaus")
check(len(taiyi_rules.get("taiyi_palace", {}).get("yin_72", [])) == 72, "Taiyi Yin Dun palace sequence must contain 72 bureaus")
check(set(taiyi_rules.get("taiyi_palace", {}).get("valid_palace_numbers", [])) == {1,2,3,4,6,7,8,9}, "Taiyi palace sequence must exclude center 5 and 0")
check(taiyi_rules.get("eight_doors", {}).get("base_order") == ["开","休","生","伤","杜","景","死","惊"], "Taiyi Eight Doors base order mismatch")
check(len(taiyi_rules.get("sixteen_palaces", [])) == 16, "Taiyi must contain 16 palaces")
check(len(taiyi_rules.get("luoshu_outer_order", [])) == 8, "Taiyi outer Luo Shu order must contain 8 palaces")

# Tarot
check(tarot.get("record_count") == 78, "Tarot must contain 78 cards")
check(tarot.get("spread_count") == 9, "Tarot must contain 9 spreads")
tarot_counts = tarot.get("counts", {})
check(tarot_counts.get("MajorArcana") == 22, "Tarot must contain 22 major arcana")
check(sum(int(v) for v in tarot_counts.values()) == 78, "Tarot suit counts must sum to 78")

# Zeri / Almanac
check(len(zeri.get("events", {})) == 10, "Zeri must contain 10 recognized event types")
check(len(zeri.get("branch_clashes", {})) == 12, "Zeri must cover 12 branch clashes")
check(len(zeri.get("sha_direction", {})) == 12, "Zeri must cover 12 sha directions")
fixed = almanac.get("fixed_inauspicious", {})
check(len(fixed.get("yang_gong_13_avoid", [])) == 13, "Almanac Yang Gong avoid list must contain 13 dates")
check(len(fixed.get("san_niang_sha_lunar_days", [])) == 6, "Almanac Sanniang list must contain 6 lunar days")
check(len(fixed.get("shi_e_da_bai_jiazi", [])) == 10, "Almanac Shi E Da Bai list must contain 10 Jiazi")

# Fengshui
luoshu_calc = fengshui_calc.get("luoshu", {})
check(len(fengshui_calc.get("san_yuan_periods", [])) == 9, "Fengshui must contain 9 San Yuan periods")
check(len(luoshu_calc.get("palace_numbers", {})) == 9, "Fengshui Luo Shu must contain 9 palaces")
check(len(luoshu_calc.get("flight_path", [])) == 9, "Fengshui Luo Shu flight path must contain 9 palaces")
check(len(fengshui_calc.get("ming_gua", {}).get("directions", {})) == 8, "Eight Mansions Ming Gua must contain 8 non-center gua mappings")
check(len(fengshui_schools.get("schools", [])) >= 7, "Fengshui school separation must list at least 7 methods")
mountains = fengshui_mountains.get("records", [])
check(len(mountains) == 24, "Fengshui 24-mountain compass must contain 24 sectors")
check(len({x.get("mountain") for x in mountains}) == 24, "Fengshui 24 mountains must be unique")
check(len({x.get("compass_label") for x in mountains}) == 24, "Fengshui compass labels must be unique")
check(all(x.get("center_degrees") == (x.get("index") * 15) % 360 for x in mountains), "Fengshui mountain center degrees must advance by 15 degrees")
check(all(x.get("opposite", {}).get("index") == (x.get("index") + 12) % 24 for x in mountains), "Fengshui opposite mountains must differ by 180 degrees")
check(mountains[0].get("mountain") == "子" and mountains[0].get("compass_label") == "N2", "Fengshui 24 mountains must start from 子/N2")
check(mountains[-1].get("mountain") == "壬" and mountains[-1].get("compass_label") == "N1", "Fengshui 24 mountains must end at 壬/N1")

# Hetu / Luoshu
hetu_pairs = hetu_luoshu.get("hetu", {}).get("pairs", [])
check(len(hetu_pairs) == 5, "Hetu must contain 5 generating/completing pairs")
check(all(x["completing"] - x["generating"] == 5 for x in hetu_pairs), "Hetu pair difference must be 5")
matrix = hetu_luoshu.get("luoshu", {}).get("matrix_south_up", [])
check(matrix == [[4,9,2],[3,5,7],[8,1,6]], "Luo Shu matrix mismatch")
if len(matrix) == 3:
    lines = matrix + [list(x) for x in zip(*matrix)] + [[matrix[i][i] for i in range(3)], [matrix[i][2-i] for i in range(3)]]
    check(all(sum(line) == 15 for line in lines), "Every Luo Shu row/column/diagonal must sum to 15")
check(len(hetu_luoshu.get("luoshu", {}).get("nine_palaces", [])) == 9, "Luo Shu must contain 9 palace mappings")

# Public-domain Bazi classics
check(yuanhai.get("source_level") == "L0-public-domain-classic", "Yuanhai Ziping must be L0 classic")
check(yuanhai.get("section_count", 0) >= 180, "Yuanhai Ziping section count unexpectedly small")
check(sum(len(x.get("text", "")) for x in yuanhai.get("sections", [])) >= 55000, "Yuanhai Ziping text unexpectedly short")
check(yuanhai.get("cleaning", {}).get("replacement_chars") == 0, "Yuanhai Ziping contains unresolved replacement chars")
check(qiongtong.get("source_level") == "L0-public-domain-classic", "Qiongtong Baojian must be L0 classic")
check(qiongtong.get("section_count", 0) >= 95, "Qiongtong Baojian section count unexpectedly small")
check(sum(len(x.get("text", "")) for x in qiongtong.get("sections", [])) >= 30000, "Qiongtong Baojian text unexpectedly short")
check(qiongtong.get("cleaning", {}).get("replacement_chars") == 0, "Qiongtong Baojian contains unresolved replacement chars")
check(ditiansui.get("source_level") == "L0-public-domain-classic", "Ditiansui Chanwei must be L0 classic")
check(ditiansui.get("section_count") == 63, "Ditiansui Chanwei must contain 63 topic sections")
check(sum(len(x.get("text", "")) for x in ditiansui.get("sections", [])) >= 120000, "Ditiansui Chanwei text unexpectedly short")
check(ditiansui.get("cleaning", {}).get("replacement_chars") == 0, "Ditiansui Chanwei contains unresolved replacement chars")
check(ditiansui.get("cleaning", {}).get("private_use_chars") == 0, "Ditiansui Chanwei contains private-use glyphs")

# Licensing and ingestion guardrails
valid_policies = {"ALLOW","REFERENCE_ONLY","PUBLIC_DOMAIN_EXTRACT_ONLY","NON_COMMERCIAL","COPYLEFT","QUARANTINE"}
check(len({x["repo"] for x in registry}) == len(registry), "duplicate source repositories")
by_id = {x["id"]: x for x in registry}
check(len(by_id) == len(registry), "duplicate source ids")
for source in registry:
    check(source["license_policy"] in valid_policies, f"invalid license policy: {source['repo']}")
    if source.get("license_spdx") is None and source["license_policy"] == "ALLOW":
        errors.append(f"unlicensed source cannot be ALLOW: {source['repo']}")

for group in public_domain_manifest.get("sources", []):
    source = by_id.get(group["source_id"])
    check(source is not None, f"public-domain manifest references unknown source: {group['source_id']}")
    if source:
        check(
            source["license_policy"] == "PUBLIC_DOMAIN_EXTRACT_ONLY",
            f"public-domain manifest source has wrong policy: {source['repo']}",
        )
    for work in group.get("works", []):
        check(bool(work.get("path")), f"public-domain work missing path: {work.get('id')}")
        if work.get("promotion") == "canonical":
            check(bool(work.get("output")), f"canonical public-domain work missing output: {work.get('id')}")
            check(bool(work.get("parser")), f"canonical public-domain work missing parser: {work.get('id')}")
        if work.get("promotion") == "quarantine_only":
            planned = work.get("planned_output") or work.get("output")
            if planned:
                check(
                    not (ROOT / planned).exists(),
                    f"quarantined public-domain work leaked into canonical: {work.get('id')} -> {planned}",
                )

# Sanming Tonghui PUA collation gate
sanming_audit_path = ROOT / "data/quarantine/public_domain_snapshots/daizhigev20/sanming_pua_audit.json"
sanming_collation_path = ROOT / "data/quarantine/public_domain_snapshots/daizhigev20/sanming_pua_collation.json"
sanming_source_path = ROOT / "data/quarantine/public_domain_snapshots/daizhigev20/sanming_tonghui.txt"

check(sanming_audit_path.exists(), "Sanming PUA audit is missing")
check(sanming_collation_path.exists(), "Sanming PUA collation map is missing")
check(sanming_source_path.exists(), "Sanming quarantined source is missing")

if sanming_audit_path.exists() and sanming_collation_path.exists():
    audit = json.loads(sanming_audit_path.read_text(encoding="utf-8"))
    collation = json.loads(sanming_collation_path.read_text(encoding="utf-8"))
    audit_rows = {x["codepoint"]: x for x in audit.get("glyphs", [])}
    mappings = collation.get("mappings", [])
    codes = [x.get("codepoint") for x in mappings]
    check(len(codes) == len(set(codes)), "Sanming collation contains duplicate codepoints")

    def is_private_use_char(ch: str) -> bool:
        cp = ord(ch)
        return (
            0xE000 <= cp <= 0xF8FF
            or 0xF0000 <= cp <= 0xFFFFD
            or 0x100000 <= cp <= 0x10FFFD
        )

    confirmed = []
    for row in mappings:
        codepoint = row.get("codepoint")
        glyph = row.get("glyph", "")
        replacement = row.get("replacement", "")
        status = row.get("status")
        check(status in {"confirmed", "provisional", "unresolved"}, f"invalid Sanming mapping status: {codepoint}")
        check(codepoint in audit_rows, f"Sanming mapping not present in audit: {codepoint}")
        if len(glyph) == 1:
            check(is_private_use_char(glyph), f"Sanming mapping glyph is not PUA: {codepoint}")
            check(codepoint == f"U+{ord(glyph):04X}", f"Sanming mapping codepoint/glyph mismatch: {codepoint}")
        else:
            check(False, f"Sanming mapping glyph must be one character: {codepoint}")
        if codepoint in audit_rows:
            check(row.get("count") == audit_rows[codepoint].get("count"), f"Sanming mapping count mismatch: {codepoint}")
            check(glyph == audit_rows[codepoint].get("glyph"), f"Sanming mapping glyph mismatch with audit: {codepoint}")
        if status == "confirmed":
            confirmed.append(row)
            check(bool(replacement), f"confirmed Sanming mapping missing replacement: {codepoint}")
            check(not any(is_private_use_char(ch) for ch in replacement), f"confirmed Sanming replacement still contains PUA: {codepoint}")
            check(len(row.get("source_anchors", [])) >= min(2, int(row.get("count", 0))), f"confirmed Sanming mapping lacks source anchors: {codepoint}")
            check(len(row.get("evidence", [])) >= 2, f"confirmed Sanming mapping lacks cross-check evidence: {codepoint}")

    confirmed_occurrences = sum(int(x.get("count", 0)) for x in confirmed)
    summary = collation.get("summary", {})
    check(summary.get("audit_total_occurrences") == audit.get("total_private_use_chars"), "Sanming audit total drift")
    check(summary.get("audit_unique_codepoints") == audit.get("unique_private_use_chars"), "Sanming audit unique-count drift")
    check(summary.get("confirmed_mappings") == len(confirmed), "Sanming confirmed mapping summary mismatch")
    check(summary.get("confirmed_occurrences") == confirmed_occurrences, "Sanming confirmed occurrence summary mismatch")
    check(summary.get("remaining_unique_codepoints") == audit.get("unique_private_use_chars") - len(confirmed), "Sanming remaining unique-count mismatch")
    check(summary.get("remaining_occurrences") == audit.get("total_private_use_chars") - confirmed_occurrences, "Sanming remaining occurrence mismatch")

    if sanming_source_path.exists():
        raw = sanming_source_path.read_text(encoding="utf-8")
        for row in confirmed:
            check(raw.count(row["glyph"]) == row["count"], f"Sanming source drift for {row['codepoint']}")
            raw = raw.replace(row["glyph"], row["replacement"])
        remaining = [ch for ch in raw if is_private_use_char(ch)]
        check(len(remaining) == summary.get("remaining_occurrences"), "Sanming post-collation PUA occurrence mismatch")
        check(len(set(remaining)) == summary.get("remaining_unique_codepoints"), "Sanming post-collation PUA unique-count mismatch")

    niu = by_id.get("niutrans-classical-modern")
    check(niu is not None, "NiuTrans collation source is not registered")
    if niu:
        check(niu.get("license_spdx") == "MIT", "NiuTrans source must preserve MIT license metadata")
        check(niu.get("license_policy") == "ALLOW", "NiuTrans source must be ALLOW")

for entry in ingestion.get("sources", []):
    source = by_id.get(entry["source_id"])
    check(source is not None, f"ingestion manifest references unknown source: {entry['source_id']}")
    if source:
        check(source["license_policy"] == "ALLOW", f"auto-ingestion source is not ALLOW: {source['repo']}")

if errors:
    print("\n".join(errors))
    raise SystemExit(1)

print(
    f"Knowledge base validation passed: {len(registry)} sources; "
    f"Zhouyi=64 hexagrams/{line_count}+2 special-use texts/386 Xiang units/5 Ten-Wings sections; "
    f"Bazi shensha={len(shensha['items'])}; Ziwei=14 major stars; "
    f"Qimen=9 palaces/24 solar-term bureaus; "
    f"Daliuren={liuren_catalog['record_count']} bibliography/8 transmission methods; "
    f"Taiyi={taiyi_catalog['record_count']} bibliography/72+72 palace rules; "
    f"Tarot={tarot['record_count']} cards/{tarot['spread_count']} spreads; "
    f"Zeri={len(zeri['events'])} events; Hetu/Luoshu=5 pairs/9 palaces; "
    f"Fengshui=24 mountains; "
    f"Bazi classics={yuanhai['section_count']}+{qiongtong['section_count']}+"
    f"{ditiansui['section_count']} canonical sections; Sanming=quarantine."
)
