"""Qimen inference layer — structural facts only, no verdicts.

O-02 (TJ-0426 Lane 5). The plate itself (局数/地盘/九星/八门/八神)
is computed by operations/qimen_chart.py under ruleset
`qfdk-table-exact-term-v1` (转盘). This module adds the inference
layer's scaffolding:

- A variant registry: only the qfdk exact-term rotating-plate variant
  is implemented. 置闰 / 超接 / 飞盘 are registered as UNMERGED and
  are refused, never silently mixed into a computation.
- `structural_summary()`: restates positional facts already present
  in a chart result (chief star/door palaces, star/door/deity
  positions, bureau/yuan/dun) and explicitly records that no
  inference rule beyond the chief placements is registered — verdict
  is always None. No 吉凶断语 is ever produced.

This module never computes a plate itself and never reads the sealed
tables; it consumes a chart result dict, so its tests run without
data/.
"""

VARIANT = 'qimen-inference-structural-v1'
IMPLEMENTED_RULESET = 'qfdk-table-exact-term-v1'

VARIANT_REGISTRY = {
    'qfdk-table-exact-term-v1': {
        'status': 'implemented', 'plate': '转盘', 'evidence_level': 'C',
        'note': '固定 qfdk 表；节气按准确时刻，非上游整日切换。'},
    '置闰': {'status': 'unmerged', 'evidence_level': 'D',
             'note': '置闰 variant 未登记、未合并；调用即拒绝。'},
    '超接': {'status': 'unmerged', 'evidence_level': 'D',
             'note': '超接 variant 未登记、未合并；调用即拒绝。'},
    '飞盘': {'status': 'unmerged', 'evidence_level': 'D',
             'note': '飞盘 variant 未登记、未合并；调用即拒绝。'},
}

QIMEN_GAPS = {
    'inference_rules': {'status': 'gap', 'evidence_level': 'D',
        'note': '值符值使落宫判断之外的推断规则未登记；无吉凶断语。'},
    'variant_merge': {'status': 'gap', 'evidence_level': 'D',
        'note': '置闰/超接/飞盘 variant 未逐项登记，未合并。'},
}

_REQUIRED_KEYS = ('ruleset', 'solar_term', 'dun', 'bureau', 'yuan',
                  'chief_star_origin', 'chief_star_palace',
                  'chief_door_palace', 'star_positions', 'door_positions',
                  'deity_positions')


def validate_variant(name):
    """Return the registry entry for an implemented variant.

    Unmerged variants (置闰/超接/飞盘) and unknown names raise
    ValueError naming the variant and the reason; there is no fallback.
    """
    entry = VARIANT_REGISTRY.get(name)
    if entry is None:
        raise ValueError('Unknown Qimen variant: %r; no implicit fallback' % (name,))
    if entry['status'] != 'implemented':
        raise ValueError('Qimen variant %r is unmerged (%s); refused, never mixed'
                         % (name, entry['note']))
    return dict(entry)


def structural_summary(chart_result):
    """Restate a qfdk chart's positional facts; verdict always None.

    `chart_result` is a chart dict as produced by
    operations/qimen_chart.chart (or a fixture with the same keys).
    A mismatched ruleset/variant is refused rather than reinterpreted.
    """
    if not isinstance(chart_result, dict):
        raise ValueError('Expected a chart result dict')
    missing = [key for key in _REQUIRED_KEYS if key not in chart_result]
    if missing:
        raise ValueError('Chart result lacks required keys: %s' % ','.join(missing))
    validate_variant(chart_result['ruleset'])
    star_positions = chart_result['star_positions']
    door_positions = chart_result['door_positions']
    deity_positions = chart_result['deity_positions']
    if set(star_positions) != {'天蓬', '天任', '天冲', '天辅', '天英', '天禽', '天芮', '天柱', '天心'}:
        raise ValueError('Expected all nine named stars in star_positions')
    if len(door_positions) != 8 or len(deity_positions) != 8:
        raise ValueError('Expected eight doors and eight deities in positions')
    chief_palace = chart_result['chief_star_palace']
    chief_names = [name for name, palace in star_positions.items() if palace == chief_palace]
    if not chief_names:
        raise ValueError('No star at the chief star palace %r' % (chief_palace,))
    return {'variant': VARIANT, 'ruleset': IMPLEMENTED_RULESET,
            'research_only': True, 'public': False, 'ai': False,
            'evidence_level': 'C', 'verdict': None, 'determination': None,
            'bureau': {'solar_term': chart_result['solar_term'], 'dun': chart_result['dun'],
                       'number': chart_result['bureau'], 'yuan': chart_result['yuan']},
            'chief_star': {'palace': chief_palace,
                           'origin': chart_result['chief_star_origin'],
                           'name': '/'.join(chief_names)},
            'chief_door': {'palace': chart_result['chief_door_palace']},
            'star_positions': dict(star_positions),
            'door_positions': dict(door_positions),
            'deity_positions': dict(deity_positions),
            'inference': {'status': 'structural_only',
                          'note': '仅复述落宫位置事实；值符值使之外的推断规则未登记，无吉凶断语。'}}
