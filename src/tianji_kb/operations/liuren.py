import json
from pathlib import Path
from .liuyao import STEMS, BRANCHES
from ..foundations import CONTROLS, ELEMENTS


def base():
    return json.loads((Path(__file__).resolve().parents[3]/'data/canonical/liuren/rules_v1.json').read_text())


def month_general(solar_term):
    for row in base()['month_general_by_solar_terms']:
        if solar_term in row['terms']:
            return row.copy()
    raise ValueError('Unknown solar term')


def sky_plate(month_general,hour_branch):
    if month_general not in list(BRANCHES) or hour_branch not in list(BRANCHES):
        raise ValueError('Expected single branch symbols')
    shift=(BRANCHES.index(month_general)-BRANCHES.index(hour_branch))%12
    return {branch:BRANCHES[(i+shift)%12] for i,branch in enumerate(BRANCHES)}


def validate_sky(sky):
    if set(sky)!=set(BRANCHES) or set(sky.values())!=set(BRANCHES):
        raise ValueError('Expected complete branch permutation')
    shifts={(BRANCHES.index(sky[b])-BRANCHES.index(b))%12 for b in BRANCHES}
    if len(shifts)!=1:
        raise ValueError('Sky plate must be a cyclic rotation')


def four_lessons(day_stem,day_branch,sky):
    validate_sky(sky)
    if day_stem not in list(STEMS) or day_branch not in list(BRANCHES):
        raise ValueError('Invalid day stem/branch')
    if (STEMS.index(day_stem)-BRANCHES.index(day_branch))%2:
        raise ValueError('Day stem/branch polarity mismatch')
    lodging=base()['stem_lodging'][day_stem]
    first=sky[lodging]
    third=sky[day_branch]
    return [{'lesson':1,'upper':first,'lower':day_stem},{'lesson':2,'upper':sky[first],'lower':first},{'lesson':3,'upper':third,'lower':day_branch},{'lesson':4,'upper':sky[third],'lower':third}]


def follow_transmissions(initial,sky):
    validate_sky(sky)
    if initial not in list(BRANCHES):
        raise ValueError('Invalid initial branch')
    # Initial selection and special-case methods are deliberately outside this function.
    middle=sky[initial]
    return [initial,middle,sky[middle]]


def noble_start(day_stem,day_night,variant):
    if day_stem not in list(STEMS) or day_night not in ('昼','夜') or str(variant) not in ('0','1'):
        raise ValueError('Expected valid stem, day/night and explicit variant 0 or 1')
    table=base()['heavenly_generals']['noble_start_variants'][str(variant)]
    return next(value[day_night] for group,value in table.items() if day_stem in group)


# ---------------------------------------------------------------------------
# O-03 (TJ-0426 Lane 5): compiled initial-transmission selection.
#
# What this is: a standalone transcription of the nine-method selection
# that `liuren_chart.select()` performs inline. It adds no doctrine and
# changes no rule: `liuren_chart.py` (variant
# `daquan-nine-methods-lodged-stems-v1`, 11 Golden Cases) is left
# untouched as the reference implementation, and this compiled form is
# verified against it by equivalence (see
# tests/test_tj0426_lane5_liuren.py: all 60 days x 12 hours for 雨水
# plus the 11 Golden Cases, data-gated).
#
# What this is not: a new transmission rule, a heavenly-general
# (天将/贵人)排法, or any auspiciousness judgment. Outputs carry
# research_only=true, public=false, ai=false and no verdict.
#
# Lodging rule (fail-closed): the ten-stem lodging table
# (十干寄宫) is NEVER defaulted here. It lives only in the sealed
# rules file (`base()['stem_lodging']`) and must be supplied by the
# caller. In particular the bazi禄 table must never be substituted:
# the bazi collation reads 戊寄巳/己寄午
# (bazi_sanming_juan3_collation), which is a different table from the
# liuren lodging. Paths that do not consult lodging (贼克 single
# candidate, 伏吟, 返吟, 八专, 昴星) accept stem_lodging=None; the
# 涉害 depth path and the 别责 path raise naming the missing table
# instead of guessing.
# ---------------------------------------------------------------------------

COMPILED_VARIANT = 'daquan-nine-methods-compiled-v1'
COMPILED_REFERENCE = 'daquan-nine-methods-lodged-stems-v1'

# Same literal as liuren_chart.PUNISH (kept as the single compiled copy;
# the chart module keeps its own literal; a test pins them equal).
FUYIN_PUNISH = dict(zip('寅巳申丑戌未子卯辰午酉亥', '巳申寅戌未丑卯子辰午酉亥'))

# 返吟无贼克候选时的驿马分支（与 chart 实现同一组对照）。
FANYIN_HORSE_GROUPS = (('申子辰', '寅'), ('寅午戌', '申'), ('巳酉丑', '亥'), ('亥卯未', '巳'))


def _advance(branch, n):
    return BRANCHES[(BRANCHES.index(branch) + n) % 12]


# Branch -> element, as a module constant (子水丑土寅木卯木辰土巳火午火
# 未土申金酉金戌土亥水）. foundations.branch_element() reads the same
# mapping from the sealed seed table; a data-gated test pins this
# literal equal to that table for all 12 branches, so the compiled
# selector stays pure (locally runnable) without ever reading data/.
BRANCH_ELEMENTS = dict(zip('子丑寅卯辰巳午未申酉戌亥', '水土木木土火火土金金土水'))


def _element(symbol):
    if symbol in STEMS:
        return ELEMENTS[STEMS.index(symbol) // 2]
    return BRANCH_ELEMENTS[symbol]


def _controls(a, b):
    return CONTROLS[_element(a)] == _element(b)


def _same_polarity(a, b):
    return (BRANCHES.index(a) - STEMS.index(b)) % 2 == 0


def _control_candidates(lessons):
    lower = [lesson['upper'] for lesson in lessons if _controls(lesson['lower'], lesson['upper'])]
    upper = [lesson['upper'] for lesson in lessons if _controls(lesson['upper'], lesson['lower'])]
    return list(dict.fromkeys(lower or upper)), bool(lower)


def _validate_compiled_inputs(day, sky, lessons):
    validate_sky(sky)
    if (not isinstance(day, str) or len(day) != 2 or day[0] not in list(STEMS)
            or day[1] not in list(BRANCHES)
            or (STEMS.index(day[0]) - BRANCHES.index(day[1])) % 2):
        raise ValueError('Invalid day ganzhi (stem/branch polarity mismatch)')
    if (not isinstance(lessons, (list, tuple)) or len(lessons) != 4
            or any(not isinstance(lesson, dict) or lesson.get('upper') not in list(BRANCHES)
                   or lesson.get('lower') not in list(STEMS) + list(BRANCHES)
                   for lesson in lessons)):
        raise ValueError('Expected four lessons of {upper: branch, lower: stem-or-branch}')


def _require_lodging(stem_lodging, needed):
    if stem_lodging is None:
        raise ValueError(
            'Stem lodging table is required for this path and is never defaulted; '
            'supply stem_lodging explicitly (e.g. base()["stem_lodging"]); '
            'missing stems: %s' % ','.join(needed))
    missing = [stem for stem in needed if stem not in stem_lodging
               or stem_lodging[stem] not in list(BRANCHES)]
    if missing:
        raise ValueError(
            'Stem lodging table lacks valid entries for: %s; '
            'lodging is never defaulted or borrowed from the bazi table' % ','.join(missing))
    return stem_lodging


def _choose_initial(candidates, lower_controls, day, sky, lessons, stem_lodging):
    """Transcription of the 贼克/比用/涉害 choice (chart `choose`)."""
    if len(candidates) == 1:
        return candidates[0], '贼克', {}
    same = [s for s in candidates if _same_polarity(s, day[0])]
    if len(same) == 1:
        return same[0], '比用', {'polarity_candidates': same}
    pool = same or candidates
    inverse = {s: e for e, s in sky.items()}
    lodging = _require_lodging(stem_lodging, list(STEMS))
    depths = {}
    for candidate in pool:
        start = inverse[candidate]
        depth = 0
        for i in range((BRANCHES.index(candidate) - BRANCHES.index(start)) % 12 + 1):
            place = _advance(start, i)
            obstacles = [place] + [stem for stem in STEMS if lodging[stem] == place]
            depth += sum(_controls(x, candidate) if lower_controls else _controls(candidate, x)
                         for x in obstacles)
        depths[candidate] = depth
    best = [s for s in pool if depths[s] == max(depths.values())]
    rank = lambda s: 0 if inverse[s] in '寅申巳亥' else 1 if inverse[s] in '子午卯酉' else 2
    best = [s for s in best if rank(s) == min(rank(x) for x in best)]
    if len(best) > 1:
        preferred = lessons[0]['upper'] if STEMS.index(day[0]) % 2 == 0 else lessons[2]['upper']
        if preferred in best:
            best = [preferred]
    if len(best) != 1:
        raise ValueError(f'Unresolved Shehai tie for this variant: {day}/{depths}')
    return best[0], '涉害', {'depths': depths, 'earth_positions': {s: inverse[s] for s in pool}}


def select_initial_transmission(day, sky, lessons, stem_lodging=None):
    """Compile the nine-method initial-transmission choice.

    Returns (method, initial, details). `stem_lodging` is required only
    on the 涉害/别责 paths (see _require_lodging); other paths accept
    None. The middle/final transmissions are NOT chosen here; use
    complete_transmissions() for the full triple, including the
    伏吟/返吟 special branches.
    """
    _validate_compiled_inputs(day, sky, lessons)
    candidates, lower = _control_candidates(lessons)
    yang = STEMS.index(day[0]) % 2 == 0
    first, third = lessons[0]['upper'], lessons[2]['upper']
    shift = (BRANCHES.index(sky['子']) - BRANCHES.index('子')) % 12
    details = {'control_candidates': candidates, 'lower_controls_upper': lower,
               'distinct_uppers': len({lesson['upper'] for lesson in lessons})}
    if shift == 0:
        initial = candidates[0] if candidates else first if yang else third
        return '伏吟', initial, details
    if candidates:
        initial, method, selection = _choose_initial(candidates, lower, day, sky, lessons, stem_lodging)
        details.update(selection, selection_method=method)
        return '返吟' if shift == 6 else method, initial, details
    if shift == 6:
        horse = next(v for group, v in FANYIN_HORSE_GROUPS if day[1] in group)
        return '返吟', horse, details
    distinct = details['distinct_uppers']
    if distinct == 2:
        initial = _advance(first, 2) if yang else _advance(lessons[3]['upper'], -2)
        return '八专', initial, details
    uppers = list(dict.fromkeys(lesson['upper'] for lesson in lessons))
    remote = [s for s in uppers if _controls(s, day[0])] or [s for s in uppers if _controls(day[0], s)]
    if remote:
        same = [s for s in remote if _same_polarity(s, day[0])]
        selected = same or remote
        if len(selected) != 1:
            raise ValueError('Unresolved remote-control candidates')
        details['remote_candidates'] = remote
        return '遥克', selected[0], details
    if distinct == 3:
        other = STEMS[(STEMS.index(day[0]) + 5) % 10]
        if yang:
            _require_lodging(stem_lodging, [other])
            initial = sky[stem_lodging[other]]
        else:
            initial = _advance(day[1], 4)
        return '别责', initial, details
    if distinct == 4:
        initial = sky['酉'] if yang else next(e for e, s in sky.items() if s == '酉')
        return '昴星', initial, details
    raise ValueError('Unsupported lesson structure')


def complete_transmissions(method, initial, day, sky, lessons, stem_lodging=None, details=None):
    """Derive [initial, middle, final] for a chosen method.

    Special branches (transcribed from chart `select`):
    - 伏吟: middle/final follow the 刑 (PUNISH) chain with fallbacks.
    - 返吟: horse branch -> [horse, third, first]; with control
      candidates (details carries selection_method) -> sky succession.
    - 八专/别责: [initial, first, first].
    - 昴星: [initial, third, first] (yang day) / [initial, first, third].
    - 贼克/比用/涉害/遥克: sky succession.
    """
    _validate_compiled_inputs(day, sky, lessons)
    if initial not in list(BRANCHES):
        raise ValueError('Invalid initial branch')
    details = details or {}
    yang = STEMS.index(day[0]) % 2 == 0
    first, third = lessons[0]['upper'], lessons[2]['upper']
    if method == '伏吟':
        middle = FUYIN_PUNISH[initial]
        if middle == initial:
            middle = third if yang else first
        final = FUYIN_PUNISH[middle]
        if final == middle or final == initial:
            final = _advance(middle, 6)
        return [initial, middle, final]
    if method == '返吟' and 'selection_method' not in details:
        return [initial, third, first]
    if method in ('八专', '别责'):
        return [initial, first, first]
    if method == '昴星':
        return [initial, third, first] if yang else [initial, first, third]
    if method in ('贼克', '比用', '涉害', '遥克', '返吟'):
        return [initial, sky[initial], sky[sky[initial]]]
    raise ValueError('Unknown transmission method: %r' % (method,))


def compile_transmissions(day, sky, lessons, stem_lodging=None):
    """Full compiled nine-method selection: (method, [i, m, f], details).

    Output envelope carries the research flags; no verdict is produced.
    """
    method, initial, details = select_initial_transmission(day, sky, lessons, stem_lodging)
    transmissions = complete_transmissions(method, initial, day, sky, lessons, stem_lodging, details)
    return {'method': method, 'transmissions': transmissions, 'selection': details,
            'variant': COMPILED_VARIANT, 'reference_variant': COMPILED_REFERENCE,
            'research_only': True, 'public': False, 'ai': False,
            'evidence_level': 'C', 'verdict': None}


# O-03 gap registry: what the compiled selector does NOT cover. The
# heavenly-general (天将/贵人) table stays partially structured until
# its two variants are collated line by line; noble_start() is a
# software-table lookup, never classical truth on its own.
NOBLE_VARIANT_REGISTRY = {
    '0': {'status': 'partially_structured', 'evidence_level': 'C',
          'note': '贵人昼夜表 variant 0；逐句核定前不升级规则状态。'},
    '1': {'status': 'partially_structured', 'evidence_level': 'C',
          'note': '贵人昼夜表 variant 1；逐句核定前不升级规则状态。'},
}

LIUREN_GAPS = {
    'noble_table_collation': {'status': 'gap', 'evidence_level': 'C',
        'note': '贵人表两种 variant 未逐句核定；天将排法未建。'},
    'heavenly_generals': {'status': 'gap', 'evidence_level': 'C',
        'note': '天将（贵人）排布未接入 chart 输出；limitations 已明记。'},
    'verdict': {'status': 'gap', 'evidence_level': 'D',
        'note': '无吉凶结论层；三传只作结构事实。'},
}


def noble_variant_status(variant):
    """Return the registry entry for a noble-start variant (no lookup)."""
    key = str(variant)
    if key not in NOBLE_VARIANT_REGISTRY:
        raise ValueError('Unknown noble-start variant: %r (expected 0 or 1)' % (variant,))
    return dict(NOBLE_VARIANT_REGISTRY[key])
