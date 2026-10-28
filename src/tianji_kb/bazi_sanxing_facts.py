"""三刑组表结构事实层（TJ-012.3 实现批：SLICE_SPEC sanxing-branch-fact-v1）。

审定依据：``bazi_sanxing_fact_adjudication`` 登记册
（bazi-sanxing-fact-adjudication-v1，E0267）与审定文档
``docs/product/TJ0123_SANXING_FACT_ADJUDICATION.md``。本模块是该
SLICE_SPEC 的实现：独立结构事实函数 ``reviewed_branch_punishment_facts``
与既有 ``bazi_core.reviewed_branch_pair_relations`` 并列（同层、
kind 隔离），不改写 ``reviewed_relations`` / ``branch_relations``
的任何既有输出键。

事实模式（全部消费审定登记，不另存平行常量）：

- 无名三组（sanxing-group-1 子卯 / group-2 寅巳申 / group-3 丑戌未）
  的在场组态：completeness 只陈述集合在场（full/partial/single），
  不是「刑成立／刑不全」的裁定（审定 P6、FACT_PATTERN_DESIGN）。
  组名（无恩/恃势/无礼）在三命节内即有正文与《三车一览》互换
  冲突（018-B 登记 conflict、不裁定），事实层**永不输出组名**，
  输出 ``names`` 恒为 None；组名采用是用户级待裁定 P-D1
  （PENDING_ITEMS B2），本批不代决。
- 有向对：只报登记 DIRECTED_PAIR_TABLE 中 in_slice 的 7 条环边
  （等级 A 6 条＋等级 B 1 条卯→子，等级随事实逐行输出，不得与
  A 混同）；等级 C 的未→丑因三命可引明文缺位不入切片
  （blocked_by_evidence_gap，PENDING_ITEMS B1，证据工程而非
  流派裁定），组内其余 6 条有序对是方案非边——两者在任何输入
  下永不出现于输出（穷举与判别例钉住：丑未同盘组 partial 而
  有向对零条；寅申同盘只报申→寅）。
- 自刑集（辰午酉亥）：同支见于 ≥2 柱位才报，单柱出现不报；
  三见/四见仍报一条并列全柱位，不作程度区分。

边界（审定 FACT_PATTERN_DESIGN.boundary_rules）：刑事实与既有
clash/six_harmony/harm/triple_harmony/directional_meeting 事实
并存、互不抵消、互不优先（寅巳=害、巳申=六合、申寅=冲三条
等级 A 边各与一种既有对关系同对并存是常态）；柱位以
year/month/day/hour 原样报告，不赋权重；事实层不读旺衰/裁定层
任何输出，不因命盘其他条件抑制或放大事实（刑中有制等程度
命题被一般旺衰与制伏效力层阻断，PENDING_ITEMS B3，不属本层）。

fail-closed：每次调用先逐条核验审定登记的完整性（边表与组环
互洽、见证等级构成钉死 A×6＋B×1＋C×1 排除、每条 evidence_refs
可解析到 018-B 登记引文或 Canonical Section 钉定、非边划分
完备、自刑集与组员构成与登记一致）；任一不一致即
RuntimeError(registration_integrity_failure) 拒绝产出事实，
不降级猜测（镜像 siling pilot 的登记篡改 fail-closed 先例）。

注册与消费边界（审定 SLICE_SPEC.registration /
consumption_boundaries，本批重申）：evidence_binding 保持
pending_phase1_registration、sufficient_rule=None，不借用任何
既有 rule id；不建 Phase2 规则、不进 unresolved_interactions；
research_only=true、public_enabled=false、ai_enabled=false，
不接任何公开场景，公开投影对 branch_punishment_facts 键做
防御性整体剥离（public_projection）。概念
bazi.concept.conflict_three_punishments 全部字段逐字不变
（status unresolved、executable_policy
blocked_pending_school_resolution，审定 CONCEPT_LINKAGE）；
任氏分支不应用口径不变。事实层建成**不解锁任何
determination**：正官破格侧消费另经贵命整体判断转手
（PENDING_ITEMS B4 在案），TJ-012.3 保持阻塞。统一三刑教义
executable 是用户级待裁定 P-D2（B5），本批不呈请、不预判、
不代决。输出契约以白名单钉住：任何吉凶、成否、效价、程度、
评分、名目键的出现即测试失败（审定 P14 明文禁止由刑推吉凶）。
"""

from . import bazi_sanming_juan2_sanxing_collation as _cj
from . import bazi_sanxing_fact_adjudication as _adj
from .foundations import BRANCHES

SLICE_ID = 'sanxing-branch-fact-v1'
ADJUDICATION_REGISTER_ID = 'bazi-sanxing-fact-adjudication-v1'
PILLAR_NAMES = ('year', 'month', 'day', 'hour')

SLICE_REGISTRATION = {
    'slice_id': SLICE_ID,
    'task': 'TJ-012.3',
    'adjudication_register': ADJUDICATION_REGISTER_ID,
    'evidence_binding': 'pending_phase1_registration',
    'sufficient_rule': None,
    'research_only': True,
    'public_enabled': False,
    'ai_enabled': False,
    'phase2_rule': None,
    'scenario_wiring': None,
    'concept_id': 'bazi.concept.conflict_three_punishments',
    'concept_semantics_changed': False,
    'naming_status': 'conflict_unresolved_not_emitted',
}

SLICE_LIMITATIONS = (
    '本事实层只报三刑组员在场、有向环边与自刑重见三类结构事实，'
    '不报组名、不报成否、不报吉凶效价；completeness 是在场档，'
    '不得读作刑之成立与否。',
    '未刑丑（等级 C）因三命可引明文缺位不入切片：group-3 的环'
    '在事实层呈开口状态如实输出，不得以环的应然补边；解锁属'
    '018 线证据工程（PENDING_ITEMS B1）。',
    '事实层建成不解锁任何 determination：正官破格等教义性消费'
    '另经贵命整体判断、制伏效力等前置阻断（PENDING_ITEMS B4），'
    'TJ-012.3 保持阻塞。',
    '组名采用（P-D1）与统一三刑教义 executable（P-D2）为用户级'
    '待裁定，本模块不输出名目、不建教义规则。',
)


def _resolvable_refs():
    quote_ids = {q['id'] for q in _cj.COLLATION_QUOTES}
    section_ids = {s['section_id'] for s in _adj.SEALED_SECTION_PINS}
    return quote_ids | section_ids


def _registration_integrity_errors():
    """Cross-verify the adjudication register against itself.

    The fact function consumes the register; any tampering or drift
    between its parts (pair table vs group cycles vs non-edge
    partition vs attestation pins) must fail closed rather than
    silently change the emitted facts.
    """
    errors = []
    valid_refs = _resolvable_refs()
    groups = _adj.GROUP_TABLE['groups']
    group_members = {g['group_id']: list(g['members']) for g in groups}

    for g in groups:
        for ref in g['evidence_refs']:
            if ref not in valid_refs:
                errors.append(f"group {g['group_id']} ref {ref}")
    self_row = _adj.GROUP_TABLE['self_punishment']
    for ref in self_row['evidence_refs']:
        if ref not in valid_refs:
            errors.append(f"self_punishment ref {ref}")
    if list(self_row['members']) != ['辰', '午', '酉', '亥']:
        errors.append('self_punishment members drifted')

    # Cycle edges derived from the group table must equal the pair
    # table exactly (the pair table is the cycle, graded).
    cycle_edges = set()
    for g in groups:
        cyc = list(g['cycle'])
        if set(cyc) != set(g['members']):
            errors.append(f"cycle/members mismatch {g['group_id']}")
        for i, a in enumerate(cyc):
            cycle_edges.add((a, cyc[(i + 1) % len(cyc)]))
    pair_rows = _adj.DIRECTED_PAIR_TABLE
    pair_edges = {(p['actor'], p['target']) for p in pair_rows}
    if cycle_edges != pair_edges:
        errors.append('pair table != group cycles')

    for p in pair_rows:
        if group_members.get(p['group_id']) is None:
            errors.append(f"unknown group {p['group_id']}")
        else:
            members = group_members[p['group_id']]
            if p['actor'] not in members or p['target'] not in members:
                errors.append(
                    f"pair {p['actor']}->{p['target']} outside group")
        if not p['evidence_refs']:
            errors.append(f"pair {p['actor']}->{p['target']} no refs")
        for ref in p['evidence_refs']:
            if ref not in valid_refs:
                errors.append(
                    f"pair {p['actor']}->{p['target']} ref {ref}")

    # Attestation composition is adjudication-pinned: A x6 in slice,
    # B x1 (卯->子) in slice with its grade emitted, C x1 (未->丑)
    # excluded on an evidence gap. Any drift is a registration
    # change that needs its own adjudication batch, not a silent
    # behaviour change here.
    in_slice = [p for p in pair_rows if p['in_slice']]
    excluded = [p for p in pair_rows if not p['in_slice']]
    grades = [p['attestation_grade'] for p in in_slice]
    if len(in_slice) != 7 or grades.count('A') != 6 \
            or grades.count('B') != 1:
        errors.append('in-slice attestation composition drifted')
    b_rows = [p for p in in_slice if p['attestation_grade'] == 'B']
    if b_rows and (b_rows[0]['actor'], b_rows[0]['target']) != ('卯', '子'):
        errors.append('grade B edge is not 卯->子')
    if len(excluded) != 1 \
            or (excluded[0]['actor'], excluded[0]['target']) != ('未', '丑') \
            or excluded[0]['attestation_grade'] != 'C':
        errors.append('excluded edge is not 未->丑 grade C')

    # Non-edges partition the remaining intra-group ordered pairs:
    # they are scheme absences, never emitted, never gaps.
    non_edges = {tuple(x) for x in _adj.NON_EDGE_REGISTER['pairs']}
    all_ordered = set()
    for members in group_members.values():
        for a in members:
            for b in members:
                if a != b:
                    all_ordered.add((a, b))
    if pair_edges & non_edges or pair_edges | non_edges != all_ordered:
        errors.append('non-edge partition broken')

    spec = _adj.SLICE_SPEC
    if spec['id'] != SLICE_ID:
        errors.append('slice spec id drifted')
    reg = spec['registration']
    if reg['sufficient_rule'] is not None or not reg['research_only'] \
            or reg['public_enabled'] or reg['ai_enabled']:
        errors.append('slice registration flags drifted')
    return errors


def _ensure_registration():
    errors = _registration_integrity_errors()
    if errors:
        raise RuntimeError(
            'registration_integrity_failure: ' + '; '.join(errors))


def reviewed_branch_punishment_facts(branches):
    """Return reviewed 三刑 structural facts for four pillar branches.

    ``branches`` are the year/month/day/hour earthly branches of a
    real chart (production calendar chain output). Only structural
    presence facts are returned — group configurations (presence
    only), directed cycle pairs with attestation grades, and
    self-punishment repetitions. No group names, no verdict,
    valence, degree or score fields are ever emitted.
    """
    if not isinstance(branches, (list, tuple)) or len(branches) != 4:
        raise ValueError('Expected four earthly branches')
    if any(not isinstance(b, str) or len(b) != 1 or b not in BRANCHES
           for b in branches):
        raise ValueError('Invalid earthly branch')
    _ensure_registration()

    edge_by_pair = {}
    for row in _adj.DIRECTED_PAIR_TABLE:
        if row['in_slice']:
            edge_by_pair[(row['actor'], row['target'])] = row

    directed_pairs = []
    for i in range(4):
        for j in range(4):
            if i == j:
                continue
            row = edge_by_pair.get((branches[i], branches[j]))
            if row is None:
                continue
            directed_pairs.append({
                'actor_branch': branches[i],
                'target_branch': branches[j],
                'actor_pillar': PILLAR_NAMES[i],
                'target_pillar': PILLAR_NAMES[j],
                'group_id': row['group_id'],
                'attestation_grade': row['attestation_grade'],
                'evidence_refs': list(row['evidence_refs']),
            })

    branch_set = set(branches)
    group_configurations = []
    for group in _adj.GROUP_TABLE['groups']:
        members = list(group['members'])
        present = [m for m in members if m in branch_set]
        if not present:
            continue
        present_set = set(present)
        count = len(present)
        if count == len(members):
            completeness = 'full'
        elif count == 2:
            completeness = 'partial'
        else:
            completeness = 'single'
        group_configurations.append({
            'group_id': group['group_id'],
            'members': members,
            'present_branches': present,
            'present_pillars': [PILLAR_NAMES[k] for k in range(4)
                                if branches[k] in present_set],
            'present_member_count': count,
            'completeness': completeness,
        })

    self_row = _adj.GROUP_TABLE['self_punishment']
    self_punishments = []
    for branch in self_row['members']:
        pillars = [PILLAR_NAMES[k] for k in range(4)
                   if branches[k] == branch]
        if len(pillars) >= 2:
            self_punishments.append({
                'branch': branch,
                'pillars': pillars,
                'evidence_refs': list(self_row['evidence_refs']),
            })

    return {
        'directed_pairs': directed_pairs,
        'group_configurations': group_configurations,
        'self_punishments': self_punishments,
        'names': None,
    }
