"""TJ-010.1: Public code/source boundary regression (private originals tested separately)."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def source(path):
    return (ROOT / path).read_text(encoding="utf-8")


def test_source_registry_pins_actual_classical_texts():
    registry = json.loads(source("config/knowledge_sources.json"))
    rows = {row["source_id"]: row for row in registry["sources"]}
    for key in ("bazi.source.yuanhai", "bazi.source.ditiansui-spouse"):
        entry = rows[key]
        assert entry["evidence_level"] == "C"
        assert re.fullmatch(r"[0-9a-f]{40}", entry["commit"])
        assert re.fullmatch(r"[0-9a-f]{64}", entry["sha256"])
        assert entry["content_path"].startswith("data/quarantine/")


def test_report_distinguishes_secondary_implementation_and_approved_s004():
    audit = source("docs/product/audits/tj0101-bazi-evidence-audit.md")
    assert "jinchenma94/bazi-skill" in audit
    assert "bazi.section.s004" in audit
    assert "737" in audit
    assert "60/30/10" in audit
    assert "不得一键" in audit
    assert "应标记为 `secondary_pending`" not in audit


def test_public_factor_does_not_derive_total_strength():
    code = source("src/tianji_kb/bazi_strength.py")
    assert "'overall_strength': None" in code
    assert "'effective_strength': None" in code
    assert "'full_strength_classifier_ready': False" in code
    assert "司令分日有原典口径差异，未裁定" in code


def test_root_candidates_have_no_effective_weight_model():
    code = source("src/tianji_kb/bazi_root_conditions.py")
    assert "'weights_available': False" in code
    assert "'position_weights_available': False" in code
    assert "'branch_relation_effect': 'unresolved'" in code


def test_bounded_adjudication_research_only_not_public():
    code = source("src/tianji_kb/bazi_adjudication.py")
    assert "'research_only':True" in code
    assert "'public_enabled':False" in code
    assert "'ai_enabled':False" in code
    assert "'weights_available':False" in code


def test_no_private_canonical_in_public_repo():
    assert not (ROOT / "data/canonical/bazi/foundations_v1.json").exists()
    assert not (ROOT / "data/canonical/bazi/phase1_knowledge.json").exists()
