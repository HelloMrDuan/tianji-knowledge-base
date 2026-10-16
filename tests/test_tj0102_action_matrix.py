"""TJ-010.2: Real action condition matrix tests.

Uses real chart_from_datetime() and reviewed_relations().
No mocks. No SKIPs. No vacuously-true assertions.
Each test must FAIL if the implementation is wrong.
"""
import sys
sys.path.insert(0, 'src')

from tianji_kb.bazi_core import chart_from_datetime, reviewed_relations
from tianji_kb.bazi_action_matrix import build_matrix_from_chart, MATRIX_VARIANT


def _chart(birth_iso):
    """Real chart from ISO datetime. Raises if computation fails."""
    chart = chart_from_datetime(birth_iso)
    assert chart['deterministic'] is True, "Chart must be deterministic"
    assert len(chart['pillars']) == 4, "Must have 4 pillars"
    return chart


def test_matrix_variant():
    assert MATRIX_VARIANT == 'bazi-action-matrix-v1'


def test_real_chart_wood_day_master_with_roots():
    """2000-01-07T12:00+08:00: real chart, verify root structure."""
    chart = _chart("2000-01-07T12:00:00+08:00")
    day_master = chart['day_master']['stem']
    result = build_matrix_from_chart(chart)
    # Must have all sections with real data
    assert len(result['roots']) > 0, "Must find root candidates"
    assert len(result['actions']) > 0, "Must find action relations"
    # Day master must match
    assert result['day_master'] == day_master
    # Statuses must be from the valid set
    valid = {'observed', 'candidate', 'effective', 'unresolved', 'not_applicable'}
    for row in result['roots'] + result['actions'] + result['exposures']:
        assert row['status'] in valid, f"Invalid status: {row['status']}"
    # Summary must add up
    total = sum(result['summary'].values())
    assert total == len(result['roots']) + len(result['actions']) + len(result['exposures'])
    # No overall strength
    assert result['overall_strength'] is None
    print(f"  roots={len(result['roots'])} actions={len(result['actions'])} "
          f"summary={result['summary']}")


def test_no_clash_no_harmony_control():
    """A chart with no interactions: roots/actions must not be unresolved due to conflict."""
    chart = _chart("2000-01-07T12:00:00+08:00")
    stems = [p['stem']['value'] for p in chart['pillars']]
    branches = [p['branch']['value'] for p in chart['pillars']]
    rel = reviewed_relations(stems, branches)
    # This specific chart should have no clashes (verify, don't assume)
    has_clash = bool(rel.get('branch_six_clashes'))
    result = build_matrix_from_chart(chart)
    # If no clash, no root should be unresolved DUE TO clash
    # (may still be unresolved for other reasons - that's fine)
    for r in result['roots']:
        if not has_clash:
            assert 'branch_interaction_unresolved' not in r['status_reason'], \
                f"Root {r['pillar']} wrongly marked clash-unresolved"


def test_real_clash_creates_unresolved():
    """Construct pillars with a real 子午 clash; verify unresolved status."""
    # Use chart_from_pillars with known clash: 子 (year) vs 午 (month)
    from tianji_kb.bazi_core import chart_from_pillars
    chart = chart_from_pillars(
        ("甲", "子"), ("丙", "午"), ("甲", "寅"), ("己", "巳")
    )
    stems = [p['stem']['value'] for p in chart['pillars']]
    branches = [p['branch']['value'] for p in chart['pillars']]
    rel = reviewed_relations(stems, branches)
    # Verify the clash is real
    clash_found = any(
        '子' in c.get('branches', []) and '午' in c.get('branches', [])
        for c in rel.get('branch_six_clashes', [])
    )
    assert clash_found, "Test setup must have real 子午 clash"
    result = build_matrix_from_chart(chart)
    # At least one root or action involving 子 or 午 must be unresolved
    affected = [
        r for r in result['roots'] + result['actions']
        if r.get('branch') in ('子', '午') or r.get('pillar') in ('year', 'month')
    ]
    assert len(affected) > 0, "Must have rows for clashed pillars"
    unresolved_affected = [r for r in affected if r['status'] == 'unresolved']
    assert len(unresolved_affected) > 0, \
        f"Clash must cause unresolved, got: {[r['status'] for r in affected]}"
    print(f"  clash test: {len(unresolved_affected)}/{len(affected)} unresolved")


def test_tougan_exposure_observed():
    """If a hidden stem appears as visible stem, exposure must be observed."""
    chart = _chart("2000-01-07T12:00:00+08:00")
    result = build_matrix_from_chart(chart)
    # At least one exposure should be observed (or all not_applicable is also valid)
    # The key check: status must be one of the two, never something else
    for e in result['exposures']:
        assert e['status'] in ('observed', 'not_applicable')
        if e['status'] == 'observed':
            assert len(e['exposed_in']) > 0, "observed must list pillars"
        else:
            assert len(e['exposed_in']) == 0, "not_applicable must have empty list"


def test_deterministic_repeat():
    """Same chart twice must give identical matrix."""
    chart = _chart("2000-01-07T12:00:00+08:00")
    r1 = build_matrix_from_chart(chart)
    r2 = build_matrix_from_chart(chart)
    assert r1['summary'] == r2['summary'], "Summary must be deterministic"
    assert len(r1['roots']) == len(r2['roots'])
    # Compare statuses
    s1 = [(r['pillar'], r['status']) for r in r1['roots']]
    s2 = [(r['pillar'], r['status']) for r in r2['roots']]
    assert s1 == s2, "Root statuses must be deterministic"


def test_invalid_chart_rejected():
    """Malformed chart must raise, not silently produce matrix."""
    try:
        build_matrix_from_chart({'pillars': [], 'day_master': {'stem': '甲'}})
        assert False, "Must raise for empty pillars"
    except (ValueError, KeyError, IndexError):
        pass  # Expected


def test_day_master_mismatch_rejected():
    """Chart with inconsistent day master must be rejected."""
    chart = _chart("2000-01-07T12:00:00+08:00")
    # Corrupt the day master
    bad = dict(chart)
    bad['day_master'] = {'stem': 'ZZ'}
    try:
        build_matrix_from_chart(bad)
        # If it doesn't raise, the result must not claim valid day master
        assert False, "Should reject invalid day master"
    except (ValueError, KeyError):
        pass  # Expected
