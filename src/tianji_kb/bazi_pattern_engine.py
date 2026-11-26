"""Pattern engine (TJ-0424): one evaluator per pattern, research_only.

Assembles the already-reviewed pattern material into a single per-pattern
assessment. It invents no new pattern rule: every state is either

- ``established`` -- only through the Ren-branch 寅月 true-pattern block
  (``ren_yin_true_pattern``, bazi.phase2.ren_yin_true_pattern, validated,
  Golden 15), the single reviewed determination in the sealed tree;
- ``candidate`` -- a reviewed structural observation, now carrying the
  per-pattern condition facts registered in the public Yuanhai
  section registrations (``bazi_yuanhai_{qisha,cai,shishang,
  zhengguan,yin,luren,cong}``): a condition's *presence* is computed
  from the pillars, its *efficacy* is never judged (every operative
  quote in those registrations routes through an unbuilt gate --
  strength, control/retention efficacy, combination, or the pattern's
  own establishment -- and each registration concludes determination
  is still None). A candidate therefore reports which classical
  conditions are in fact present and names the exact gate that blocks
  any further verdict;
- ``conflict`` -- two reviewed branches disagree and neither is adjudicated
  (正官 + 时七杀 s055 caution; 杂气原注 vs 三命 vs 子平真诠 Ch16,
  pattern_zaqi, validated Golden 6);
- ``not_judgeable`` -- no reviewed basis for this pattern on this chart.

``broken`` is never emitted: no per-pattern 破格 condition is reviewed
anywhere in the sealed tree or in the Yuanhai registrations (each
candidate condition's breaking efficacy -- 财旺破印, 伤官见官,
制伏太过, 官杀去留 -- is expressly unadjudicated). Every evaluator
names its own broken-gap explicitly instead of emitting ``broken``.

Classical rules and any modern engineering judgement are kept apart:
the only modern-engineering element is the narrow 从格候选屏 in
``evaluate_special``, which reuses the batch-1 strength engine's
screen definition (no roots, no visible support, >= 2 visible
relations all controls_me / i_generate) and is labelled
``model_kind="modern_engineering"``; it is a screen hit, never an
establishment. Strength is otherwise consumed only through
``bazi_strength.factors()`` and only as listed factors (roots,
visibility, month command); its ``overall_strength`` is always None
and is reported as unresolved wherever it would matter.

Governance: research_only=True, public=False, ai=False throughout.
Nothing here is a public API field and nothing is wired into
``public_projection``. 戊×巳 / 己×午 are always not_judgeable
(TJ-011.2: earth day-master pattern formation is unbuildable).
"""

from .bazi_core import hidden_stems, reviewed_relations, ten_god
from .bazi_pattern import (
    EXPOSABLE_PILLARS,
    LUREN_ROUTE_VARIANT,
    LU_BRANCH,
    MISCELLANEOUS_BRANCHES,
    PATTERN_VARIANT,
    REN_BRANCH,
    REN_YIN_TRUE_VARIANT,
    YUANHAI_RESOURCE_MONTHS,
    candidates as _pattern_candidates,
    luren_route_lookup,
    month_pattern_route,
    month_pattern_zaqi,
    ren_yin_true_pattern,
    zaqi_selection_lookup,
)
from .bazi_strength import factors as _strength_factors
from .foundations import BRANCHES, STEMS

PATTERN_ENGINE_VARIANT = 'bazi-pattern-engine-v2'

# pattern_key -> (Chinese pattern name, ten god or None)
PATTERNS = (
    ('zhengguan', '正官', '正官'),
    ('qisha', '七杀', '七杀'),
    ('zhengyin', '正印', '正印'),
    ('pianyin', '偏印', '偏印'),
    ('zhengcai', '正财', '正财'),
    ('piancai', '偏财', '偏财'),
    ('shishen', '食神', '食神'),
    ('shangguan', '伤官', '伤官'),
    ('jianlu', '建禄', None),
    ('yangren', '阳刃', None),
    ('zaqi', '杂气', None),
    ('special', '特殊格局', None),
)
PATTERN_NAMES = {key: name for key, name, _ in PATTERNS}
TEN_GOD_PATTERNS = {god: key for key, _, god in PATTERNS if god is not None}
# Ren D-1 can also mechanically establish 比肩格 / 劫财格 (commander stem
# identical to the day master); those names are outside the reviewed
# public eight-name whitelist and are reported here as research-only
# extras, never as one of the twelve patterns above.
EXTRA_TEN_GOD_PATTERNS = {'比肩': 'bijian', '劫财': 'jiecai'}
EXTRA_PATTERN_NAMES = {'bijian': '比肩', 'jiecai': '劫财'}

# Earth day-master pattern formation is unbuildable (TJ-011.2).
EARTH_UNJUDGEABLE = (('戊', '巳'), ('己', '午'))

STATES = ('candidate', 'established', 'broken', 'conflict', 'not_judgeable')


PILLAR_CN = {'year': '年', 'month': '月', 'day': '日', 'hour': '时'}

# 《论七杀》七日生主杀列举（yh.qs_seven_days）：日柱有限列举，
# 非成格 / 破格条件。
SEVEN_KILLING_DAYS = ('甲申', '乙酉', '丁丑', '戊寅', '己卯', '辛未', '癸未')

# 《论日刃》日刃三柱（yh.rr_same_method）：日刃与阳刃同法。
DAY_REN_PILLARS = ('戊午', '丙午', '壬子')


def _ev(evidence_id, detail):
    return {'id': evidence_id, 'detail': detail}


def _result(ctx, pattern_key, state, evidence, limitations, *, rule_ids=()):
    name = PATTERN_NAMES.get(pattern_key) or EXTRA_PATTERN_NAMES[pattern_key]
    return {
        'pattern': name,
        'pattern_key': pattern_key,
        'state': state,
        'evidence': list(evidence),
        'limitations': list(limitations),
        'rule_ids': list(rule_ids),
        'research_only': True,
        'public': False,
        'ai': False,
        'variant': PATTERN_ENGINE_VARIANT,
        'day_stem': ctx.day_stem,
        'month_branch': ctx.month_branch,
    }


class _Context:
    """Facts shared by every per-pattern evaluator."""

    def __init__(self, chart, *, official=None, resource=None, route=None,
                 zaqi=None, ren_yin=None):
        pillars = chart['pillars']
        if len(pillars) != 4:
            raise ValueError('Pattern engine requires four pillars')
        self.day_stem = chart['day_master']['stem']
        if self.day_stem not in STEMS:
            raise ValueError('Pattern engine requires a valid day stem')
        self.stems = [p['stem']['value'] for p in pillars]
        self.branches = [p['branch']['value'] for p in pillars]
        if any(b not in BRANCHES for b in self.branches):
            raise ValueError('Pattern engine requires valid branches')
        self.month_branch = self.branches[1]
        self.pillar_names = ('year', 'month', 'day', 'hour')
        # Visible ten gods per pillar (day pillar is the day-master
        # reference itself, never an exposed actor).
        self.visible_ten_gods = {
            name: ten_god(self.day_stem, stem)
            for name, stem in zip(self.pillar_names, self.stems)
            if name != 'day'
        }
        self.visible_stems = {
            name: stem for name, stem in zip(self.pillar_names, self.stems)
            if name != 'day'
        }
        # Month hidden stems with their ten gods (executed fact order).
        self.month_hidden = hidden_stems(self.month_branch, self.day_stem)
        self.month_hidden_by_god = {}
        for row in self.month_hidden:
            self.month_hidden_by_god.setdefault(row['ten_god'], []).append(row)
        # Every pillar's hidden stems (day branch included): a god's
        # positions across the whole chart, visible and hidden.
        self.all_hidden = []
        for i, name in enumerate(self.pillar_names):
            for row in hidden_stems(self.branches[i], self.day_stem):
                self.all_hidden.append({'pillar': name,
                                        'branch': self.branches[i],
                                        'stem': row['stem'],
                                        'ten_god': row['ten_god']})
        # Reviewed stem five-combination facts among the four stems.
        self.five_combinations = reviewed_relations(
            self.stems, self.branches)['stem_five_combinations']
        # Strength factors only: no strength verdict is consumed.
        self.strength_factors = _strength_factors(pillars, self.day_stem)
        # Optional precomputed reviewed blocks (from a trace); when a
        # block is absent the evaluator falls back to the same structural
        # facts computed directly from the pillars.
        self.official = official
        self.resource = resource
        self.route = route
        self.zaqi = zaqi
        self.ren_yin = ren_yin
        self.earth_gate = (self.day_stem, self.month_branch) in EARTH_UNJUDGEABLE

    def god_positions(self, god):
        """All positions of ``god``: visible stems (year/month/hour) and
        hidden stems of every branch (day branch included). The day stem
        itself is the reference and never a position."""
        out = []
        for name in ('year', 'month', 'hour'):
            if self.visible_ten_gods[name] == god:
                out.append({'pillar': name, 'kind': 'visible',
                            'stem': self.visible_stems[name]})
        for row in self.all_hidden:
            if row['ten_god'] == god:
                out.append({'pillar': row['pillar'], 'kind': 'hidden',
                            'stem': row['stem']})
        return out

    def god_position_text(self, positions):
        return '、'.join('%s%s%s' % (PILLAR_CN[p['pillar']],
                                     '干' if p['kind'] == 'visible' else '支藏',
                                     p['stem'])
                         for p in positions)

    def has_any_god(self, god):
        return bool(self.god_positions(god))

    def structural_roots(self):
        """Same-element hidden-stem root *candidates* (structural only):
        the Yuanhai 从格 registrations stress that root *grade*
        (light root / tomb root / pending) is unadjudicated, so these
        are presence facts, never an effective-root verdict."""
        return self.strength_factors['root_candidates']['positions']

    def visible_relation_kinds(self):
        return [row['relation'] for row in
                self.strength_factors['support_relations']['visible_positions']]

    def exposed_pillars(self, stem):
        """Year/month/hour pillars exposing ``stem`` (day stem excluded)."""
        return [name for name in EXPOSABLE_PILLARS
                if self.visible_stems[name] == stem]

    def month_hidden_god(self, god):
        rows = self.month_hidden_by_god.get(god, [])
        return rows[0] if rows else None

    def ren_yin_pattern(self):
        """(pattern_name, commander_stem, visible_pillars) if D-1 established."""
        block = self.ren_yin
        if not isinstance(block, dict):
            return None
        if block.get('status') != 'determined':
            return None
        inner = block.get('determination') or {}
        if inner.get('true_false') != 'true':
            return None
        pattern = inner.get('pattern')
        if not pattern:
            return None
        commander = block.get('commander') or {}
        return (pattern, commander.get('stem'),
                list(commander.get('visible_pillars') or []))

    def ren_yin_commander_not_visible(self):
        """Commander ten god when D-1 determined commander_not_visible."""
        block = self.ren_yin
        if not isinstance(block, dict):
            return None
        if block.get('status') != 'determined':
            return None
        inner = block.get('determination') or {}
        if inner.get('true_false') != 'commander_not_visible':
            return None
        commander = block.get('commander') or {}
        return commander.get('ten_god')

    def route_value(self):
        if isinstance(self.route, dict):
            return self.route.get('route')
        return luren_route_lookup(self.day_stem, self.month_branch)['route']

    def earth_result(self, pattern_key):
        return _result(
            self, pattern_key, 'not_judgeable',
            [_ev('tj0112_earth_unbuildable',
                 '戊×巳 / 己×午土日主成格不可建（TJ-011.2）：'
                 '日干 %s、月支 %s 一律不作格局裁定。'
                 % (self.day_stem, self.month_branch))],
            ['TJ-011.2 土日主成格未建：不输出候选、成立、破格或冲突。'],
            rule_ids=[])


def _ten_god_evaluator(ctx, pattern_key, god, *, candidate_rule_id,
                       candidate_rule_note, no_rule_note, conditions=(),
                       broken_gap=''):
    """Shared logic for the eight ten-god patterns (正官/七杀/正印/偏印/
    正财/偏财/食神/伤官).

    ``conditions`` are computed presence facts from the pattern's
    registered section (in fact, efficacy unadjudicated); they are
    attached to established / candidate outcomes. ``broken_gap`` names
    the exact unadjudicated breaking condition for this pattern and is
    recorded as a limitation on every outcome -- ``broken`` is never
    emitted on its strength.
    """
    if ctx.earth_gate:
        return ctx.earth_result(pattern_key)
    limitations_extra = [broken_gap] if broken_gap else []
    established = ctx.ren_yin_pattern()
    if established is not None and established[0] == god + '格':
        return _result(
            ctx, pattern_key, 'established',
            [_ev('ren_yin_true_pattern',
                 '任氏分支寅月真格成立：司令 %s（%s）透于 %s。'
                 % (established[1], god, '、'.join(established[2]) or '无')),
             _ev('ren_yin_rule',
                 '依据 bazi.phase2.ren_yin_true_pattern（validated，'
                 'Golden 15；s053 原注定义句 + s054 任氏曰程序句）。')]
            + list(conditions),
            ['破格 / 成败 / 清浊 / 用神恒未审（八格章无逐格破格条件句）；'
             '只裁定寅月任氏分支真格成立，不外推其他月份与流派。']
            + limitations_extra,
            rule_ids=['bazi.phase2.ren_yin_true_pattern'])
    row = ctx.month_hidden_god(god)
    if row is None:
        evidence = [_ev('no_month_hidden_god',
                        '月支 %s 藏干中无 %s；散见于他柱的 %s 不导入月令取格。'
                        % (ctx.month_branch, god, god))]
        if ctx.ren_yin_commander_not_visible() == god:
            evidence.append(_ev(
                'ren_yin_commander_not_visible',
                '寅月司令为 %s 但不透：结论止于“无真格”，永不标“假格”。'
                % god))
        scattered = ctx.god_positions(god)
        if scattered:
            evidence.append(_ev(
                'scattered_god_positions',
                '散见 %s 位置（%d 处）：%s——只记事实，不导入月令取格。'
                % (god, len(scattered),
                   ctx.god_position_text(scattered))))
        return _result(ctx, pattern_key, 'not_judgeable', evidence,
                       ['无月藏 %s 观察：不等于该盘无此格，只说明本引擎无依据。' % god]
                       + limitations_extra,
                       rule_ids=[])
    exposed = ctx.exposed_pillars(row['stem'])
    evidence = [
        _ev('month_hidden_god',
            '月支 %s 藏 %s（%s），透于：%s。'
            % (ctx.month_branch, row['stem'], god,
               '、'.join(exposed) if exposed else '未透')),
    ]
    if candidate_rule_id:
        evidence.append(_ev(candidate_rule_id, candidate_rule_note))
    else:
        evidence.append(_ev('month_hidden_observation', candidate_rule_note))
    if ctx.ren_yin_commander_not_visible() == god:
        evidence.append(_ev(
            'ren_yin_commander_not_visible',
            '寅月司令为 %s 但不透：结论止于“无真格”，永不标“假格”。' % god))
    evidence.extend(conditions)
    limitations = [
        '只作候选观察：分日司令未裁定（寅月以外）、旺衰未裁定、'
        '真假 / 成败 / 清浊 / 用神未裁定。',
        no_rule_note,
    ] + limitations_extra
    return _result(ctx, pattern_key, 'candidate', evidence, limitations,
                   rule_ids=[candidate_rule_id] if candidate_rule_id else [])


def _qisha_condition_evidence(ctx):
    """七杀条件事实（《渊海》〈论七杀〉yh.qs_* / 〈论官星太过〉yh.gt_*）：
    在场事实可算，效力（身旺 / 制伏 / 合杀 / 财旺）皆未裁定。"""
    out = []
    positions = ctx.god_positions('七杀')
    if positions:
        out.append(_ev(
            'qisha_positions',
            '七杀位置（%d 处）：%s。'
            % (len(positions), ctx.god_position_text(positions))))
        pillars = {p['pillar'] for p in positions}
        if 'day' in pillars:
            out.append(_ev(
                'qisha_day_position',
                '日柱见七杀（yh.qs_day_killing：只一位、年时再见杀多为祸，'
                '却要制伏之乡、又要身旺有制伏为权；位置观察，效力未裁定）。'))
        if 'hour' in pillars:
            out.append(_ev(
                'qisha_hour_position',
                '时柱见七杀（yh.qs_hour_killing：要本身旺、三处有制伏为福；'
                'yh.qs_hour_no_fear：时上七杀却不怕阳刃、不畏冲；'
                '位置观察，效力未裁定）。'))
        if len(positions) >= 2:
            out.append(_ev(
                'qisha_many_positions',
                '杀多事实（%d 处）：月见之重、时见之轻为位置权重观察'
                '（yh.qs_many_killings_weight），非破格结论。' % len(positions)))
    control = ctx.god_positions('食神') + ctx.god_positions('伤官')
    if control:
        out.append(_ev(
            'qisha_control_present',
            '制伏在场：%s（食神 / 伤官；yh.qs_control_present 元有制伏、'
            'yh.qs_jia_example_control 甲以庚为七杀、喜丙丁制之；'
            '制伏构成与效力未裁定）。'
            % ctx.god_position_text(control)))
    else:
        out.append(_ev(
            'qisha_control_absent',
            '四柱无食神 / 伤官制伏在场（yh.qs_control_present 元无制伏句；'
            '无制伏为事实，非破格结论）。'))
    for pair in ctx.five_combinations:
        stems = pair['stems']
        killing = [s for s in stems if ten_god(ctx.day_stem, s) == '七杀']
        if killing:
            out.append(_ev(
                'qisha_combined_killing',
                '合杀在场：%s 五合，合及七杀 %s（yh.qs_jia_example_control '
                '乙合之、谓之贪合忘杀；合化效力未裁定）。'
                % ('、'.join(stems), '、'.join(killing))))
    wealth = ctx.god_positions('正财') + ctx.god_positions('偏财')
    if wealth:
        out.append(_ev(
            'qisha_wealth_feeds',
            '财星在场：%s（财能生杀；yh.qs_blade_and_wealth 忌财旺句；'
            '财旺为强度判断，未阈值化）。'
            % ctx.god_position_text(wealth)))
    ren = REN_BRANCH.get(ctx.day_stem)
    if ren is not None and (ctx.month_branch == ren or ctx.branches[2] == ren):
        out.append(_ev(
            'qisha_blade_present',
            '阳刃在场（刃在 %s，见于%s；yh.qs_blade_and_wealth 更有阳刃句；'
            '与日七杀最怕冲与阳刃、时七杀不怕阳刃构成位置对照，'
            '刃的效力未裁定）。'
            % (ren, '月支' if ctx.month_branch == ren else '日支')))
    day_ganzhi = ctx.stems[2] + ctx.branches[2]
    if day_ganzhi in SEVEN_KILLING_DAYS:
        out.append(_ev(
            'qisha_seven_days',
            '日柱 %s 在七日生主杀列举内（yh.qs_seven_days 甲申、乙酉、'
            '丁丑、戊寅、己卯、辛未、癸未；列举与性情断语，'
            '非成格 / 破格条件）。' % day_ganzhi))
    return out


def _wealth_condition_evidence(ctx, god):
    """财格条件事实（《渊海》〈论正财〉yh.zc_* / 〈论偏财〉yh.pc_* /
    〈论劫财〉yh.jc_*）：在场事实可算，比劫分夺 / 财多化官 /
    财生官的效力皆未裁定。"""
    out = []
    positions = ctx.god_positions(god)
    if positions:
        out.append(_ev(
            'wealth_positions',
            '%s位置（%d 处）：%s。'
            % (god, len(positions), ctx.god_position_text(positions))))
        if len(positions) >= 2:
            out.append(_ev(
                'wealth_many_positions',
                '财多事实（%d 处）：yh.zc_many_transform_officer 若财多则'
                '自家日本有力、可以胜任、当化作官——身健与化官效力未裁定，'
                '只记数量事实。' % len(positions)))
    robbery = ctx.god_positions('比肩') + ctx.god_positions('劫财')
    if robbery:
        out.append(_ev(
            'wealth_robbery_present',
            '比劫在场：%s（yh.pc_definition 只恐兄弟姊妹有夺之、'
            'yh.zc_wealth_strife_root 财者起争之端也；分夺效力未裁定，'
            '不判夺财破格）。' % ctx.god_position_text(robbery)))
    officer = ctx.god_positions('正官')
    if officer:
        out.append(_ev(
            'wealth_officer_present',
            '官星在场：%s（yh.zc_wealth_generates_officer 财多生官、'
            '要须身健；yh.pc_wealth_generates_officer 财盛自生官；'
            '生官链效力未裁定）。' % ctx.god_position_text(officer)))
    food = ctx.god_positions('食神') + ctx.god_positions('伤官')
    if food:
        out.append(_ev(
            'wealth_food_generates',
            '食伤在场：%s（yh.ss_definition 食神者、生我财神之谓也；'
            '食伤生财链效力未裁定）。' % ctx.god_position_text(food)))
    if god == '正财' and ctx.has_any_god('伤官'):
        out.append(_ev(
            'wealth_shangguan_sees_wealth',
            '伤官在场：%s（yh.zc_shangguan_jiancai 伤官见财格、忌见官星、'
            '只喜见财；格名提及，成立未裁定）。'
            % ctx.god_position_text(ctx.god_positions('伤官'))))
    if god == '偏财':
        exposed = ctx.exposed_pillars(ctx.month_hidden_god('偏财')['stem']) \
            if ctx.month_hidden_god('偏财') else []
        out.append(_ev(
            'piancai_exposure',
            '偏财%s（yh.pc_exposure 偏财好出、亦不惧藏，惟怕有以分夺）。'
            % ('透于 ' + '、'.join(exposed) if exposed else '藏于月支未透')))
    return out


def _food_condition_evidence(ctx, god):
    """食伤条件事实（《渊海》〈论伤官〉yh.sw_* / 〈论食神〉yh.ss_* /
    〈论倒食〉yh.ds_*）：在场事实可算，伤尽程度 / 伤官见官 /
    倒食夺食的效力皆未裁定。"""
    out = []
    positions = ctx.god_positions(god)
    if positions:
        out.append(_ev(
            '%s_positions' % ('shishen' if god == '食神' else 'shangguan'),
            '%s位置（%d 处）：%s。'
            % (god, len(positions), ctx.god_position_text(positions))))
    if god == '食神':
        wealth = ctx.god_positions('正财') + ctx.god_positions('偏财')
        if wealth:
            out.append(_ev(
                'shishen_generates_wealth',
                '财星在场：%s（yh.ss_definition 食神者、生我财神之谓也；'
                '生财链效力未裁定）。' % ctx.god_position_text(wealth)))
        seal = ctx.god_positions('偏印')
        if seal:
            out.append(_ev(
                'shishen_seized_by_seal',
                '偏印在场：%s（yh.ds_mechanism 倒食：甲见壬之类、壬剋丙火、'
                '食神不能生财；倒食夺食效力未裁定，不判破格）。'
                % ctx.god_position_text(seal)))
    else:
        officer = ctx.god_positions('正官') + ctx.god_positions('七杀')
        if officer:
            out.append(_ev(
                'shangguan_sees_officer',
                '官杀在场：%s（yh.sw_pattern_no_officer 用伤官格者、支干岁运'
                '都要不见官星、如见官星谓之伤官见官；见官效力未裁定，'
                '不判破格）。' % ctx.god_position_text(officer)))
        else:
            out.append(_ev(
                'shangguan_exhausted_observation',
                '四柱无官杀在场：伤尽结构观察（yh.sw_exhaust_core 伤官务要'
                '伤尽；伤尽为程度词、无已裁定程度标尺，仍只作候选观察，'
                '不作伤尽成立）。'))
        wealth = ctx.god_positions('正财') + ctx.god_positions('偏财')
        if wealth:
            out.append(_ev(
                'shangguan_meets_wealth',
                '财星在场：%s（yh.sw_meet_wealth_wonderful 如遇伤官者、'
                '须见其财为妙、是财能生官也；评价以伤官格成立为前提，'
                '成立未裁定）。' % ctx.god_position_text(wealth)))
    return out


def _official_condition_evidence(ctx):
    """正官条件事实（《渊海》〈正官论〉yh.zg_* / 〈论官杀混杂要制伏〉
    yh.gs_*）：官多与他柱杀只记事实；去留条件事实在场不等于去留
    已行。时柱七杀的混杂 conflict 由 evaluate_zhengguan 另行判定。"""
    out = []
    officials = ctx.god_positions('正官')
    if len(officials) >= 2:
        out.append(_ev(
            'official_many_positions',
            '官星多事实（%d 处）：%s（yh.zg_duo 正官或多、反不为福；'
            'yh.gt_clear 官星多则杂、务要除而清之；多寡只记事实，'
            '杂 / 去留效力未裁定）。'
            % (len(officials), ctx.god_position_text(officials))))
    killings = ctx.god_positions('七杀')
    other = [p for p in killings if p['pillar'] != 'hour']
    if other:
        out.append(_ev(
            'official_other_pillar_killing',
            '七杀在他柱：%s（s055 / yh.zg_jia_mixed 只论时干支逢杀乃官杀'
            '混杂；他柱杀只记共现事实，不定混杂、不定去留）。'
            % ctx.god_position_text(other)))
    control = ctx.god_positions('食神') + ctx.god_positions('伤官')
    if control:
        out.append(_ev(
            'guansha_retention_condition',
            '去留条件事实在场：%s（食神 / 伤官；yh.gs_example_zhifu '
            '若有金或庚申、则混杂为杀、要行火乡制伏、则发福也；'
            'yh.gt_clear 除而清之；去何星、清至何程度均未裁定）。'
            % ctx.god_position_text(control)))
    return out


def _resource_condition_evidence(ctx, god):
    """印绶条件事实（《渊海》〈论印綬〉yh.yn_* / yh.ys_* / 〈论倒食〉
    yh.ds_*）：财破印 / 官印相生 / 倒食夺食只记方向与位置，
    效力一律未裁定。"""
    out = []
    positions = ctx.god_positions(god)
    if positions:
        out.append(_ev(
            'resource_positions',
            '%s位置（%d 处）：%s。'
            % (god, len(positions), ctx.god_position_text(positions))))
    wealth = ctx.god_positions('正财') + ctx.god_positions('偏财')
    if wealth:
        out.append(_ev(
            'resource_wealth_breaks_seal',
            '财星在场：%s（yh.yn_wealth_floods 财多乘旺、必多淹留；'
            'yh.yn_wealth_arrives_floods 最忌财来乘旺、必生淹滞；'
            '财破印效力未裁定，不判破格）。'
            % ctx.god_position_text(wealth)))
    officer = ctx.god_positions('正官') + ctx.god_positions('七杀')
    if officer:
        out.append(_ev(
            'resource_officer_generates_seal',
            '官杀在场：%s（yh.ys_guangui_sheng 官鬼能生我、只畏其财；'
            '官印相生方向已见，效力未裁定）。'
            % ctx.god_position_text(officer)))
    if god == '偏印' and ctx.has_any_god('食神'):
        out.append(_ev(
            'resource_seal_seizes_food',
            '食神在场：%s（yh.ds_mechanism 倒食：甲用食神、大忌见之；'
            '偏印夺食效力未裁定，不判破格）。'
            % ctx.god_position_text(ctx.god_positions('食神'))))
    month_hour = [p for p in positions if p['pillar'] in ('month', 'hour')]
    if month_hour:
        out.append(_ev(
            'resource_month_hour_position',
            '印见于%s（yh.yn_month_hour_position 月与时上见者为妙、'
            '而月上最为紧要；评价以印格成立为前提，成立未裁定）。'
            % '、'.join(PILLAR_CN[p['pillar']] + '柱' for p in month_hour)))
    return out


def _luren_condition_evidence(ctx, kind):
    """禄刃条件事实（三命《论十干禄》/《论阳刃》/《论日刃》yh.yr_* /
    yh.rr_*）：位置事实可算，禄刃成格 determination 恒 None。"""
    out = []
    if kind == 'lu':
        lu = LU_BRANCH[ctx.day_stem]
        if ctx.branches[2] == lu:
            out.append(_ev(
                'day_lu_position',
                '日支 %s 为 %s 日之禄支（三命《论十干禄》禄表；'
                '日禄位置事实，建禄成格无已审依据）。'
                % (lu, ctx.day_stem)))
        return out
    ren = REN_BRANCH.get(ctx.day_stem)
    if ren is None:
        return out
    day_ganzhi = ctx.stems[2] + ctx.branches[2]
    if ctx.branches[2] == ren:
        out.append(_ev(
            'day_ren_position',
            '日支 %s 为 %s 日之刃支（三命《论阳刃》刃表；'
            '日刃位置事实，阳刃成格无已审依据）。'
            % (ren, ctx.day_stem)))
        if day_ganzhi in DAY_REN_PILLARS:
            out.append(_ev(
                'day_ren_enumerated',
                '日柱 %s 在《论日刃》所列三柱内（yh.rr_same_method 日刃有'
                '戊午、丙午、壬子也、与阳刃同法；列举事实，'
                '日刃格 determination 恒 None）。' % day_ganzhi))
    killing = ctx.god_positions('七杀')
    if killing and (ctx.month_branch == ren or ctx.branches[2] == ren):
        out.append(_ev(
            'blade_killing_present',
            '刃杀俱全在场：刃（%s）与七杀（%s）共现'
            '（yh.yr_blade_killing_strength 杀无刃不显、刃无杀不威，'
            '刃杀俱全、非常人有之；评价以阳刃格成立为前提，'
            '成立未裁定）。'
            % (ren, ctx.god_position_text(killing))))
    wealth = ctx.god_positions('偏财')
    if wealth and (ctx.month_branch == ren or ctx.branches[2] == ren):
        out.append(_ev(
            'blade_wealth_present',
            '偏财在场：%s（yh.yr_wealth_preference 凡有刃者、却喜偏财七杀；'
            '喜忌方向已见，效力未裁定）。'
            % ctx.god_position_text(wealth)))
    return out


def _zaqi_variant_evidence(ctx, lookup):
    """杂气三向 Variant 并列（Q13）：原注 / 三命 / 子平真诠 Ch16
    各自陈述，不强行统一，不代选。"""
    exposed = lookup.get('exposed_renyuan') or []
    exposed_text = '、'.join('%s（%s）' % (row['stem'], row['ten_god'])
                             for row in exposed) if exposed else '无人元透出'
    arm = lookup.get('arm')
    if arm == 'wuji_exposed_renyuan':
        yuanzhu = ('原注 Variant（戊己臂）：当看人元透出天干者取格；'
                   '透出者并列：%s；原文不予定序定名，不代选。' % exposed_text)
    else:
        yuanzhu = ('原注 Variant（一般臂）：只当取土为格、不可言杂气财官；'
                   '土格换算（“土”是否指月支本气之土、再对日干作十神换算）'
                   '未裁定；透出者只作事实并列：%s。' % exposed_text)
    return [
        _ev('zaqi_variant_yuanzhu', yuanzhu),
        _ev('zaqi_variant_sanming',
            '三命 Variant：杂气格为正式格名（s066 卷六《日禄归时》实案'
            '“作杂气格论尤是”、s067 女命章“杂气格中禄最佳”）；'
            '与原注“不可言杂气财官”直接对立，不裁定。'),
        _ev('zaqi_variant_ziping',
            '子平真诠 Ch16 Variant（ziping-zaqi-ch16-v1，第三立场）：'
            'B-16-03“透干會支。取其清者用之。”直接命名杂气财官印；'
            '11 条（B-16-03–B-16-10、B-16-12–B-16-14）与原注一般臂直接'
            '对立；B-16-10 会支句、B-16-16 机制句、B-16-18 理由句不可引；'
            '清 / 有情无定义、无阈值；determination 恒 None，'
            'evidence_binding 恒 pending。'),
    ]


def evaluate_zhengguan(ctx):
    """正官： reviewed candidate rule (Golden 20); s055 hour-killing
    caution is a conflict, never a 破格 verdict."""
    if ctx.earth_gate:
        return ctx.earth_result('zhengguan')
    established = ctx.ren_yin_pattern()
    if established is not None and established[0] == '正官格':
        result = _ten_god_evaluator(
            ctx, 'zhengguan', '正官',
            candidate_rule_id='bazi.phase2.official_pattern_candidates',
            candidate_rule_note='正官结构候选（validated，Golden 20）。',
            no_rule_note='',
            conditions=_official_condition_evidence(ctx),
            broken_gap='破格缺口：官杀去留效力（yh.gs_example_zhifu 行火乡制伏、'
                       'yh.gt_clear 除而清之）与清浊标准未裁定，'
                       '故正官破格条件无，broken 永不输出。')
        # D-1 establishes the true pattern, but an hour 七杀 co-presence
        # still carries the s055 additional-review caution.
        hour_killing = _hour_killing_positions(ctx)
        if hour_killing:
            result['evidence'].append(_ev(
                'hour_killing_restriction_s055',
                '时柱另见七杀（%s）：《渊海》s055 提示追加审核，'
                '与 D-1 真格成立并列记录，不改写成立结论。'
                % '、'.join('%s：%s' % (k, v) for k, v in hour_killing)))
            result['limitations'].append(
                '时七杀共现：s055 追加审核仍待另行裁定（官杀去留未裁定）。')
        return result
    row = ctx.month_hidden_god('正官')
    if row is None:
        # Yuanhai 甲辛 / 巳酉丑 single-example branch: 甲日、酉月、
        # 辛不透、巳酉丑齐备 -- a reviewed structural candidate, not a
        # determination.
        branch = _yuanhai_unexposed_official_branch(ctx)
        if branch is not None:
            return _result(
                ctx, 'zhengguan', 'candidate', branch,
                ['单例观察（《渊海》s056 甲辛酉月例）：不定正官格、'
                 '不定合化、身旺、真假成败或喜用；不外推他日他月。'],
                rule_ids=['bazi.phase2.official_pattern_candidates'])
        return _ten_god_evaluator(
            ctx, 'zhengguan', '正官',
            candidate_rule_id='bazi.phase2.official_pattern_candidates',
            candidate_rule_note='正官结构候选（validated，Golden 20）。',
            no_rule_note='')
    hour_killing = _hour_killing_positions(ctx)
    if hour_killing:
        evidence = [
            _ev('month_hidden_official',
                '月支 %s 藏正官 %s。' % (ctx.month_branch, row['stem'])),
            _ev('hour_killing_restriction_s055',
                '时柱见七杀（%s）：《渊海》s055 提示不得直称正官，'
                '只标注追加审核。'
                % '、'.join('%s：%s' % (k, v) for k, v in hour_killing)),
            _ev('guansha_variant_s055',
                '官杀混杂 Variant（s055）：时干支逢杀、不得直称正官，'
                '只追加审核；不定混杂、不定破格。'),
            _ev('guansha_variant_yuanhai_zhifu',
                '官杀混杂 Variant（《论官杀混杂要制伏》yh.gs_example_zhifu）：'
                '若有金或庚申、则混杂为杀、以伤其身，要行火乡制伏、'
                '则发福也；去留操作与效力未裁定。两 Variant 并列，'
                '不统一、不代选。'),
            _ev('official_candidate_rule',
                '正官结构候选（validated，Golden 20）：'
                '官杀去留 / 混杂未裁定。'),
        ]
        evidence.extend(_official_condition_evidence(ctx))
        return _result(
            ctx, 'zhengguan', 'conflict', evidence,
            ['s055 只作追加审核标注：不定官杀混杂、不定破格、'
             '不定正官格成立与否；两说并列，未裁定。',
             '破格缺口：官杀去留效力与清浊标准未裁定，'
             '故正官破格条件无，broken 永不输出。'],
            rule_ids=['bazi.phase2.official_pattern_candidates'])
    result = _ten_god_evaluator(
        ctx, 'zhengguan', '正官',
        candidate_rule_id='bazi.phase2.official_pattern_candidates',
        candidate_rule_note='正官结构候选（validated，Golden 20）：'
                            '月藏正官及透干位置观察。',
        no_rule_note='官杀去留 / 混杂、司令、旺衰、真假成败喜用均未裁定。',
        conditions=_official_condition_evidence(ctx),
        broken_gap='破格缺口：官杀去留效力（yh.gs_example_zhifu 行火乡制伏、'
                   'yh.gt_clear 除而清之）与清浊标准未裁定，'
                   '故正官破格条件无，broken 永不输出。')
    branch = _yuanhai_unexposed_official_branch(ctx)
    if branch is not None:
        result['evidence'].extend(branch)
    return result


def _yuanhai_unexposed_official_branch(ctx):
    """甲日、酉月、辛不透、巳酉丑齐备的单例分支观察（s056）。"""
    if ctx.day_stem != '甲' or ctx.month_branch != '酉':
        return None
    if any(stem == '辛' for stem in ctx.visible_stems.values()):
        return None
    if not {'巳', '酉', '丑'}.issubset(set(ctx.branches)):
        return None
    return [_ev('yuanhai_unexposed_official_s056',
                '甲日酉月、辛不透、巳酉丑齐备：单例结构观察。'),
            _ev('official_candidate_rule',
                '正官结构候选（validated，Golden 20）所含渊海分支。')]


def _hour_killing_positions(ctx):
    """Hour-pillar 七杀 positions (visible stem or hidden stem)."""
    out = []
    if ctx.visible_ten_gods.get('hour') == '七杀':
        out.append(('时干', ctx.visible_stems['hour']))
    hour_hidden = hidden_stems(ctx.branches[3], ctx.day_stem)
    for row in hour_hidden:
        if row['ten_god'] == '七杀':
            out.append(('时支藏', row['stem']))
    return out


def evaluate_qisha(ctx):
    """七杀： no standalone candidate rule; only month-hidden observation
    plus Ren D-1 establishment (Golden t2-bing-qisha). The candidate now
    carries the registered 〈论七杀〉/〈论官星太过〉 condition facts
    (positions, control, combination, wealth-feeding, blade, seven-day
    enumeration); every condition's efficacy stays unadjudicated, so the
    state machine is candidate / established / not_judgeable only."""
    if ctx.earth_gate:
        return ctx.earth_result('qisha')
    conditions = _qisha_condition_evidence(ctx)
    broken_gap = ('破格缺口：制伏效力（yh.qs_control_present / '
                  'yh.qs_control_moderation 制之太过无阈值）、身旺门'
                  '（yh.qs_naming 身旺有气为偏官、身弱无制为七杀）与合杀'
                  '效力（yh.qs_jia_example_control 贪合忘杀）皆未裁定，'
                  '故七杀破格条件无，broken 永不输出。')
    established = ctx.ren_yin_pattern()
    if established is not None and established[0] == '七杀格':
        return _ten_god_evaluator(
            ctx, 'qisha', '七杀',
            candidate_rule_id='bazi.phase2.ren_yin_true_pattern',
            candidate_rule_note='任氏分支寅月真格（validated，Golden 15）。',
            no_rule_note='',
            conditions=conditions, broken_gap=broken_gap)
    return _ten_god_evaluator(
        ctx, 'qisha', '七杀',
        candidate_rule_id='',
        candidate_rule_note='月藏七杀结构观察（无独立七杀候选规则；'
                            '仅见于正官 / 印绶候选块的共现事实与'
                            'ren_yin Golden t2-bing-qisha）。',
        no_rule_note='制杀 / 身旺合杀 / 身弱无制均未裁定；'
                     '《渊海》〈论七杀〉整节已登记，条件事实已接入候选，'
                     '但无一条可操作句可直接执行（登记结论 determination None）。',
        conditions=conditions, broken_gap=broken_gap)


def _resource_evaluator(ctx, pattern_key, god):
    """正印 / 偏印： reviewed candidate rule (Golden 42); s057/s058
    co-presence facts stay indeterminate, never 财旺破印 / 官印相生."""
    if ctx.earth_gate:
        return ctx.earth_result(pattern_key)
    established = ctx.ren_yin_pattern()
    if established is not None and established[0] == god + '格':
        return _ten_god_evaluator(
            ctx, pattern_key, god,
            candidate_rule_id='bazi.phase2.ren_yin_true_pattern',
            candidate_rule_note='任氏分支寅月真格（validated，Golden 15）。',
            no_rule_note='',
            conditions=_resource_condition_evidence(ctx, god),
            broken_gap='破格缺口：财破印效力（yh.yn_wealth_floods / '
                       'yh.yn_wealth_arrives_floods）、偏印夺食效力'
                       '（yh.ds_mechanism）与制杀效力（yh.ds_killing_control）'
                       '皆未裁定，故印绶破格条件无，broken 永不输出。')
    row = ctx.month_hidden_god(god)
    if row is None:
        return _ten_god_evaluator(
            ctx, pattern_key, god,
            candidate_rule_id='bazi.phase2.resource_pattern_candidates',
            candidate_rule_note='印绶结构候选（validated，Golden 42）。',
            no_rule_note='',
            broken_gap='破格缺口：财破印 / 偏印夺食 / 制杀效力皆未裁定，'
                       '故印绶破格条件无，broken 永不输出。')
    result = _ten_god_evaluator(
        ctx, pattern_key, god,
        candidate_rule_id='bazi.phase2.resource_pattern_candidates',
        candidate_rule_note='印绶结构候选（validated，Golden 42）：'
                            '月藏印及透干位置观察。',
        no_rule_note='财旺破印 / 官印相生 / 官鬼多均 indeterminate'
                     '（s057/s058 共现事实只记方向与位置，不判效力）；'
                     '司令、旺衰、真假成败喜用均未裁定。',
        conditions=_resource_condition_evidence(ctx, god),
        broken_gap='破格缺口：财破印效力（yh.yn_wealth_floods / '
                   'yh.yn_wealth_arrives_floods）、偏印夺食效力'
                   '（yh.ds_mechanism）与制杀效力（yh.ds_killing_control）'
                   '皆未裁定，故印绶破格条件无，broken 永不输出。')
    # Yuanhai s059 month-generating-me example, when it applies.
    if ctx.month_branch in YUANHAI_RESOURCE_MONTHS[ctx.day_stem]:
        result['evidence'].append(_ev(
            'yuanhai_resource_month_example_s059',
            '渊海 s059 月份生我例：%s 日生于 %s 月（仅例举，不定印格）。'
            % (ctx.day_stem, ctx.month_branch)))
    competing = _resource_competing(ctx)
    result['evidence'].extend(competing)
    return result


def _resource_competing(ctx):
    """财 / 官 / 杀与月藏印共现的方向事实（s057/s058），效力未裁定。"""
    out = []
    for name in ('year', 'month', 'hour'):
        god = ctx.visible_ten_gods[name]
        if god in ('正财', '偏财'):
            out.append(_ev('resource_context_visible_wealth',
                           '%s干 %s（%s）与月藏印共现：五行克印方向已见，'
                           '效力 indeterminate。'
                           % (name, ctx.visible_stems[name], god)))
        elif god in ('正官', '七杀'):
            out.append(_ev('resource_context_visible_official_killing',
                           '%s干 %s（%s）与月藏印共现：五行生印方向已见，'
                           '效力 indeterminate。'
                           % (name, ctx.visible_stems[name], god)))
    for row in ctx.month_hidden:
        if row['ten_god'] in ('正财', '偏财', '正官', '七杀'):
            out.append(_ev('resource_context_hidden_actor',
                           '月支藏 %s（%s）与月藏印共现：方向已见，'
                           '效力 indeterminate。'
                           % (row['stem'], row['ten_god'])))
    return out


def evaluate_zhengyin(ctx):
    return _resource_evaluator(ctx, 'zhengyin', '正印')


def evaluate_pianyin(ctx):
    return _resource_evaluator(ctx, 'pianyin', '偏印')


def _wealth_evaluator(ctx, pattern_key, god):
    """正财 / 偏财： no standalone candidate rule; only month-hidden
    observation plus Ren D-1 establishment (Golden t1-wu-zhengcai).
    The candidate now carries the registered 〈论正财〉/〈论偏财〉
    condition facts (positions, robbery, officer, food, exposure)."""
    if ctx.earth_gate:
        return ctx.earth_result(pattern_key)
    conditions = _wealth_condition_evidence(ctx, god)
    broken_gap = ('破格缺口：比劫分夺效力（yh.pc_definition 只恐兄弟姊妹'
                  '有夺之）、财多化官效力（yh.zc_many_transform_officer）'
                  '与财生官链效力（yh.zc_wealth_generates_officer）'
                  '皆未裁定，故财格破格条件无，broken 永不输出。')
    established = ctx.ren_yin_pattern()
    if established is not None and established[0] == god + '格':
        return _ten_god_evaluator(
            ctx, pattern_key, god,
            candidate_rule_id='bazi.phase2.ren_yin_true_pattern',
            candidate_rule_note='任氏分支寅月真格（validated，Golden 15）。',
            no_rule_note='',
            conditions=conditions, broken_gap=broken_gap)
    return _ten_god_evaluator(
        ctx, pattern_key, god,
        candidate_rule_id='',
        candidate_rule_note='月藏%s结构观察（无独立财格候选规则；'
                            '财只见于印绶候选块的共现事实与'
                            'ren_yin Golden t1-wu-zhengcai）。' % god,
        no_rule_note='身旺任财 / 财多身弱 / 财生官等均未裁定；'
                     '《渊海》〈论正财〉〈论偏财〉整节已登记，条件事实'
                     '已接入候选，但无一条可操作句可直接执行'
                     '（登记结论 determination None）。',
        conditions=conditions, broken_gap=broken_gap)


def evaluate_zhengcai(ctx):
    return _wealth_evaluator(ctx, 'zhengcai', '正财')


def evaluate_piancai(ctx):
    return _wealth_evaluator(ctx, 'piancai', '偏财')


def _food_evaluator(ctx, pattern_key, god):
    """食神 / 伤官： no standalone candidate rule; only month-hidden
    observation plus Ren D-1 establishment (食神 Golden t4-jia-shishen,
    伤官 Golden f2-boundary-exact). The candidate now carries the
    registered 〈论伤官〉/〈论食神〉/〈论倒食〉 condition facts."""
    if ctx.earth_gate:
        return ctx.earth_result(pattern_key)
    conditions = _food_condition_evidence(ctx, god)
    broken_gap = ('破格缺口：伤官见官效力（yh.sw_pattern_no_officer）、'
                  '伤尽程度标尺（yh.sw_exhaust_core 伤官务要伤尽，程度词'
                  '无标尺）与倒食夺食效力（yh.ds_mechanism）皆未裁定，'
                  '故食伤破格条件无，broken 永不输出。')
    established = ctx.ren_yin_pattern()
    if established is not None and established[0] == god + '格':
        return _ten_god_evaluator(
            ctx, pattern_key, god,
            candidate_rule_id='bazi.phase2.ren_yin_true_pattern',
            candidate_rule_note='任氏分支寅月真格（validated，Golden 15）。',
            no_rule_note='',
            conditions=conditions, broken_gap=broken_gap)
    return _ten_god_evaluator(
        ctx, pattern_key, god,
        candidate_rule_id='',
        candidate_rule_note='月藏%s结构观察（无独立食伤候选规则；'
                            '仅见于 ren_yin Golden：食神 t4-jia-shishen、'
                            '伤官 f2-boundary-exact）。' % god,
        no_rule_note='伤官见官 / 伤尽 / 泄秀等均未裁定；'
                     '《渊海》〈论伤官〉〈论食神〉整节已登记，条件事实'
                     '已接入候选，但无一条可操作句可直接执行'
                     '（登记结论 determination None）。',
        conditions=conditions, broken_gap=broken_gap)


def evaluate_shishen(ctx):
    return _food_evaluator(ctx, 'shishen', '食神')


def evaluate_shangguan(ctx):
    return _food_evaluator(ctx, 'shangguan', '伤官')


def evaluate_jianlu(ctx):
    """建禄： the only reviewed material is the negative route exclusion
    (pattern_route, validated Golden 9): a 禄 month closes the month
    pattern route and the borrowed route stays undetermined. No basis
    for candidate / established / broken exists; the evaluator now also
    reports the 日禄 position fact (still not_judgeable) and names the
    gap (《论禄》未逐节登记，建禄成格 determination 恒 None)。"""
    if ctx.earth_gate:
        return ctx.earth_result('jianlu')
    route = ctx.route_value()
    lu = LU_BRANCH[ctx.day_stem]
    conditions = _luren_condition_evidence(ctx, 'lu')
    broken_gap = ('破格缺口：建禄成格 / 破格皆无已审依据（禄刃表只用于'
                  '负向排除；《论禄》未逐节登记）；broken 永不输出。')
    if route == 'luren_no_month_pattern' and ctx.month_branch == lu:
        return _result(
            ctx, 'jianlu', 'not_judgeable',
            [_ev('luren_route_exclusion',
                 '月支 %s 为 %s 日之禄支（三命《论十干禄》）：'
                 '任氏 s054“月逢禄刃，无格可取”，月令正格路线关闭。'
                 % (ctx.month_branch, ctx.day_stem)),
             _ev('luren_route_rule',
                 '依据 bazi.phase2.pattern_route（validated，Golden 9）。')]
            + conditions,
            ['借用路线（“借以为用”）恒未定：借神定名规则未审，'
             '建禄是否成格未裁定；不输出候选、成立或破格。',
             broken_gap],
            rule_ids=['bazi.phase2.pattern_route'])
    return _result(
        ctx, 'jianlu', 'not_judgeable',
        [_ev('no_luren_observation',
             '月支 %s 非 %s 日之禄支（禄在 %s）：无禄刃路线事实。'
             % (ctx.month_branch, ctx.day_stem, lu))]
        + conditions,
        ['建禄成格无已审依据：禄刃表只用于负向排除，不作取格规则。',
         broken_gap],
        rule_ids=['bazi.phase2.pattern_route'])


def evaluate_yangren(ctx):
    """阳刃： same negative-exclusion basis as 建禄. Yin day masters have
    no 刃 branch at all (三命《论阳刃》纲句：五阴干无刃). The evaluator
    now also reports 日刃 / 刃杀俱全 / 刃喜偏财 position facts from the
    registered 〈论阳刃〉/〈论日刃〉 (yh.yr_* / yh.rr_*); all stay
    not_judgeable (阳刃格 / 日刃格 determination 恒 None)。"""
    if ctx.earth_gate:
        return ctx.earth_result('yangren')
    route = ctx.route_value()
    ren = REN_BRANCH.get(ctx.day_stem)
    if ren is None:
        return _result(
            ctx, 'yangren', 'not_judgeable',
            [_ev('yin_stem_no_ren',
                 '%s 为阴干：三命《论阳刃》纲句“五阴干无刃”，无刃支可查。'
                 % ctx.day_stem)],
            ['阴干刃位异说在已登记来源中无逐字依据，不登记、不采用；'
             '阳刃成格无已审依据。',
             '破格缺口：阳刃成格 / 破格皆无已审依据；broken 永不输出。'],
            rule_ids=['bazi.phase2.pattern_route'])
    conditions = _luren_condition_evidence(ctx, 'ren')
    broken_gap = ('破格缺口：阳刃成格 / 破格皆无已审依据（yh.yr_* / yh.rr_* '
                  '可操作句全部经身旺 / 制刃效力 / 印财链 / 支关系效力门'
                  '转手，determination 恒 None）；broken 永不输出。')
    if route == 'luren_no_month_pattern' and ctx.month_branch == ren:
        return _result(
            ctx, 'yangren', 'not_judgeable',
            [_ev('luren_route_exclusion',
                 '月支 %s 为 %s 日之刃支（三命《论阳刃》）：'
                 '任氏 s054“月逢禄刃，无格可取”，月令正格路线关闭。'
                 % (ctx.month_branch, ctx.day_stem)),
             _ev('luren_route_rule',
                 '依据 bazi.phase2.pattern_route（validated，Golden 9）。')]
            + conditions,
            ['借用路线恒未定：借神定名规则未审，'
             '阳刃是否成格未裁定；不输出候选、成立或破格。',
             broken_gap],
            rule_ids=['bazi.phase2.pattern_route'])
    return _result(
        ctx, 'yangren', 'not_judgeable',
        [_ev('no_luren_observation',
             '月支 %s 非 %s 日之刃支（刃在 %s）：无禄刃路线事实。'
             % (ctx.month_branch, ctx.day_stem, ren))]
        + conditions,
        ['阳刃成格无已审依据：禄刃表只用于负向排除，不作取格规则。',
         broken_gap],
        rule_ids=['bazi.phase2.pattern_route'])


def evaluate_zaqi(ctx):
    """杂气： reviewed selection statement + school conflict
    (pattern_zaqi, validated Golden 6). A miscellaneous month is a
    conflict (原注 vs 三命), never a determination."""
    if ctx.earth_gate:
        return ctx.earth_result('zaqi')
    if ctx.month_branch not in MISCELLANEOUS_BRANCHES:
        return _result(
            ctx, 'zaqi', 'not_judgeable',
            [_ev('not_miscellaneous_month',
                 '月支 %s 非四季月（辰戌丑未）：杂气选格陈述不适用。'
                 % ctx.month_branch)],
            ['杂气选格只在四季月有陈述；不等于该盘无杂气之论，'
             '只说明本引擎无依据。'],
            rule_ids=['bazi.phase2.pattern_zaqi'])
    if isinstance(ctx.zaqi, dict):
        block = ctx.zaqi
        evidence = [
            _ev('zaqi_selection_statement',
                '杂气选格陈述：臂 %s，状态 %s。'
                % (block.get('arm'), block.get('status'))),
            _ev('zaqi_conflict',
                '流派冲突并列：原注“不可言杂气财官” vs '
                '三命两案以“杂气格”为正式名目（s066/s067），不裁定。'),
            _ev('zaqi_rule',
                '依据 bazi.phase2.pattern_zaqi（validated，Golden 6）。'),
        ]
        selection = (block.get('selection') or {})
        if selection.get('selected_candidates'):
            evidence.append(_ev(
                'zaqi_selected_candidates',
                '戊己臂选格对象（并列，不代选）：%s。'
                % '、'.join('%s（%s）' % (c['stem'], c['ten_god'])
                            for c in selection['selected_candidates'])))
        elif selection.get('earth_conversion'):
            evidence.append(_ev(
                'zaqi_earth_conversion_unadjudicated',
                '一般臂“只当取土为格”原文并列，土格换算未裁定。'))
        evidence.extend(_zaqi_variant_evidence(
            ctx, {'arm': block.get('arm'),
                  'exposed_renyuan': (block.get('selection') or {}).get(
                      'selected_candidates') or (block.get('exposed_renyuan') or [])}))
        return _result(
            ctx, 'zaqi', 'conflict', evidence,
            ['杂气陈述不是定格：不给格名、真假、成败、清浊、用神或喜忌；'
             '土格换算未审；分日司令未裁定。',
             '破格缺口：杂气破格条件无已审依据；broken 永不输出。'],
            rule_ids=['bazi.phase2.pattern_zaqi'])
    # No precomputed block: reuse the reviewed pure lookup.
    exposed = []
    for row in ctx.month_hidden:
        pillars = ctx.exposed_pillars(row['stem'])
        if pillars:
            exposed.append({'stem': row['stem'], 'ten_god': row['ten_god'],
                            'visible_pillars': pillars})
    lookup = zaqi_selection_lookup(
        ctx.day_stem, ctx.month_branch,
        [{'stem': r['stem'], 'ten_god': r['ten_god']}
         for r in ctx.month_hidden], exposed)
    evidence = [
        _ev('zaqi_selection_statement',
            '杂气选格陈述：臂 %s，状态 %s。'
            % (lookup.get('arm'), lookup.get('status'))),
        _ev('zaqi_conflict',
            '流派冲突并列：原注“不可言杂气财官” vs '
            '三命两案以“杂气格”为正式名目（s066/s067），不裁定。'),
        _ev('zaqi_rule',
            '依据 bazi.phase2.pattern_zaqi（validated，Golden 6）。'),
    ]
    selection = lookup.get('selection') or {}
    if selection.get('selected_candidates'):
        evidence.append(_ev(
            'zaqi_selected_candidates',
            '戊己臂选格对象（并列，不代选）：%s。'
            % '、'.join('%s（%s）' % (c['stem'], c['ten_god'])
                        for c in selection['selected_candidates'])))
    elif selection.get('earth_conversion'):
        evidence.append(_ev(
            'zaqi_earth_conversion_unadjudicated',
            '一般臂“只当取土为格”原文并列，土格换算未裁定。'))
    evidence.extend(_zaqi_variant_evidence(ctx, lookup))
    return _result(
        ctx, 'zaqi', 'conflict', evidence,
        ['杂气陈述不是定格：不给格名、真假、成败、清浊、用神或喜忌；'
         '土格换算未审；分日司令未裁定。',
         '破格缺口：杂气破格条件无已审依据；broken 永不输出。'],
        rule_ids=['bazi.phase2.pattern_zaqi'])


def _special_screens(ctx):
    """特殊格局候选屏（Q11）：屏命中与成立规则分离。每一屏只报告
    结构事实命中与否；命中仍只作 candidate，成立恒无依据。

    - 从杀结构屏（yh.cg_follow_killing_rule 弃命从杀、须要会杀；
      yh.cg_cross_rules_root_negation 命逢根气一票否决）：七杀在场 +
      无结构根 + 无制伏在场 + 无印比救援在场。会杀成局判定不存在。
    - 从财结构屏（yh.cg_follow_wealth_rule 弃命从财、须要会财；
      yh.cg_cross_rules_root_negation 从财忌杀）：财在场 + 无结构根 +
      无七杀在场 + 无比劫分夺在场。会财成局判定不存在。
    - 现代工程从格候选屏（与第一批旺衰现代模型同一窄口径，Q4）：
      无结构根、无显干生扶、显干 >= 2 且全为克我 / 我生方向；
      model_kind="modern_engineering"，古典与现代严格区分。
    - 化气结构屏：天干五合在场事实（reviewed_relations）；五合命中
      不代表化气成立（密封 unresolved，合化效力未裁定）。
    - 三奇：三命卷三《论三奇》只见歌诀提及，无可执行规则，不计算，
      只记缺口。
    """
    evidence = []
    limitations = []
    hit = False
    roots = ctx.structural_roots()
    killing = ctx.god_positions('七杀')
    control = ctx.god_positions('食神') + ctx.god_positions('伤官')
    seal = ctx.god_positions('正印') + ctx.god_positions('偏印')
    wealth = ctx.god_positions('正财') + ctx.god_positions('偏财')
    robbery = ctx.god_positions('比肩') + ctx.god_positions('劫财')
    if killing and not roots and not control and not seal and not robbery:
        hit = True
        evidence.append(_ev(
            'congsha_screen_hit',
            '从杀结构屏命中：七杀在场（%s），无结构根、无制伏在场、'
            '无印比救援在场（yh.cg_follow_killing_rule 弃命从杀、须要会杀；'
            'yh.cg_cross_rules_root_negation 命逢根气、命殞无猜——'
            '根气一票否决未触发）。屏命中≠从杀格成立：会杀成局判定'
            '不存在、根级判定未裁、极弱档无定义。'
            % ctx.god_position_text(killing)))
    else:
        reasons = []
        if not killing:
            reasons.append('无七杀在场')
        if roots:
            reasons.append('结构根在场（%d 处），根气一票否决触发'
                           % len(roots))
        if control:
            reasons.append('制伏在场')
        if seal:
            reasons.append('印星救援在场')
        if robbery:
            reasons.append('比劫救援在场')
        evidence.append(_ev(
            'congsha_screen_miss',
            '从杀结构屏未命中：%s。' % '、'.join(reasons)))
    if wealth and not roots and not killing and not robbery:
        hit = True
        evidence.append(_ev(
            'congcai_screen_hit',
            '从财结构屏命中：财在场（%s），无结构根、无七杀在场、'
            '无比劫分夺在场（yh.cg_follow_wealth_rule 弃命从财、须要会财；'
            'yh.cg_cross_rules_root_negation 从财忌杀）。屏命中≠从财格'
            '成立：会财成局判定不存在、根级判定未裁、极弱档无定义。'
            % ctx.god_position_text(wealth)))
    else:
        reasons = []
        if not wealth:
            reasons.append('无财在场')
        if roots:
            reasons.append('结构根在场（%d 处），根气一票否决触发'
                           % len(roots))
        if killing:
            reasons.append('七杀在场（从财忌杀）')
        if robbery:
            reasons.append('比劫分夺在场')
        evidence.append(_ev(
            'congcai_screen_miss',
            '从财结构屏未命中：%s。' % '、'.join(reasons)))
    kinds = ctx.visible_relation_kinds()
    if not roots and len(kinds) >= 2 and all(
            kind in ('controls_me', 'i_generate') for kind in kinds):
        hit = True
        evidence.append(_ev(
            'cong_screen_hit_modern',
            '现代工程从格候选屏命中（model_kind="modern_engineering"，'
            '与第一批旺衰模型同一窄口径 Q4）：无结构根、无显干生扶、'
            '显干 %d 个全为克我 / 我生方向。屏命中≠从格成立：'
            '古典从格成立本身未裁定，现代屏不作古典结论。'
            % len(kinds)))
    else:
        evidence.append(_ev(
            'cong_screen_miss_modern',
            '现代工程从格候选屏未命中：结构根 %d 处、显干关系 %s。'
            % (len(roots), '、'.join(kinds) if kinds else '无')))
    if ctx.five_combinations:
        hit = True
        evidence.append(_ev(
            'huaqi_combination_screen',
            '化气结构屏命中：天干五合在场（%s）。五合命中不代表化气'
            '成立（密封 unresolved；合化效力未裁定）。'
            % '、'.join('%s（%s，化%s）' % (
                '、'.join(pair['pillars']), '＋'.join(pair['stems']),
                pair['traditional_result_element'])
                for pair in ctx.five_combinations)))
    else:
        evidence.append(_ev(
            'huaqi_combination_screen_miss',
            '化气结构屏未命中：四柱天干无五合。'))
    limitations.append(
        '三奇缺口：三命卷三《论三奇》只见歌诀提及，无可执行规则，'
        '本引擎不计算三奇。')
    limitations.append(
        '从格 / 化气成立恒无依据：从杀、从财格 determination 恒 None'
        '（yh.cg_* 登记结论）；化气成立以合化裁定为前提，合化未裁定。')
    limitations.append(
        '破格缺口：从格 / 化气破格条件无已审依据；broken 永不输出。')
    return hit, evidence, limitations


def evaluate_special(ctx):
    """特殊格局（从格 / 化气 / 三奇等）： no reviewed establishment rule.
    Sealed unresolved: 五合命中不代表化气成立；格局未完成证据裁定；
    factors() leaves 从格 / 旺极衰极 unlisted. v2 reports the four
    separated candidate screens (从杀 / 从财 / 现代从格屏 / 化气);
    a screen hit is a candidate, never an establishment."""
    if ctx.earth_gate:
        return ctx.earth_result('special')
    hit, evidence, limitations = _special_screens(ctx)
    base = [
        _ev('no_special_pattern_rule',
            '密封 phase2_execution 无从格 / 化气 / 三奇等特殊格局成立规则；'
            'unresolved 明言“旺衰、格局、喜用神尚未完成证据裁定”。'),
        _ev('huaqi_not_established',
            '五合 / 六合命中不代表化气成立（密封 unresolved）。'),
        _ev('strength_factors_unresolved',
            'factors() 未纳入从格、旺极衰极与阴阳十二长生；'
            'overall_strength 为 None。'),
    ]
    if hit:
        return _result(
            ctx, 'special', 'candidate', base + evidence,
            ['候选屏命中≠特殊格局成立：不得以屏命中推定从格、化气格'
             '或任何外格；需新的逐项证据裁定与用户裁定。'] + limitations,
            rule_ids=[])
    return _result(
        ctx, 'special', 'not_judgeable', base + evidence,
        ['特殊格局全部未裁定：不得以月令、合化或旺衰因素推定从格、'
         '化气格或任何外格；需新的逐项证据裁定与用户裁定。'] + limitations,
        rule_ids=[])


def _extra_ten_god_evaluator(ctx, pattern_key, god):
    """比肩 / 劫财： only reachable through Ren D-1 (Golden a2/a4)."""
    if ctx.earth_gate:
        return ctx.earth_result(pattern_key)
    established = ctx.ren_yin_pattern()
    if established is not None and established[0] == god + '格':
        result = _ten_god_evaluator(
            ctx, pattern_key, god,
            candidate_rule_id='bazi.phase2.ren_yin_true_pattern',
            candidate_rule_note='任氏分支寅月真格（validated，Golden 15）。',
            no_rule_note='')
        result['limitations'].append(
            '公开投影白名单外：%s 不在已审八格公开名目内，'
            '公开呈现时为 not_judgeable（pattern_name_not_public）。' % (god + '格'))
        return result
    return None


def evaluate_bijian(ctx):
    result = _extra_ten_god_evaluator(ctx, 'bijian', '比肩')
    return result if result is not None else _result(
        ctx, 'bijian', 'not_judgeable',
        [_ev('no_bijian_basis', '比肩格只见于任氏 D-1 机械换算名，本盘未成立。')],
        ['比肩不属本批十二格；无 D-1 成立即无依据。'],
        rule_ids=[])


def evaluate_jiecai(ctx):
    result = _extra_ten_god_evaluator(ctx, 'jiecai', '劫财')
    return result if result is not None else _result(
        ctx, 'jiecai', 'not_judgeable',
        [_ev('no_jiecai_basis', '劫财格只见于任氏 D-1 机械换算名，本盘未成立。')],
        ['劫财不属本批十二格；无 D-1 成立即无依据。'],
        rule_ids=[])


_EVALUATORS = {
    'zhengguan': evaluate_zhengguan,
    'qisha': evaluate_qisha,
    'zhengyin': evaluate_zhengyin,
    'pianyin': evaluate_pianyin,
    'zhengcai': evaluate_zhengcai,
    'piancai': evaluate_piancai,
    'shishen': evaluate_shishen,
    'shangguan': evaluate_shangguan,
    'jianlu': evaluate_jianlu,
    'yangren': evaluate_yangren,
    'zaqi': evaluate_zaqi,
    'special': evaluate_special,
    'bijian': evaluate_bijian,
    'jiecai': evaluate_jiecai,
}


def evaluate_pattern(chart, pattern_key, *, official=None, resource=None,
                     route=None, zaqi=None, ren_yin=None):
    """Evaluate one pattern over a ``chart_from_pillars`` chart."""
    if pattern_key not in _EVALUATORS:
        raise ValueError('Unknown pattern key: %s' % pattern_key)
    ctx = _Context(chart, official=official, resource=resource, route=route,
                   zaqi=zaqi, ren_yin=ren_yin)
    return _EVALUATORS[pattern_key](ctx)


def evaluate_all(chart, *, official=None, resource=None, route=None,
                 zaqi=None, ren_yin=None):
    """Evaluate all twelve patterns over a ``chart_from_pillars`` chart.

    Optional precomputed reviewed blocks (from a trace) are consumed as
    evidence; otherwise each evaluator computes the same structural
    facts directly from the pillars.
    """
    ctx = _Context(chart, official=official, resource=resource, route=route,
                   zaqi=zaqi, ren_yin=ren_yin)
    results = {key: _EVALUATORS[key](ctx) for key, _, _ in PATTERNS}
    established = ctx.ren_yin_pattern()
    if established is not None and established[0] in ('比肩格', '劫财格'):
        extra_key = EXTRA_TEN_GOD_PATTERNS[established[0][:2]]
        results[extra_key] = _EVALUATORS[extra_key](ctx)
    counts = {}
    for result in results.values():
        counts[result['state']] = counts.get(result['state'], 0) + 1
    return {
        'variant': PATTERN_ENGINE_VARIANT,
        'pattern_variant': PATTERN_VARIANT,
        'ren_yin_determination_variant': REN_YIN_TRUE_VARIANT,
        'luren_route_variant': LUREN_ROUTE_VARIANT,
        'day_stem': ctx.day_stem,
        'month_branch': ctx.month_branch,
        'earth_gate': ctx.earth_gate,
        'strength_overall': ctx.strength_factors['overall_strength'],
        'results': results,
        'counts': counts,
        'research_only': True,
        'public': False,
        'ai': False,
        'scope': ('十二格逐格评估（研究用）：成立只认任氏寅月真格；'
                  '候选附各格已登记条件事实（在场可算、效力未裁定）；'
                  '破格恒不输出（逐格破格缺口见各结果 limitations）；'
                  '古典规则与现代工程判断严格区分。'),
    }


def _trace_view(trace):
    if hasattr(trace, 'steps') and hasattr(trace, 'evidence'):
        return trace
    if isinstance(trace, dict) and 'trace' in trace and 'evidence' in trace:
        class _View:
            pass
        view = _View()
        view.steps = trace['trace']
        view.evidence = trace['evidence']
        return view
    raise ValueError('Pattern engine requires an executed trace')


def evaluate_patterns_from_trace(trace, *, pilot_result=None):
    """Evaluate all patterns from an executed bazi trace.

    Reuses the reviewed blocks (candidates / route / zaqi / ren_yin)
    from ``bazi_pattern``; ``pilot_result`` is the explicit Slice C
    pilot block (None means no Ren D-1 determination is attempted).
    Fails closed when the required executed steps are absent.
    """
    view = _trace_view(trace)
    steps = {row['rule_id']: row for row in view.steps}
    required = ('pillars', 'ten_gods', 'hidden_stems', 'hidden_to_visible',
                'month_command_variant')
    if any('bazi.phase2.' + name not in steps for name in required):
        raise ValueError('Pattern engine trace lacks executed structural steps')
    for name in required:
        step = steps['bazi.phase2.' + name]
        if not step['evidence_ids'] or any(
                e not in view.evidence for e in step['evidence_ids']):
            raise ValueError('Pattern engine trace lacks executed evidence')
    pillars_out = steps['bazi.phase2.pillars']['output']
    ganzhi = pillars_out['ganzhi']
    chart = {
        'pillars': [
            {'name': name,
             'stem': {'value': ganzhi[i][0]},
             'branch': {'value': ganzhi[i][1]}}
            for i, name in enumerate(('year', 'month', 'day', 'hour'))
        ],
        'day_master': {'stem': pillars_out['day_master']['stem']},
    }
    official = _pattern_candidates(view, family='official')
    resource = _pattern_candidates(view, family='resource')
    route = month_pattern_route(view)
    zaqi = month_pattern_zaqi(view)
    ren_yin = (ren_yin_true_pattern(view, pilot_result)
               if pilot_result is not None else None)
    return evaluate_all(chart, official=official, resource=resource,
                        route=route, zaqi=zaqi, ren_yin=ren_yin)
