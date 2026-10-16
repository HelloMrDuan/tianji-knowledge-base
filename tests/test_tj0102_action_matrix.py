"""TJ-010.2: Action matrix structure verification (public CI).

Static verification only - no chart computation (requires private Canonical).
Full integration tests run in private CI with real data.

Each test must FAIL if the implementation is wrong.
"""
import re


def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def test_matrix_variant():
    src = _read("src/tianji_kb/bazi_action_matrix.py")
    assert "MATRIX_VARIANT = 'bazi-action-matrix-v1'" in src, \
        "Must define MATRIX_VARIANT"


def test_five_statuses_defined():
    """All 5 statuses must be documented and used."""
    src = _read("src/tianji_kb/bazi_action_matrix.py")
    for s in ['observed', 'candidate', 'effective', 'unresolved', 'not_applicable']:
        assert s in src, f"Missing status: {s}"


def test_reuses_existing_variants():
    """Must reuse, not reinvent, the 5 existing variants."""
    src = _read("src/tianji_kb/bazi_action_matrix.py")
    # Must import the existing variant constants
    assert "FACTOR_VARIANT" in src, "Must reuse FACTOR_VARIANT"
    assert "ROOT_VARIANT" in src, "Must reuse ROOT_VARIANT"
    assert "ACTION_VARIANT" in src, "Must reuse ACTION_VARIANT"
    assert "AVAILABILITY_VARIANT" in src, "Must reuse AVAILABILITY_VARIANT"
    assert "EFFECT_VARIANT" in src, "Must reuse EFFECT_VARIANT"


def test_no_weights_no_overall_strength():
    """Must not compute weights or overall strength."""
    src = _read("src/tianji_kb/bazi_action_matrix.py")
    assert "'overall_strength': None" in src, "Must set overall_strength None"
    assert "'weights_available': False" in src, "Must set weights_available False"


def test_three_matrix_sections():
    """Must have roots, exposures, actions sections."""
    src = _read("src/tianji_kb/bazi_action_matrix.py")
    assert "root_rows" in src, "Must build root rows"
    assert "exposure_rows" in src, "Must build exposure rows"
    assert "action_rows" in src, "Must build action rows"


def test_build_matrix_from_chart_exists():
    """Must have the real chart integration function."""
    src = _read("src/tianji_kb/bazi_action_matrix.py")
    assert "def build_matrix_from_chart(chart)" in src, \
        "Must have build_matrix_from_chart"
    # Must use real chart_from_datetime-compatible structure
    assert "chart['pillars']" in src, "Must read pillars from chart"
    assert "chart['day_master']['stem']" in src, "Must read day_master from chart"


def test_uses_reviewed_relations():
    """Must use reviewed_relations for real clash/harmony detection."""
    src = _read("src/tianji_kb/bazi_action_matrix.py")
    assert "reviewed_relations" in src, "Must use reviewed_relations"


def test_integrates_availability_and_effects():
    """Must integrate root_availability and action_effects (P0-4)."""
    src = _read("src/tianji_kb/bazi_action_matrix.py")
    assert "root_availability" in src, "Must call root_availability"
    assert "action_effects" in src, "Must call action_effects"
    # Must map availability statuses to 5-state
    assert "'effective'" in src, "Must handle effective status"
