"""Pattern engine (TJ-0424): one evaluator per pattern, research_only.

Assembles the already-reviewed pattern material into a single per-pattern
assessment. It invents no new pattern rule: every state is either

- ``established`` -- only through the Ren-branch 寅月 true-pattern block
  (``ren_yin_true_pattern``, bazi.phase2.ren_yin_true_pattern, validated,
  Golden 15), the single reviewed determination in the sealed tree;
- ``candidate`` -- a reviewed structural observation only
  (official_pattern_candidates, validated Golden 20;
  resource_pattern_candidates, validated Golden 42; or a plain
  month-hidden ten-god observation where no candidate rule exists);
- ``conflict`` -- two reviewed branches disagree and neither is adjudicated
  (正官 + 时七杀 s055 caution; 杂气原注 vs 三命, pattern_zaqi,
  validated Golden 6);
- ``not_judgeable`` -- no reviewed basis for this pattern on this chart.

``broken`` is never emitted: no per-pattern 破格 condition is reviewed
anywhere in the sealed tree (the Ren block marks success_failure /
purity / useful_god unreviewed for every case; the official-candidate
evidence scope states 官杀/破印未裁定). A pattern that cannot be
established is reported as candidate / conflict / not_judgeable, never
as broken.

Classical rules and any modern engineering judgement are kept apart:
this module performs no modern scoring, no weights, no strength
classification. Strength is consumed only through
``bazi_strength.factors()`` and only as listed factors (roots,
visibility, month command); its ``overall_strength`` is always None
and is reported as unresolved wherever it would matter.

Governance: research_only=True, public=False, ai=False throughout.
Nothing here is a public API field and nothing is wired into
``public_projection``. 戊×巳 / 己×午 are always not_judgeable
(TJ-011.2: earth day-master pattern formation is unbuildable).
"""

from .bazi_core import hidden_stems, ten_god
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

PATTERN_ENGINE_VARIANT = 'bazi-pattern-engine-v1'

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
                       candidate_rule_note, no_rule_note):
    """Shared logic for the eight ten-god patterns (正官/七杀/正印/偏印/
    正财/偏财/食神/伤官)."""
    if ctx.earth_gate:
        return ctx.earth_result(pattern_key)
    established = ctx.ren_yin_pattern()
    if established is not None and established[0] == god + '格':
        return _result(
            ctx, pattern_key, 'established',
            [_ev('ren_yin_true_pattern',
                 '任氏分支寅月真格成立：司令 %s（%s）透于 %s。'
                 % (established[1], god, '、'.join(established[2]) or '无')),
             _ev('ren_yin_rule',
                 '依据 bazi.phase2.ren_yin_true_pattern（validated，'
                 'Golden 15；s053 原注定义句 + s054 任氏曰程序句）。')],
            ['破格 / 成败 / 清浊 / 用神恒未审（八格章无逐格破格条件句）；'
             '只裁定寅月任氏分支真格成立，不外推其他月份与流派。'],
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
        return _result(ctx, pattern_key, 'not_judgeable', evidence,
                       ['无月藏 %s 观察：不等于该盘无此格，只说明本引擎无依据。' % god],
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
    limitations = [
        '只作候选观察：分日司令未裁定（寅月以外）、旺衰未裁定、'
        '真假 / 成败 / 清浊 / 用神未裁定。',
        no_rule_note,
    ]
    return _result(ctx, pattern_key, 'candidate', evidence, limitations,
                   rule_ids=[candidate_rule_id] if candidate_rule_id else [])


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
            no_rule_note='')
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
        return _result(
            ctx, 'zhengguan', 'conflict',
            [_ev('month_hidden_official',
                 '月支 %s 藏正官 %s。' % (ctx.month_branch, row['stem'])),
             _ev('hour_killing_restriction_s055',
                 '时柱见七杀（%s）：《渊海》s055 提示不得直称正官，'
                 '只标注追加审核。'
                 % '、'.join('%s：%s' % (k, v) for k, v in hour_killing)),
             _ev('official_candidate_rule',
                 '正官结构候选（validated，Golden 20）：'
                 '官杀去留 / 混杂未裁定。')],
            ['s055 只作追加审核标注：不定官杀混杂、不定破格、'
             '不定正官格成立与否；两说并列，未裁定。'],
            rule_ids=['bazi.phase2.official_pattern_candidates'])
    result = _ten_god_evaluator(
        ctx, 'zhengguan', '正官',
        candidate_rule_id='bazi.phase2.official_pattern_candidates',
        candidate_rule_note='正官结构候选（validated，Golden 20）：'
                            '月藏正官及透干位置观察。',
        no_rule_note='官杀去留 / 混杂、司令、旺衰、真假成败喜用均未裁定。')
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
    plus Ren D-1 establishment (Golden t2-bing-qisha)."""
    if ctx.earth_gate:
        return ctx.earth_result('qisha')
    established = ctx.ren_yin_pattern()
    if established is not None and established[0] == '七杀格':
        return _ten_god_evaluator(
            ctx, 'qisha', '七杀',
            candidate_rule_id='bazi.phase2.ren_yin_true_pattern',
            candidate_rule_note='任氏分支寅月真格（validated，Golden 15）。',
            no_rule_note='')
    return _ten_god_evaluator(
        ctx, 'qisha', '七杀',
        candidate_rule_id='',
        candidate_rule_note='月藏七杀结构观察（无独立七杀候选规则；'
                            '仅见于正官 / 印绶候选块的共现事实与'
                            'ren_yin Golden t2-bing-qisha）。',
        no_rule_note='制杀 / 身旺合杀 / 身弱无制均未裁定；'
                     '《渊海》〈论七杀〉整节已登记，未转为可执行选格规则。')


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
            no_rule_note='')
    row = ctx.month_hidden_god(god)
    if row is None:
        return _ten_god_evaluator(
            ctx, pattern_key, god,
            candidate_rule_id='bazi.phase2.resource_pattern_candidates',
            candidate_rule_note='印绶结构候选（validated，Golden 42）。',
            no_rule_note='')
    result = _ten_god_evaluator(
        ctx, pattern_key, god,
        candidate_rule_id='bazi.phase2.resource_pattern_candidates',
        candidate_rule_note='印绶结构候选（validated，Golden 42）：'
                            '月藏印及透干位置观察。',
        no_rule_note='财旺破印 / 官印相生 / 官鬼多均 indeterminate'
                     '（s057/s058 共现事实只记方向与位置，不判效力）；'
                     '司令、旺衰、真假成败喜用均未裁定。')
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
    observation plus Ren D-1 establishment (Golden t1-wu-zhengcai)."""
    if ctx.earth_gate:
        return ctx.earth_result(pattern_key)
    established = ctx.ren_yin_pattern()
    if established is not None and established[0] == god + '格':
        return _ten_god_evaluator(
            ctx, pattern_key, god,
            candidate_rule_id='bazi.phase2.ren_yin_true_pattern',
            candidate_rule_note='任氏分支寅月真格（validated，Golden 15）。',
            no_rule_note='')
    return _ten_god_evaluator(
        ctx, pattern_key, god,
        candidate_rule_id='',
        candidate_rule_note='月藏%s结构观察（无独立财格候选规则；'
                            '财只见于印绶候选块的共现事实与'
                            'ren_yin Golden t1-wu-zhengcai）。' % god,
        no_rule_note='身旺任财 / 财多身弱 / 财生官等均未裁定；'
                     '《渊海》〈论正财〉整节已登记，未转为可执行选格规则。')


def evaluate_zhengcai(ctx):
    return _wealth_evaluator(ctx, 'zhengcai', '正财')


def evaluate_piancai(ctx):
    return _wealth_evaluator(ctx, 'piancai', '偏财')


def _food_evaluator(ctx, pattern_key, god):
    """食神 / 伤官： no standalone candidate rule; only month-hidden
    observation plus Ren D-1 establishment (食神 Golden t4-jia-shishen,
    伤官 Golden f2-boundary-exact)."""
    if ctx.earth_gate:
        return ctx.earth_result(pattern_key)
    established = ctx.ren_yin_pattern()
    if established is not None and established[0] == god + '格':
        return _ten_god_evaluator(
            ctx, pattern_key, god,
            candidate_rule_id='bazi.phase2.ren_yin_true_pattern',
            candidate_rule_note='任氏分支寅月真格（validated，Golden 15）。',
            no_rule_note='')
    return _ten_god_evaluator(
        ctx, pattern_key, god,
        candidate_rule_id='',
        candidate_rule_note='月藏%s结构观察（无独立食伤候选规则；'
                            '仅见于 ren_yin Golden：食神 t4-jia-shishen、'
                            '伤官 f2-boundary-exact）。' % god,
        no_rule_note='伤官见官 / 伤尽 / 泄秀等均未裁定；'
                     '《渊海》〈论伤官〉整节已登记，未转为可执行选格规则。')


def evaluate_shishen(ctx):
    return _food_evaluator(ctx, 'shishen', '食神')


def evaluate_shangguan(ctx):
    return _food_evaluator(ctx, 'shangguan', '伤官')


def evaluate_jianlu(ctx):
    """建禄： the only reviewed material is the negative route exclusion
    (pattern_route, validated Golden 9): a 禄 month closes the month
    pattern route and the borrowed route stays undetermined. No basis
    for candidate / established / broken exists."""
    if ctx.earth_gate:
        return ctx.earth_result('jianlu')
    route = ctx.route_value()
    lu = LU_BRANCH[ctx.day_stem]
    if route == 'luren_no_month_pattern' and ctx.month_branch == lu:
        return _result(
            ctx, 'jianlu', 'not_judgeable',
            [_ev('luren_route_exclusion',
                 '月支 %s 为 %s 日之禄支（三命《论十干禄》）：'
                 '任氏 s054“月逢禄刃，无格可取”，月令正格路线关闭。'
                 % (ctx.month_branch, ctx.day_stem)),
             _ev('luren_route_rule',
                 '依据 bazi.phase2.pattern_route（validated，Golden 9）。')],
            ['借用路线（“借以为用”）恒未定：借神定名规则未审，'
             '建禄是否成格未裁定；不输出候选、成立或破格。'],
            rule_ids=['bazi.phase2.pattern_route'])
    return _result(
        ctx, 'jianlu', 'not_judgeable',
        [_ev('no_luren_observation',
             '月支 %s 非 %s 日之禄支（禄在 %s）：无禄刃路线事实。'
             % (ctx.month_branch, ctx.day_stem, lu))],
        ['建禄成格无已审依据：禄刃表只用于负向排除，不作取格规则。'],
        rule_ids=['bazi.phase2.pattern_route'])


def evaluate_yangren(ctx):
    """阳刃： same negative-exclusion basis as 建禄. Yin day masters have
    no 刃 branch at all (三命《论阳刃》纲句：五阴干无刃)."""
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
             '阳刃成格无已审依据。'],
            rule_ids=['bazi.phase2.pattern_route'])
    if route == 'luren_no_month_pattern' and ctx.month_branch == ren:
        return _result(
            ctx, 'yangren', 'not_judgeable',
            [_ev('luren_route_exclusion',
                 '月支 %s 为 %s 日之刃支（三命《论阳刃》）：'
                 '任氏 s054“月逢禄刃，无格可取”，月令正格路线关闭。'
                 % (ctx.month_branch, ctx.day_stem)),
             _ev('luren_route_rule',
                 '依据 bazi.phase2.pattern_route（validated，Golden 9）。')],
            ['借用路线恒未定：借神定名规则未审，'
             '阳刃是否成格未裁定；不输出候选、成立或破格。'],
            rule_ids=['bazi.phase2.pattern_route'])
    return _result(
        ctx, 'yangren', 'not_judgeable',
        [_ev('no_luren_observation',
             '月支 %s 非 %s 日之刃支（刃在 %s）：无禄刃路线事实。'
             % (ctx.month_branch, ctx.day_stem, ren))],
        ['阳刃成格无已审依据：禄刃表只用于负向排除，不作取格规则。'],
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
        return _result(
            ctx, 'zaqi', 'conflict', evidence,
            ['杂气陈述不是定格：不给格名、真假、成败、清浊、用神或喜忌；'
             '土格换算未审；分日司令未裁定。'],
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
    return _result(
        ctx, 'zaqi', 'conflict', evidence,
        ['杂气陈述不是定格：不给格名、真假、成败、清浊、用神或喜忌；'
         '土格换算未审；分日司令未裁定。'],
        rule_ids=['bazi.phase2.pattern_zaqi'])


def evaluate_special(ctx):
    """特殊格局（从格 / 化气 / 三奇等）： no reviewed rule at all.
    Sealed unresolved: 五合命中不代表化气成立；格局未完成证据裁定；
    factors() leaves 从格 / 旺极衰极 unlisted."""
    if ctx.earth_gate:
        return ctx.earth_result('special')
    return _result(
        ctx, 'special', 'not_judgeable',
        [_ev('no_special_pattern_rule',
             '密封 phase2_execution 无从格 / 化气 / 三奇等特殊格局规则；'
             'unresolved 明言“旺衰、格局、喜用神尚未完成证据裁定”。'),
         _ev('huaqi_not_established',
             '五合 / 六合命中不代表化气成立（密封 unresolved）。'),
         _ev('strength_factors_unresolved',
             'factors() 未纳入从格、旺极衰极与阴阳十二长生；'
             'overall_strength 为 None。')],
        ['特殊格局全部未裁定：不得以月令、合化或旺衰因素推定从格、'
         '化气格或任何外格；需新的逐项证据裁定与用户裁定。'],
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
                  '破格恒不输出；古典规则与现代工程判断严格区分。'),
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
