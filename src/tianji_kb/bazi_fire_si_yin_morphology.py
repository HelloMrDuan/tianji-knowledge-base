"""TJ-011.2 F3/F4 adjudication register: fire x Si (lu month) and fire x
Yin (changsheng / generating month) strength morphologies.

DESIGN / ADJUDICATION BATCH (E0246). This module registers the F3 and F4
morphology adjudications on top of the fire-line register
(``bazi_fire_morphology.py``, PR #407) and the metal/water root register
(``bazi_metal_water_roots.py``, PR #421). It defines NO predicate and is
imported by NO executable path: adjudication is not implementation.

F3 ADJUDICATION - BING x SI IS BUILDABLE AS A NEW "LU MONTH" FORM
-------------------------------------------------------------------
The two existing same-element month shapes do not transfer to Si:

* pure-support unsatisfiable: Si branch fixed hidden stems are Bing
  (principal, same element), Wu (middle qi, i_generate / shishen output)
  and Geng (remaining qi, i_control / wealth). Every Si-month chart
  therefore contains non-support hidden relations, so the pure forms'
  all-positions-support-only condition can never hold (structural,
  same proof shape as the Yin case against Wu in the fire register).
* generating misnomer: for a Bing day master, Si's principal stem is
  Bing itself (same_element), NOT a generating (resource) stem, and Si
  is not a generating month for fire. Naming the form
  pure_generating_support (the Mu x Hai generating form) would misstate
  the month relation. The month is adjudicated as what the registered
  evidence says it is: the stem-listed LU (deer / salary) position of
  Bing, triple-attested (Sanming per-stem sentence, the section-closing
  summary block and Shenfeng's ten-stem lu table, plus the Ditiansui
  single-point statement). A new morphology ``bing-si-lu-...`` is
  therefore adjudicated, mirroring the F1 commanding form's nine
  conditions with the month condition replaced by the lu condition.

F3 satisfiability is registered honestly: an exhaustive scan of every
Bing-day-master x Si-month chart 1900-2100 (7,512 charts at shichen
granularity, conditions evaluated exactly as registered) finds exactly
ONE positive witness (1927-05-12, Wu hour, Ding Mao / Yi Si / Bing Wu /
Jia Wu). The form is satisfiable but its firing surface is a single
witness in two centuries; the bottleneck is the rooted-resource channel
(the reviewed wood root branches {Hai, Yin, Mao}: Yin harms Si, Hai
clashes Si, Mao can only enter as the year branch because a Bing day's
Mao hour stem is Gui (officer, non-support) and Bing Mao is not a legal
pillar). No condition is loosened to widen the surface (standing rule).

F4 ADJUDICATION - BING x YIN DESIGN ADJUDICATED, IMPLEMENTATION GATED
----------------------------------------------------------------------
Yin is a generating month (principal Jia generates fire, reviewed) and
the stem-listed CHANGSHENG (long-life) position of Bing (Sanming
per-stem sentence, corroborated by its converse death sentence, the
Shenfeng four-births statement and Sanming's own renyuan allocation).
The pure/generating shapes are again constructively unsatisfiable (Yin
fixed hidden stems contain Wu, an i_generate stem for fire). The form
is adjudicated on the Cong Wang anchor (which carries no month-
commanding requirement, same precedent as the generating lineage) with
a compound month condition: reviewed generating month AND month branch
is the day master's listed changsheng position. It is NOT described as
dangling / commanding: Yin is not the lu position of Bing and no
original sentence calls a Yin-month fire day master "in command".

IMPLEMENTATION GATE (registered, not elided): Yin is the one month for
which a registered, pilot-authorized Ren-branch siling segmentation
exists (Slice C: Wu [lichun, +7d) / Bing [+7d, +14d) / Jia [+14d, next
jie), convention ``siling-calculation-convention`` v1). The first
segment's commander Wu is, for a Bing day master, an OUTPUT (shishen)
stem: the "generating month" characterisation and the first-segment
commander pull in opposite directions for charts born in that segment.
Whether the strength form's month condition should be tightened by the
commander segment is the same decision as the siling month-expansion
package, which is a USER-LEVEL school adjudication. Two readings are
registered side by side (principal-only and segment-tightened); neither
may be implemented alone before that adjudication. The morphology
adjudication itself is NOT blocked by the gate. Satisfiability is not
the issue: the scan finds 39 positive witnesses across all three
segments (Wu 12 / Bing 8 / Jia 19), so the gate decides which subset a
future predicate may fire on - a substantive difference, quantified
here rather than asserted.

DING LINES: both Ding x Si and Ding x Yin stay blocked_by_conflict
under the registered Ding changsheng conflict
(``sanming-juan2.ding-changsheng``, sealed anchors 263-270 of the
juan2 collation register). Structural notes are registered: Si's
principal Bing is a peer (same element) stem for Ding - not Ding's lu
(Ding lu is Wu under both conflict readings) - so the lu-month anchor
is Bing-specific and never transfers to Ding; and Yin is exactly the
changsheng position claimed by branch B of the Ding conflict, so a
Ding x Yin form would sit directly on the unadjudicated reading.

EARTH ROOT INTERFACE: the standing gap from the S2 batch (no reviewed
earth root-position set anywhere: the sealed policy has no earth set
and no earth register exists) is audited condition by condition for
both forms. Conclusion: NO condition of either form consumes an earth
root fact - the visible layer is filtered to support-only before root
eligibility is consulted (visible Wu/Ji stems fail
visible_positions_support_only first), the day master's roots are fire
roots graded by the fire register, earth branches enter only as
carriers of already-registered fire light roots (Wei/Xu), and hidden
earth stems enter only as recorded facts under the hidden-layer
conventions. The gap therefore does NOT block F3/F4, unlike the S2
metal case where earth is the metal day master's resource and earth
visible-stem root eligibility was on the critical path. The pending
surface (any future form needing Wu/Ji visible-stem root eligibility,
or consuming hidden-stem root eligibility) is registered, not filled.

Quote policy: this register introduces NO new quotes. Every quote it
relies on is already registered in an earlier register and is
referenced by (register, quote_id); the sealed tests resolve the
references and re-verify the source slices byte-for-byte in the
assembled tree.
"""

F34_ADJUDICATION_REGISTER = {
    'id': 'bazi-fire-si-yin-morphology-adjudication-v1',
    'task': 'TJ-011.2',
    'kind': 'strength_morphology_adjudication_register',
    'source_snapshot': {
        'name': 'daizhigev20',
        'ditiansui_sha256':
            '6a875a3149abc35a41b1853e2bcca0b557acacb728b32d6ac01af6e11593ff26',
        'ditiansui_chars': 139538,
        'sanming_sha256':
            '00e2a7dbcd5d43ee6d51c6993acaa7fdad9ad46af64ba09f794bda2400b11b51',
        'sanming_chars': 461157,
    },
    'authority': (
        'Adjudication/design only. This register implements no '
        'predicate; both forms stay research_only with '
        'public_enabled=false and ai_enabled=false, and their '
        'Phase1/Phase2 rule registration stays '
        'pending_phase1_rule_registration (no rule ID is borrowed).'
    ),
    'supersedes_dispositions': {
        'register': 'bazi_fire_morphology',
        'entries': {
            'F3': 'not_adjudicated',
            'F4': 'deferred_not_adjudicated',
        },
        'note': (
            'The F1 register is a historical record and is not edited. '
            'This register carries the F3/F4 adjudications forward; '
            'where the two registers speak about F3/F4, this register '
            'is the current disposition.'
        ),
    },
}

# Registered quotes referenced (not duplicated) from earlier registers.
# The sealed tests resolve every reference and re-verify the source
# slice in the assembled tree.
QUOTE_REFERENCES = {
    # dt.congqiang_def (char 96605-, Ren commentary layer): the
    # commanding anchor - "day master also in command" plus the
    # no-wealth/no-officer clause.
    'dt.congqiang_def': {
        'register': 'bazi_fire_morphology',
        'role': 'F3 primary definition anchor (commanding clause)',
    },
    # dt.congwang_def (char 96521-, Ren commentary layer): support
    # mass without a commanding requirement.
    'dt.congwang_def': {
        'register': 'bazi_fire_morphology',
        'role': 'F3 co-anchor; F4 primary definition anchor',
    },
    # dt.congqiang_no_caiguan (char 96627-): "absolutely no trace of
    # wealth-star or officer-killer qi" - registered in the fire
    # register as its own quote.
    'dt.congqiang_no_caiguan': {
        'register': 'bazi_fire_morphology',
        'role': 'visible-layer denial anchor (both forms)',
    },
    # dt.root_heavy_light (char 39967-40222, original commentary):
    # changsheng / lu / wang are the heavy roots.
    'dt.root_heavy_light': {
        'register': 'bazi_fire_morphology',
        'role': 'root grading spine (both forms)',
    },
    # sm2.bing_lu (char 39568-39578, collation item sm2-10): per-stem
    # sentence "its lu is at Si".
    'sm2.bing_lu': {
        'register': 'bazi_sanming_juan2_collation',
        'role': 'F3 lu position, per-stem listed sentence',
    },
    # sm2.summary_bracket (char 43044-43074, collation item sm2-43):
    # the section-closing summary block (Bing at Si in the lu list;
    # the same bracket lists "Bing born at Yin" in the changsheng
    # list).
    'sm2.summary_bracket': {
        'register': 'bazi_sanming_juan2_collation',
        'role': 'F3 lu and F4 changsheng, summary corroboration',
    },
    # sm2.bing_sheng (char 39659-39668): per-stem sentence "Bing fire
    # is born at Yin".
    'sm2.bing_sheng': {
        'register': 'bazi_sanming_juan2_collation',
        'role': 'F4 changsheng position, per-stem listed sentence',
    },
    # sm2.bing_shengsi (char 39709-39719): converse sentence "Bing
    # fire is born at Yin and dies at You".
    'sm2.bing_shengsi': {
        'register': 'bazi_sanming_juan2_collation',
        'role': 'F4 changsheng corroboration (converse sentence)',
    },
    # sf.lubiao (Shenfeng ten-stem lu table statement): "Bing and Wu
    # lu at Si".
    'sf.lubiao': {
        'register': 'bazi_sanming_juan2_collation',
        'role': 'F3 lu position, cross-book table witness',
    },
    # sf.sisheng (Shenfeng four-births statement, char 129944-130179):
    # "the four births are the changsheng places of the five yang
    # stems".
    'sf.sisheng': {
        'register': 'bazi_sanming_juan2_collation',
        'role': 'F4 changsheng corroboration (framework statement)',
    },
    # dt.bing_lu_single (char 80850-80854): Ditiansui single-point
    # statement "Bing lu resides at Si".
    'dt.bing_lu_single': {
        'register': 'bazi_sanming_juan2_collation',
        'role': 'F3 lu position, Ditiansui single-point witness',
    },
    # sm2.renyuan_bing (char 47988-48008, Sanming Lun Renyuan Sishi):
    # "within Yin, Gen earth governs five days, Bing fire is
    # long-born five days, Jia wood twenty days" - same-book renyuan
    # corroboration. Note well: this is Sanming's own renyuan
    # allocation, a DIFFERENT statement from the Ren-branch siling
    # segments (7/7/remainder, dt.s024_yinyue) used by the Slice C
    # pilot. The two are never merged.
    'sm2.renyuan_bing': {
        'register': 'bazi_sanming_juan2_collation',
        'role': (
            'F4 changsheng corroboration (same-book renyuan side '
            'witness); also attests the Yin hidden Wu allocation '
            'behind the pure-shape unsatisfiability at Yin'
        ),
    },
    # dt.s024_yinyue (char 38056-38101, Ditiansui s024, original
    # commentary layer): the Yin-month segment sentence - first seven
    # days Wu earth governs, days 8-14 Bing fire, from day 15 Jia
    # wood. Registered in the Slice C siling matrix; the pilot
    # Variant bazi-siling-yin-pilot-v1 executes it under convention
    # siling-calculation-convention v1.
    'dt.s024_yinyue': {
        'register': 'bazi_siling_matrix',
        'role': (
            'F4 implementation-gate fact source: the registered '
            'Ren-branch Yin segments whose first-segment commander '
            '(Wu, an output stem for Bing) conflicts with the '
            'generating-month characterisation'
        ),
    },
}

# ---------------------------------------------------------------------
# F3: Bing x Si - the lu-month visible-support strong form.
# ---------------------------------------------------------------------

# Exclusion anchors follow the fire register's own registered
# structure exactly: officer/killer and wealth denials carry verbatim
# original-text anchors; the output (shishen) denial is honestly a
# scope construction (the definitions quantify over resource/peer
# mass and do not name visible output stems verbatim) - the same
# disclosure the F1 register makes.
_BING_SI_EXCLUSIONS = {
    'visible_officer': {
        'verdict': 'excluded',
        'anchors': ['dt.congwang_def', 'dt.congqiang_no_caiguan'],
    },
    'visible_killer': {
        'verdict': 'excluded',
        'anchors': ['dt.congwang_def', 'dt.congqiang_no_caiguan'],
    },
    'visible_wealth': {
        'verdict': 'excluded',
        'anchors': ['dt.congqiang_no_caiguan'],
    },
    'visible_output': {
        'verdict': 'excluded',
        'anchor_type': 'scope_construction',
        'anchors': ['dt.congwang_def', 'dt.congqiang_def'],
        'note': 'The definitions do not name visible output stems '
                'verbatim; the denial follows from the visible '
                'support-only construction over the definitions\' '
                'quantified resource/peer mass (same disclosure as '
                'the fire register).',
    },
    'hidden_officer_killer_wealth_output': {
        'verdict': 'recorded_not_adjudicated_outside_scope',
        'note': (
            'Hidden stems appear only as root-position facts and as '
            'the recorded facts recited by the Si hidden-layer '
            'convention instance. Si has NO hidden officer/killer '
            'stem; its hidden Wu (output) and Geng (wealth) are '
            'handled by that convention instance, never as a '
            'definition-layer adjudication.'
        ),
    },
}

FORM_BING_SI = {
    'form_id': 'bing-si-lu-commanding-visible-support-v1',
    'scope_candidate': 'lu_visible_support',
    'scope_status': (
        'adjudicated_design_only; the scope key is a candidate label '
        'for the future implementation batch and is not wired into '
        'any executable registry by this batch'
    ),
    'day_master': '丙',
    'month_branch': '巳',
    'direction': 'strong',
    'definition_anchors': [
        {'quote_ref': 'dt.congqiang_def', 'layer': '任氏曰',
         'role': 'primary: commanding clause (day master in command '
                 'in its lu month) + absolute exclusion clause'},
        {'quote_ref': 'dt.congwang_def', 'layer': '任氏曰',
         'role': 'co-anchor: support mass, no root in wealth/officer/'
                 'killer, principle qi flourishing'},
        {'quote_ref': 'dt.congqiang_no_caiguan', 'layer': '任氏曰',
         'role': 'co-anchor for the visible-layer exclusions'},
    ],
    'conditions': [
        {'key': 'fire_day_master_bing',
         'anchor_type': 'scope_construction',
         'statement': 'Day master is Bing (fire). Ding is excluded by '
                      'the registered changsheng conflict and by the '
                      'lu anchor being Bing-specific.'},
        {'key': 'reviewed_lu_command_month',
         'anchor_type': 'original_text',
         'anchors': ['sm2.bing_lu', 'sm2.summary_bracket', 'sf.lubiao',
                     'dt.bing_lu_single', 'dt.congqiang_def'],
         'statement': 'Month branch is Si; Si principal stem Bing is '
                      'reviewed same_element; AND Si is the day '
                      'master\'s stem-listed lu position (per-stem '
                      'listed, triple-attested across Sanming, '
                      'Shenfeng and Ditiansui). This is the '
                      'commanding clause of the primary anchor made '
                      'concrete for the lu month.'},
        {'key': 'visible_positions_support_only',
         'anchor_type': 'original_text',
         'anchors': ['dt.congqiang_def', 'dt.congwang_def'],
         'statement': 'Every visible stem (year/month/hour) relates '
                      'to the day master as generates_me or '
                      'same_element only; any visible officer, '
                      'killer, wealth or output stem falsifies the '
                      'definition outright.'},
        {'key': 'visible_resource_present',
         'anchor_type': 'original_text',
         'anchors': ['dt.congwang_def'],
         'statement': 'At least one visible stem is generates_me '
                      '(Jia/Yi resource).'},
        {'key': 'visible_peer_present',
         'anchor_type': 'original_text',
         'anchors': ['dt.congwang_def'],
         'statement': 'At least one visible stem is same_element '
                      '(Bing/Ding peer).'},
        {'key': 'effective_heavy_day_roots',
         'anchor_type': 'original_text',
         'anchors': ['dt.root_heavy_light'],
         'statement': 'The day master has at least one root and ALL '
                      'of its executed root facts are effective (no '
                      'registered type-source conflict, no branch '
                      'relation touching the root position), with at '
                      'least one heavy root in the heavy set '
                      '{Yin, Si, Wu} (changsheng / lu / diwang per '
                      'the fire register grading; the month branch '
                      'Si is itself a heavy lu root position).'},
        {'key': 'all_visible_have_reviewed_roots',
         'anchor_type': 'scope_construction',
         'statement': 'Every visible stem has at least one root '
                      'whose position branch is in the reviewed set '
                      'for its element: the sealed policy reviewed '
                      'sets for wood/metal/water, and the fire '
                      'register set {Yin, Si, Wu, Wei, Xu} for fire '
                      'stems (same construction as the commanding '
                      'form).'},
        {'key': 'no_unresolved_interactions',
         'anchor_type': 'scope_construction',
         'statement': 'No tracked interaction is unresolved: no stem '
                      'combination, no branch clash / harmony / harm '
                      '/ formed triple harmony anywhere in the chart.'},
        {'key': 'hidden_layer_convention_applied',
         'anchor_type': 'governance_convention',
         'convention': 'fire-morph.wu-geng-in-si-non-veto',
         'statement': 'The hidden-layer convention instance for Si '
                      'is recorded on the result (hidden Wu = output '
                      'and hidden Geng = wealth inside Si do not '
                      'veto; hidden stems outside root-position use '
                      'are not adjudicated).'},
    ],
    'exclusions': _BING_SI_EXCLUSIONS,
    'abstention_conditions': [
        'Any unresolved tracked interaction -> the form abstains '
        '(indeterminate), it never forces a verdict.',
        'Any day-root fact carrying the registered conflict '
        'bazi.concept.conflict_root_type_readings (a Xu root) -> the '
        'form abstains and the conflict is presented, per the '
        'conflict-presentation rules.',
    ],
    'sufficiency_statement': (
        'When all nine conditions hold, the registered sufficient '
        'conclusion is exactly: strength direction strong for a Bing '
        'day master in a Si month under this form. Nothing about '
        'pattern, useful god, fortune or any other day master / month '
        'is concluded.'
    ),
    'evidence_binding': 'pending_phase1_rule_registration',
    'research_only': True,
    'public_enabled': False,
    'ai_enabled': False,
}

# Why the existing shapes cannot be reused for Si (registered proofs).
F3_SHAPE_REJECTIONS = {
    'pure_support_shape': {
        'verdict': 'constructively_unsatisfiable',
        'proof': (
            'Si fixed hidden stems are Bing (principal, same '
            'element), Wu (middle qi, i_generate) and Geng (remaining '
            'qi, i_control). Every Si-month chart contains the Wu and '
            'Geng hidden relations, so the pure shapes\' '
            'all-positions-support-only condition is false for every '
            'Si chart by construction. No evidence gap is involved; '
            'the shape simply does not fit this branch.'
        ),
    },
    'pure_generating_support_shape': {
        'verdict': 'name_relation_mismatch',
        'proof': (
            'The generating lineage (Mu x Hai, Shui x Zi) requires '
            'the month principal stem to relate generates_me. Si '
            'principal stem is Bing itself: for a Bing day master the '
            'relation is same_element, and Si is not a generating '
            'month for fire. Carrying the generating name over would '
            'mislabel the month relation; the lu month gets its own '
            'form instead.'
        ),
    },
    'commanding_form_month_extension': {
        'verdict': 'rejected_scope_widening',
        'proof': (
            'Extending the F1 commanding form\'s month condition from '
            'Wu to {Wu, Si} would silently merge two different '
            'listed positions (diwang vs lu) and two different hidden '
            'compositions under one form id. The program rule is one '
            'form per adjudicated shape; F3 is registered separately.'
        ),
    },
}

F3_SATISFIABILITY = {
    'verdict': 'satisfiable_single_witness_in_scan_range',
    'scan': {
        'range': '1900-2100',
        'granularity': 'shichen (12 hour pillars per day)',
        'universe': 'every Bing day-master chart in a Si month',
        'chart_count': 7512,
        'positive_count': 1,
        'witness': '1927-05-12, Wu hour: Ding Mao / Yi Si / Bing Wu '
                   '/ Jia Wu',
        'method_note': (
            'Conditions evaluated exactly as registered in '
            'FORM_BING_SI (visible layer, reviewed root sets, fire '
            'register root grading, tracked interaction kinds as in '
            'the executed fact layer: stem combinations, branch '
            'clash / harmony / harm, formed triple harmonies).'
        ),
    },
    'bottleneck': (
        'The rooted-resource channel: a visible resource stem (Jia '
        'or Yi) must hold a reviewed root position, and the reviewed '
        'wood root branches are {Hai, Yin, Mao}. Yin harms the Si '
        'month branch and Hai clashes it, so both falsify '
        'no_unresolved_interactions whenever present; Mao survives '
        'only as the year branch (a Bing day\'s Mao hour stem is Gui, '
        'an officer, falsifying visible support; Bing Mao is not a '
        'legal pillar; the month branch is fixed Si). Within Mao '
        'years the visible-support filter leaves only Ding Mao / Yi '
        'Si, whose Si-month Bing days and support hours almost all '
        'fail on a named relation; the scan leaves exactly one '
        'witness. The narrowness is a property of the adjudicated '
        'condition set, not an evidence gap, and no condition is '
        'loosened to widen it.'
    ),
    'implementation_note': (
        'Per the S2 metal precedent, a narrow or even unrealizable '
        'firing surface does not bar implementation: a future '
        'predicate evaluates the registered conditions as-is and '
        'factor-level tests pin the logic. The single scan witness '
        'is registered as the Golden positive for the future batch.'
    ),
}

# The Si instance of the hidden-layer convention (the F1 register's
# Ji-in-Wu instance covers Wu only; this is a new instance of the same
# convention, scoped to the Si form).
F3_HIDDEN_CONVENTION_INSTANCE = {
    'id': 'fire-morph.wu-geng-in-si-non-veto',
    'anchor_type': 'governance_convention',
    'statement': (
        'For the lu-month form only: the Wu (output) and Geng '
        '(wealth) hidden inside the Si month branch do not veto the '
        'form. The commanding definition\'s exclusion clauses are '
        'adjudicated on the visible layer plus root facts; the '
        'hidden stems of the commanding branch enter the executed '
        'fact layer only as root-position facts.'
    ),
    'justification': (
        'If hidden Wu/Geng vetoed, the form would be unsatisfiable '
        'by construction (every Si branch carries them), while the '
        'definition anchors and the triple-attested lu position are '
        'fully registered - a disproportion the F1 batch already '
        'resolved the same way for Ji inside Wu. The convention is '
        'disclosed as governance, never dressed as original text.'
    ),
    'scope_limit': (
        'This instance says nothing about hidden-stem damage, '
        'combination or transformation; those remain unadjudicated '
        'outside this form, exactly as in F1.'
    ),
}

DING_SI_DISPOSITION = {
    'day_master': '丁',
    'month_branch': '巳',
    'verdict': 'blocked_by_conflict',
    'conflict_id': 'sanming-juan2.ding-changsheng',
    'structural_notes': [
        'Si principal stem Bing is a PEER (same element) stem for '
        'Ding, not a resource and not Ding\'s lu: Ding\'s lu is Wu '
        'under both readings of the registered conflict (Sanming '
        'per-stem sentence sm2.ding_lu). The lu-month anchor of F3 '
        'is Bing-specific and never transfers to Ding.',
        'Independently of the lu question, the whole Ding line is '
        'blocked by the unadjudicated changsheng conflict; no Ding '
        'form is designed or implemented.',
    ],
}

# ---------------------------------------------------------------------
# F4: Bing x Yin - the changsheng / generating-month visible-support
# strong form. Design adjudicated; implementation gated (see
# F4_IMPLEMENTATION_GATE).
# ---------------------------------------------------------------------

_BING_YIN_EXCLUSIONS = {
    'visible_officer': {
        'verdict': 'excluded',
        'anchors': ['dt.congwang_def', 'dt.congqiang_no_caiguan'],
    },
    'visible_killer': {
        'verdict': 'excluded',
        'anchors': ['dt.congwang_def', 'dt.congqiang_no_caiguan'],
    },
    'visible_wealth': {
        'verdict': 'excluded',
        'anchors': ['dt.congqiang_no_caiguan'],
    },
    'visible_output': {
        'verdict': 'excluded',
        'anchor_type': 'scope_construction',
        'anchors': ['dt.congwang_def'],
        'note': 'Same disclosure as the Si form: no verbatim output '
                'denial exists; the denial is the visible support-'
                'only construction over the Cong Wang quantification.',
    },
    'hidden_officer_killer_wealth_output': {
        'verdict': 'recorded_not_adjudicated_outside_scope',
        'note': (
            'Yin has NO hidden officer/killer/wealth stem; its '
            'hidden Wu (output) is handled by the Yin hidden-layer '
            'convention instance, and its hidden Bing (peer) is a '
            'support hidden stem recorded under the same convention, '
            'never counted as a root-effectiveness adjudication '
            'beyond the executed root facts.'
        ),
    },
}

FORM_BING_YIN = {
    'form_id': 'bing-yin-changsheng-visible-support-v1',
    'scope_candidate': 'changsheng_visible_support',
    'scope_status': (
        'adjudicated_design_only__implementation_gated; the scope '
        'key is a candidate label and is not wired into any '
        'executable registry by this batch'
    ),
    'day_master': '丙',
    'month_branch': '寅',
    'direction': 'strong',
    'definition_anchors': [
        {'quote_ref': 'dt.congwang_def', 'layer': '任氏曰',
         'role': 'primary: support mass with resource generation, no '
                 'root in wealth/officer/killer, principle qi '
                 'flourishing. This anchor carries NO commanding '
                 '(dangling) requirement - the same precedent as the '
                 'generating lineage (Mu x Hai).'},
        {'quote_ref': 'dt.congqiang_no_caiguan', 'layer': '任氏曰',
         'role': 'co-anchor for the visible-layer exclusions'},
    ],
    'commanding_claim': (
        'NONE. Yin is not the lu or diwang position of Bing, and no '
        'registered sentence calls a Yin-month fire day master "in '
        'command". The form is named for what is registered: a '
        'generating month whose branch is the day master\'s listed '
        'changsheng position.'
    ),
    'conditions': [
        {'key': 'fire_day_master_bing',
         'anchor_type': 'scope_construction',
         'statement': 'Day master is Bing (fire). Ding is excluded '
                      'by the registered changsheng conflict (and '
                      'Yin is one of its two claimed positions).'},
        {'key': 'reviewed_generating_changsheng_month',
         'anchor_type': 'original_text',
         'anchors': ['sm2.bing_sheng', 'sm2.bing_shengsi',
                     'sm2.summary_bracket', 'sf.sisheng',
                     'sm2.renyuan_bing', 'dt.congwang_def'],
         'statement': 'Month branch is Yin; Yin principal stem Jia '
                      'is reviewed generates_me (a generating month); '
                      'AND Yin is the day master\'s stem-listed '
                      'changsheng position (per-stem listed, with '
                      'converse-sentence, summary, Shenfeng and '
                      'renyuan corroboration).'},
        {'key': 'visible_positions_support_only',
         'anchor_type': 'original_text',
         'anchors': ['dt.congwang_def'],
         'statement': 'Every visible stem relates to the day master '
                      'as generates_me or same_element only.'},
        {'key': 'visible_resource_present',
         'anchor_type': 'original_text',
         'anchors': ['dt.congwang_def'],
         'statement': 'At least one visible stem is generates_me.'},
        {'key': 'visible_peer_present',
         'anchor_type': 'original_text',
         'anchors': ['dt.congwang_def'],
         'statement': 'At least one visible stem is same_element.'},
        {'key': 'effective_heavy_day_roots',
         'anchor_type': 'original_text',
         'anchors': ['dt.root_heavy_light'],
         'statement': 'At least one day-master root, all executed '
                      'root facts effective, at least one heavy root '
                      'in {Yin, Si, Wu}; the month branch Yin is '
                      'itself a heavy changsheng root position.'},
        {'key': 'all_visible_have_reviewed_roots',
         'anchor_type': 'scope_construction',
         'statement': 'Every visible stem has a root position in '
                      'the reviewed set for its element (same '
                      'construction as F1/F3).'},
        {'key': 'no_unresolved_interactions',
         'anchor_type': 'scope_construction',
         'statement': 'No unresolved tracked interaction anywhere '
                      'in the chart.'},
        {'key': 'hidden_layer_convention_applied',
         'anchor_type': 'governance_convention',
         'convention': 'fire-morph.wu-in-yin-non-veto',
         'statement': 'The hidden-layer convention instance for '
                      'Yin is recorded on the result (hidden Wu = '
                      'output inside Yin does not veto; hidden Bing '
                      '= peer is recorded as a support hidden stem, '
                      'not counted beyond root facts).'},
    ],
    'exclusions': _BING_YIN_EXCLUSIONS,
    'abstention_conditions': [
        'Any unresolved tracked interaction -> abstain.',
        'Any day-root fact carrying the registered conflict '
        'bazi.concept.conflict_root_type_readings (a Xu root) -> '
        'abstain with conflict presentation.',
        'Once implemented (after the gate clears), charts whose '
        'commander-segment status cannot be established at the '
        'precision the siling convention requires must abstain '
        'under that convention\'s fail-closed rules.',
    ],
    'sufficiency_statement': (
        'Subject to the implementation gate: when all nine '
        'conditions hold, the registered sufficient conclusion is '
        'exactly strength direction strong for a Bing day master in '
        'a Yin month under this form, under whichever month-'
        'condition reading the gate adjudication selects.'
    ),
    'evidence_binding': 'pending_phase1_rule_registration',
    'research_only': True,
    'public_enabled': False,
    'ai_enabled': False,
}

F4_SHAPE_REJECTIONS = {
    'pure_support_shape': {
        'verdict': 'constructively_unsatisfiable',
        'proof': (
            'Yin fixed hidden stems are Jia (principal, generates '
            'fire), Bing (middle qi, same element) and Wu (remaining '
            'qi, i_generate). Every Yin-month chart contains the Wu '
            'hidden relation (attested in the source itself by the '
            'renyuan allocation sm2.renyuan_bing), so '
            'all-positions-support-only is false for every Yin chart '
            'by construction.'
        ),
    },
    'pure_generating_support_shape': {
        'verdict': 'constructively_unsatisfiable',
        'proof': (
            'The generating form additionally requires every '
            'position to carry support only (same all-positions '
            'condition), which the hidden Wu falsifies identically.'
        ),
    },
    'pure_month_name': {
        'verdict': 'name_relation_mismatch',
        'proof': (
            'The pure lineage is named for same-element months '
            '(principal stem same_element). Yin principal Jia '
            'generates fire; it is not a same-element month, so the '
            'pure name cannot apply even before satisfiability.'
        ),
    },
}

F4_SATISFIABILITY = {
    'verdict': 'satisfiable_all_segments',
    'scan': {
        'range': '1900-2100',
        'granularity': 'shichen (12 hour pillars per day)',
        'universe': 'every Bing day-master chart in a Yin month',
        'chart_count': 7164,
        'positive_count': 39,
        'segment_distribution': {'戊': 12, '丙': 8, '甲': 19},
        'segment_method': (
            'Segments per the registered Ren-branch Yin segmentation '
            'under siling-calculation-convention v1 (t0 = provider '
            'lichun instant of the chart year, elapsed real time, '
            'left-closed right-open), computed with the same '
            'calendar provider family as the production chain.'
        ),
        'method_note': (
            'Conditions evaluated exactly as registered in '
            'FORM_BING_YIN under the principal-only reading of the '
            'month condition.'
        ),
    },
    'gate_relevance': (
        'Positive witnesses exist in ALL THREE commander segments. '
        'Under the segment-tightened reading only the Jia-segment '
        'witnesses (19 of 39) could fire; under the principal-only '
        'reading all 39 could. The gate therefore decides a real, '
        'quantified difference in the future predicate\'s firing '
        'surface - it is not a formality.'
    ),
}

F4_IMPLEMENTATION_GATE = {
    'status': 'implementation_blocked_pending_user_adjudication',
    'adjudication_blocked': False,
    'gate': (
        'Siling month expansion (Slice C decision package A/B) - a '
        'user-level school adjudication. The morphology adjudication '
        'in this register is complete and is NOT blocked; only '
        'implementation waits.'
    ),
    'reason': (
        'Yin is the only month with a registered, pilot-authorized '
        'Ren-branch commander segmentation (dt.s024_yinyue; pilot '
        'Variant bazi-siling-yin-pilot-v1 under convention '
        'siling-calculation-convention v1). Its first segment '
        'commander is Wu earth, which for a Bing day master is an '
        'output (i_generate) stem - the segment layer and the '
        'generating-month characterisation point in opposite '
        'directions for charts born in [lichun, +7d). Whether the '
        'strength form\'s month condition must be tightened by the '
        'commander segment is the same decision as the expansion '
        'package (which months, which branch, which convention), so '
        'it is decided once, by the user, not piecemeal by an '
        'implementation batch.'
    ),
    'readings': [
        {'id': 'principal_only',
         'statement': 'The month condition stands as registered '
                      '(generating month + listed changsheng '
                      'position); the commander segment is not '
                      'consulted. All 39 scan witnesses are in the '
                      'firing surface.',
         'status': 'registered_not_selected'},
        {'id': 'segment_tightened',
         'statement': 'The month condition additionally requires '
                      'the chart\'s commander segment (per '
                      'siling-calculation-convention v1) to be the '
                      'Jia segment [+14d, next jie). Only the 19 '
                      'Jia-segment witnesses are in the firing '
                      'surface; first- and second-segment charts '
                      'abstain under this form.',
         'status': 'registered_not_selected'},
    ],
    'rule': (
        'Neither reading may be implemented alone before the user '
        'adjudication. An implementation batch dispatched after the '
        'adjudication implements exactly the selected reading and '
        'registers the selection as a new adjudication event.'
    ),
}

F4_HIDDEN_CONVENTION_INSTANCE = {
    'id': 'fire-morph.wu-in-yin-non-veto',
    'anchor_type': 'governance_convention',
    'statement': (
        'For the changsheng/generating-month form only: the Wu '
        '(output) hidden inside the Yin month branch does not veto '
        'the form, and the Bing (peer) hidden inside Yin is recorded '
        'as a support hidden stem. Hidden stems enter the executed '
        'fact layer only as root-position facts.'
    ),
    'justification': (
        'Same structure as the F1/F3 instances: if hidden Wu '
        'vetoed, the form would be unsatisfiable by construction '
        'while its definition anchor and changsheng position are '
        'fully registered. Disclosed as governance convention.'
    ),
    'scope_limit': (
        'Nothing about hidden-stem damage, combination or '
        'transformation is adjudicated.'
    ),
}

DING_YIN_DISPOSITION = {
    'day_master': '丁',
    'month_branch': '寅',
    'verdict': 'blocked_by_conflict',
    'conflict_id': 'sanming-juan2.ding-changsheng',
    'structural_notes': [
        'Yin is exactly the changsheng position claimed by branch B '
        'of the registered Ding conflict (Ding changsheng at Yin, '
        'Shenfeng-based) against branch A (at You, Sanming-based). '
        'A Ding x Yin changsheng form would sit directly on the '
        'unadjudicated reading; designing it would pre-decide the '
        'conflict. No Ding form is designed or implemented.',
    ],
}

# ---------------------------------------------------------------------
# Earth root interface: condition-by-condition audit against the
# standing gap (no reviewed earth root-position set exists).
# ---------------------------------------------------------------------

EARTH_ROOT_INTERFACE = {
    'gap': (
        'Standing gap, registered by the S2 batch: no reviewed '
        'earth root-position set exists anywhere. The sealed policy '
        'reviewed_root_branches carries no earth set, and no earth '
        'root register has been adjudicated. Earth visible-stem root '
        'eligibility is therefore UNREGISTERED and must not be '
        'borrowed from any unreviewed root table.'
    ),
    'audit_conclusion': (
        'Neither F3 nor F4 consumes an earth root fact in any '
        'condition. The gap does not block either form.'
    ),
    'per_condition_audit': [
        {'condition': 'visible_positions_support_only',
         'earth_consumption': 'none_as_root',
         'note': 'A visible Wu/Ji stem falsifies this condition '
                 'directly (i_generate / controls relations are '
                 'computed from the stem itself). The filter runs '
                 'BEFORE root eligibility is consulted, so no earth '
                 'root fact is ever needed for a Wu/Ji visible stem: '
                 'it has already failed.'},
        {'condition': 'all_visible_have_reviewed_roots',
         'earth_consumption': 'none_reachable',
         'note': 'In any chart still alive at this condition, every '
                 'visible stem is Jia/Yi/Bing/Ding (support-only '
                 'survivors). Root eligibility is consulted only for '
                 'wood and fire stems, whose sets are registered '
                 '(policy wood set; fire register set). Earth stems '
                 'cannot occur here.'},
        {'condition': 'effective_heavy_day_roots',
         'earth_consumption': 'none',
         'note': 'The day master is Bing; its roots are fire roots '
                 'graded by the fire register (BING_ROOT_POSITIONS). '
                 'Earth branches (Chen/Xu/Chou/Wei) enter only as '
                 'carriers: Wei and Xu carry the registered fire '
                 'light roots (Ding in Wei/Xu) and are graded as '
                 'such; no earth-stem root fact is asserted.'},
        {'condition': 'hidden_layer_convention_applied',
         'earth_consumption': 'recorded_fact_only',
         'note': 'Hidden Wu (in Si and in Yin) and hidden Ji (in '
                 'Wu, for the F1 form) appear only as recorded facts '
                 'under the disclosed non-veto conventions. No root '
                 'eligibility is claimed for them.'},
        {'condition': 'month conditions (both forms)',
         'earth_consumption': 'none',
         'note': 'Month conditions consume month-branch identity '
                 'and registered per-stem position sentences (lu / '
                 'changsheng), never root facts.'},
    ],
    'contrast_with_s2_metal': (
        'In the S2 metal form the gap WAS blocking for positive '
        'coverage: earth is the metal day master\'s resource, so '
        'earth visible stems are support stems that SURVIVE the '
        'visible filter and then need root eligibility - one of the '
        'three channels in its unrealizability proof. For fire day '
        'masters earth is the output element: its visible stems '
        'fail the filter first, so the same gap is off the critical '
        'path. The difference is registered so the gap is neither '
        'over- nor under-generalised.'
    ),
    'pending_surface': [
        'Any future form whose day master takes earth as resource '
        'or peer (earth day masters; metal day masters beyond the '
        'registered S2 surface) needs Wu/Ji visible-stem root '
        'eligibility adjudicated first.',
        'Any future form consuming hidden-stem root eligibility '
        '(as opposed to position facts for the day master\'s own '
        'element) needs that eligibility adjudicated first.',
        'This batch registers the interface and fills none of it.',
    ],
}

F34_DISPOSITIONS = {
    'F3': {
        'subject': 'fire x Si month strong (lu month)',
        'disposition': 'adjudicated_buildable_new_form',
        'form_id': 'bing-si-lu-commanding-visible-support-v1',
        'implementation': 'not_in_this_batch',
    },
    'F4': {
        'subject': 'fire x Yin month strong (changsheng / '
                   'generating month)',
        'disposition': 'adjudicated_design_implementation_gated',
        'form_id': 'bing-yin-changsheng-visible-support-v1',
        'implementation': 'blocked_pending_siling_expansion_user_'
                           'adjudication',
    },
    'DING_SI': {
        'subject': 'ding x Si',
        'disposition': 'blocked_by_conflict',
        'conflict_id': 'sanming-juan2.ding-changsheng',
    },
    'DING_YIN': {
        'subject': 'ding x Yin',
        'disposition': 'blocked_by_conflict',
        'conflict_id': 'sanming-juan2.ding-changsheng',
    },
}

F34_ADJUDICATION_NOTES = [
    'Anchor types are labeled per condition and never upgraded: the '
    'two month conditions are original_text (per-stem listed '
    'positions, multiply attested); the rootedness and interaction '
    'conditions are scope_construction (they assemble executed facts, '
    'same as F1); the hidden-layer conditions are '
    'governance_convention and are disclosed as such.',
    'No framework_derived element is used in either form: unlike '
    'the F1 diwang substitution, the Si lu position and the Yin '
    'changsheng position both rest on per-stem listed sentences, so '
    'no derivation step needs disclosing.',
    'The F4 gate is a dependency disclosure, not a hedge: the design '
    'is complete (all nine conditions, exclusions, abstentions, '
    'satisfiability), and exactly one decision - which month-'
    'condition reading to implement - is reserved to the pending '
    'user adjudication because it is the same decision as the '
    'siling expansion package.',
    'Satisfiability scans are part of the adjudication evidence: F3 '
    'one witness in 7,512 charts; F4 thirty-nine witnesses in 7,164 '
    'charts across all three commander segments. Both scans '
    'evaluate the conditions exactly as registered.',
    'Ding x Si and Ding x Yin inherit the whole-line Ding block; '
    'their structural notes are registered so a future conflict '
    'adjudication sees the Si/Yin stakes explicitly.',
]

F34_LIMITATIONS = [
    'This batch implements no predicate: after it merges, the '
    'executed verdict for every F3/F4 chart is still indeterminate '
    '(no scope exists), and the sealed tests pin exactly that.',
    'F4 implementation additionally waits on the siling expansion '
    'user adjudication; F3 implementation is a separate future '
    'batch working from FORM_BING_SI and the Golden designs.',
    'Sealed Phase1/Phase2 registration for both forms stays '
    'pending_phase1_rule_registration; no rule ID is borrowed and '
    'sufficient_rule stays None in any future wiring until '
    'registration completes.',
    'The earth root gap stays open (see EARTH_ROOT_INTERFACE '
    'pending surface); this batch does not adjudicate any earth '
    'root position.',
    'The Ding changsheng conflict stays unadjudicated; nothing in '
    'this register prefers either branch.',
    'Golden designs are registered in '
    'tests/golden_tj0112_f34_si_yin.json (five F3 cases, two F4 '
    'cases, all real charts); they bind the future implementation '
    'batches, not the current engine.',
]
