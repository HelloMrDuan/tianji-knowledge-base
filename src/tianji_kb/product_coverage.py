"""Derived product audit over existing registries and validators, never a knowledge store."""
from __future__ import annotations

from collections import Counter
import ast
import hashlib
import json
from pathlib import Path

from .engine import PROVIDERS
from .knowledge import read_json, validate_protected_files
from .knowledge_index import iter_phase1_chunks
from .resolver import EvidenceResolver
from .scenario_engine import registry as scenario_registry, _EXECUTORS
from .governance import school_conflicts
from .claim_capabilities import ready_bindings


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(root):
    """Include every tracked-area file; parse JSON instead of inferring from docs."""
    rows = []
    for area in ('data/canonical', 'data/quarantine'):
        for path in sorted((root / area).rglob('*'), key=lambda p: p.relative_to(root).as_posix()):
            if not path.is_file():
                continue
            row = {'path': path.relative_to(root).as_posix(), 'sha256': sha(path),
                   'bytes': path.stat().st_size, 'stage': area.split('/')[-1]}
            if path.suffix == '.json':
                obj = read_json(path)  # Bad JSON fails the audit; never silently skip it.
                row.update(json_type=type(obj).__name__)
                if isinstance(obj, dict):
                    row.update(domain=obj.get('domain'), model=obj.get('model'),
                               schema_version=obj.get('schema_version'))
            rows.append(row)
    return rows


def _references(obj, words, prefix=''):
    """Text hits are discovery pointers, never accepted Evidence or inference rules."""
    hits = []
    if isinstance(obj, str):
        present = [w for w in words if w in obj]
        if present:
            at = min(obj.index(w) for w in present)
            hits.append({'pointer': prefix or '/', 'matched_terms': present,
                         'excerpt': obj[max(0, at - 25):at + 100]})
    elif isinstance(obj, list):
        for i, child in enumerate(obj):
            hits.extend(_references(child, words, prefix + '/' + str(i)))
    elif isinstance(obj, dict):
        for key, child in obj.items():
            token = key.replace('~', '~0').replace('/', '~1')
            hits.extend(_references(child, words, prefix + '/' + token))
    return hits


def build_product_coverage(root: Path, *, rag_rows=None):
    root = Path(root).resolve()
    validate_protected_files(root)
    resolver = EvidenceResolver(root, review_sources=True)
    spec = read_json(root / 'config/product_requirements.json')
    scenarios = {s['id']: s for s in scenario_registry()}
    bundles = {b['domain']: b for b in resolver.model['bundles']}
    inv = inventory(root)
    by_path = {r['path']: r for r in inv}
    legacy = {r['path']: read_json(root / r['path']) for r in inv
              if r['stage'] == 'canonical' and r['path'].endswith('.json')
              and r.get('domain') in ('bazi', 'yinyuan', 'dream')}
    engines = {}
    for domain, contract in resolver.contracts.items():
        if PROVIDERS.get(domain) != contract['provider']:
            raise ValueError('Engine provider differs from execution contract')
        golden_path = f'data/canonical/{domain}/phase2_golden.json'
        golden = read_json(root / golden_path)
        cases = {c['id']: c for c in golden['cases']}
        if len(cases) != len(golden['cases']):
            raise ValueError('Duplicate Golden Case')
        rules = []
        for r in contract['rules']:
            refs = resolver.resolve(r['id'], contract['variant'])
            if not r['golden_case_ids'] or any(cid not in cases or cases[cid]['variant'] != r['variant'] for cid in r['golden_case_ids']):
                raise ValueError('Missing or incompatible Golden Case')
            if not (root / r['regression_test']).is_file():
                raise ValueError('Missing regression test')
            rules.append({**r, 'evidence': refs})
        engines[domain] = {'registered': True, 'provider': contract['provider'],
                           'variant': contract['variant'], 'scope': contract.get('scope'),
                           'unresolved': contract.get('unresolved', []), 'rules': rules,
                           'golden_path': golden_path, 'golden_ids': sorted(cases),
                           'test_execution': 'not_asserted_by_static_audit'}
    # Do not conflate calendar helpers / legacy operation references with registered engines.
    for domain in ('bazi', 'dream'):
        if domain in engines:
            continue
        engines[domain] = {'registered': domain in PROVIDERS,
                           'provider': PROVIDERS.get(domain), 'variant': None, 'rules': [],
                           'golden_ids': [], 'test_execution': 'unavailable'}

    topic_rows = {}
    for tid, t in spec['topics'].items():
        domain = t['domain']
        b = bundles.get(domain, {})
        names = set(t['terms'])
        terms = [e for e in b.get('terms', []) if e['name'] in names or names.intersection(e.get('aliases', []))]
        term_ids = {e['id'] for e in terms}
        rules = [e for e in b.get('rules', []) if term_ids.intersection(e.get('term_refs', []))]
        declared = t.get('execution_rules', [])
        known = {r['id'] for r in engines[domain]['rules']}
        if not set(declared) <= known:
            raise ValueError('Requirements mapping contains unknown execution Rule')
        legacy_paths = []
        for name in t['legacy_paths']:
            if name not in by_path:
                raise ValueError('Missing legacy reference')
            legacy_paths.append({'path': name, 'sha256': by_path[name]['sha256'],
                                 'usage': 'legacy_reference_not_explanation_authorization'})
        text_hits = []
        if domain == 'bazi':
            for name, obj in legacy.items():
                if not name.startswith('data/canonical/classics/bazi/'):
                    continue
                hits = _references(obj.get('sections', []), t['terms'])
                if hits:
                    text_hits.append({'path': name, 'sha256': by_path[name]['sha256'],
                                      'provenance': obj.get('provenance'), 'hit_count': len(hits),
                                      'examples': [{**hit, 'pointer': '/sections' + hit['pointer']} for hit in hits[:3]],
                                      'usage': 'text_discovery_only_not_reviewed_rule_evidence'})
        topic_rows[tid] = {'name': t['label'], 'priority': t['priority'], 'domain': domain,
                          'required_terms': t['terms'], 'reviewed_terms': [{'id': e['id'], 'name': e['name'], 'source_refs': e['source_refs']} for e in terms],
                          'terms_not_structured': [w for w in t['terms'] if not any(w == e['name'] or w in e.get('aliases', []) for e in terms)],
                          'phase1_rule_ids': [e['id'] for e in rules],
                          'phase1_execution_status': dict(Counter(e['execution_status'] for e in rules)),
                          'phase2_rule_ids': declared, 'legacy_references': legacy_paths,
                          'classical_text_candidates': text_hits,
                          'explanation_ready': False, 'missing': t['missing']}

    output = {}
    for pid, p in spec['products'].items():
        topics = [topic_rows[tid] for tid in p['topics']]
        scenario = scenarios.get(p['scenario_id']) if p['scenario_id'] else None
        if p['scenario_id'] and scenario is None:
            raise ValueError('Unknown Scenario in product mapping')
        dependencies = sorted({t['domain'] for t in topics})
        supported = []
        for d in dependencies:
            if engines[d]['registered']:
                rule_ids = sorted({rid for t in topics for rid in t['phase2_rule_ids'] if rid.startswith(d + '.')})
                if rule_ids:
                    supported.append({'kind': 'deterministic_structure', 'engine_id': d,
                                      'variant': engines[d]['variant'], 'rule_ids': rule_ids,
                                      'availability': 'existing_engine_and_structural_scenario_only'})
        claims = ready_bindings(p['scenario_id'], engines)
        if not supported and not claims:
            status = 'NOT_BUILT'
        elif pid in ('bazi-reading', 'romance', 'compatibility', 'one-question'):
            status = 'PRODUCTIZABLE'
        elif pid == 'life-overview':
            status = 'BLOCKED_ADVANCED'
        else:
            status = 'PARTIAL'
        claim_rows = {}
        for cid, binding in claims.items():
            rule_rows = [r for e in engines.values() for r in e['rules'] if r['id'] in binding['execution_rule_ids']]
            claim_rows[cid] = {**binding, 'status': 'READY',
                               'golden_case_ids': sorted({g for r in rule_rows for g in r['golden_case_ids']}),
                               'regression_tests': sorted({r['regression_test'] for r in rule_rows}),
                               'scenario_test': 'tests/test_scenario_engine.py',
                               'evidence': [ref for r in rule_rows for ref in r['evidence']],
                               'execution_validation': 'existing_phase2_validated_contract; static_audit_does_not_run_tests'}
        output[pid] = {'name': p['name'], 'status': status,
                       'scenario_id': p['scenario_id'], 'required_topics': p['topics'],
                       'supported_capabilities': supported,
                       'existing_knowledge': [{'topic_id': tid, 'legacy_files': len(topic_rows[tid]['legacy_references']),
                                               'text_candidate_files': len(topic_rows[tid]['classical_text_candidates']),
                                               'terms': len(topic_rows[tid]['reviewed_terms']),
                                               'phase1_rules': len(topic_rows[tid]['phase1_rule_ids']),
                                               'phase2_rules': len(topic_rows[tid]['phase2_rule_ids'])} for tid in p['topics']],
                       'missing_capabilities': [{'topic_id': tid, 'reason': topic_rows[tid]['missing']} for tid in p['topics']],
                       'ready_claims': sorted(claims), 'claim_capabilities': claim_rows,
                       'production_claims': sorted(claims), 'production_claims_scope': 'deterministic_structure_only',
                       'blocked_claims': p['blocked_claims'],
                       'missing_dependencies': [tid for tid in p['topics'] if topic_rows[tid]['missing']],
                       'full_interpretation_ready': False,
                       'public_enabled': bool(scenario and scenario['public_release']), 'ai_enabled': False,
                       'scenario_status': {'registered': scenario is not None,
                                           'runtime_implemented': bool(scenario and scenario['id'] in _EXECUTORS),
                                           'structural_public_release': bool(scenario and scenario['public_release']),
                                           'status': scenario['status'] if scenario else None,
                                           'scope': scenario['scope'] if scenario else None,
                                           'depends_on': scenario['depends_on'] if scenario else [],
                                           'ai_enabled': False},
                       'blockers': [t['missing'] for t in topics if t['missing']] + ['AI未完成真实质量校准及人工语义复核'],
                       'recommended_sources': sorted({ref['source_id'] for t in topics for e in t['reviewed_terms'] for ref in e['source_refs']} |
                                                     {ref['path'] for t in topics for ref in t['classical_text_candidates']}),
                       'degraded_message': '当前已实现的结构能力可供专业参考；该项深入解释仍在知识审核中。' if supported else '当前版本尚未开放，相关知识、规则与证据仍在校核中。'}
    chunks = list(iter_phase1_chunks(root, resolver.model))
    rag = rag_rows if rag_rows is not None else []
    source_registry = read_json(root / 'config/source_registry.json')
    source_audit = read_json(root / 'config/phase2_source_audit.json')
    editorial_flags = []
    for name, obj in legacy.items():
        for i, section in enumerate(obj.get('sections', [])):
            markers = [m for m in ('若思按', '若思注', '(新增)') if m in section.get('text', '')]
            if markers:
                editorial_flags.append({'path': name, 'pointer': f'/sections/{i}/text',
                                        'title': section.get('title'), 'markers': markers,
                                        'status': 'edition_and_attribution_review_required',
                                        'note': '编者/增补标记须逐段核版本与权利，不能按整本公版标签自动成为原典Evidence。'})
    api_routes = []
    for node in ast.walk(ast.parse((root / 'src/tianji_kb/api.py').read_text(encoding='utf-8'))):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for dec in node.decorator_list:
                if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute) and dec.func.attr in ('get', 'post') and dec.args and isinstance(dec.args[0], ast.Constant):
                    api_routes.append({'method': dec.func.attr.upper(), 'path': dec.args[0].value, 'handler': node.name})
    staged = [read_json(root / row['path']) for row in inv if row['path'].startswith('data/quarantine/phase1_candidates/') and row['path'].endswith('.json')]
    sanming = next(w for s in read_json(root / 'config/public_domain_manifest.json')['sources']
                   for w in s['works'] if w['id'] == 'sanming_tonghui')
    if sanming['promotion'] != 'quarantine_only' or sanming['quality_blockers']['canonical_ready'] is not False or (root / sanming['planned_output']).exists():
        raise ValueError('Sanming isolation violated')
    controls = ['config/source_registry.json', 'config/source_file_manifest.json', 'config/knowledge_sources.json',
                'config/domain_registry.json', 'config/phase2_source_audit.json', 'config/phase2_rule_promotions.json',
                'config/public_domain_manifest.json', 'config/product_requirements.json']
    controls += [p.relative_to(root).as_posix() for p in sorted((root / 'src/tianji_kb').rglob('*.py'))]
    controls += [p.relative_to(root).as_posix() for p in sorted((root / 'schemas/knowledge').glob('*.json'))]
    controls += [p.relative_to(root).as_posix() for p in sorted((root / 'tests').glob('test_phase*.py'))]
    output['_audit'] = {'schema_version': '1.0', 'artifact_kind': 'derived_product_knowledge_audit',
                         'knowledge_model': 'existing_phase1_and_phase2_unchanged',
                         'publication_authority': False,
                         'input_files': inv + [{'path': p, 'sha256': sha(root / p)} for p in sorted(controls)],
                         'inventory_counts': dict(Counter(r['stage'] for r in inv)),
                         'legacy_source_registry_count': len(source_registry['sources']),
                         'source_metadata_gaps': {'edition_not_explicit': sorted(sid for sid, s in resolver.sources.items() if not s.get('edition')),
                                                  'note': '现有schema没有edition字段；书名/era不等于底本已核，不增加旁路来源模型。'},
                         'legacy_trust_level_warning': 'source_registry trust_level A/B是旧来源采纳等级，不能换算成原典独立证据A/B；实现材料按D处理。',
                         'knowledge_sources': [{k: s[k] for k in ('source_id', 'kind', 'evidence_level', 'repository', 'path', 'commit', 'license', 'public_domain', 'rights_basis', 'sha256')} for s in resolver.sources.values()],
                         'source_grades': dict(Counter(s['evidence_level'] for s in resolver.sources.values())),
                         'phase1': {d: {key: len(b[key]) for key in ('classics', 'chapters', 'sections', 'terms', 'rules', 'concepts')} for d, b in bundles.items()},
                         'engines': engines, 'topics': topic_rows,
                         'conflict_entities': school_conflicts(resolver),
                         'conflict_status': '沿用既有 governance.school_conflicts：' + '；'.join(c['name'] + '=' + c['status'] for c in school_conflicts(resolver)) + '。保留 Rule difference/exceptions、执行 unresolved 与来源审计。',
                         'source_comparisons': source_audit['claim_comparisons'],
                         'rule_promotions': read_json(root / 'config/phase2_rule_promotions.json')['promotions'],
                         'editorial_review_flags': editorial_flags,
                         'api_routes': sorted(api_routes, key=lambda x: (x['path'], x['method'])),
                         'staged_source_candidates': staged,
                         'retrieval': {'reviewed_entity_chunks': len(chunks),
                                       'general_rag_chunks': len(rag) if rag_rows is not None else None,
                                       'general_rag_domains': dict(Counter(r['metadata']['domain'] for r in rag)),
                                       'warning': '通用RAG包括旧Canonical资料；可检索不等于RuleMatch命中或解释授权。生产解释仍用现有CanonicalRetriever及EvidenceResolver。'},
                         'scenario_count': len(scenarios), 'sanming': sanming['quality_blockers'],
                         'reviewed_knowledge_batch': [
                             {'entity_id': eid, 'collection': resolver.entities[eid][0]}
                             for eid in ('bazi.chapter.zhiming_boundary', 'bazi.section.s022', 'bazi.term.strength_review_boundary', 'bazi.rule.r012')
                             if eid in resolver.entities],
                         'conditional_strength_variants': {cid: resolver.entities[cid][1]['attributes']
                             for cid in ('bazi.concept.month_command_variant_v1',
                                         'bazi.concept.root_conditions_variant_v1') if cid in resolver.entities},
                         'bounded_strength_factors': resolver.entities.get('bazi.concept.strength_factor_variant_v1', (None, {}))[1].get('attributes', {})}
    return output


def dependency_report(report, spec):
    """Derived product requirements DAG; not a Rule/Evidence source."""
    edges = spec['topic_dependencies']
    visiting, done = set(), set()
    def visit(tid):
        if tid not in spec['topics']:
            raise ValueError('Unknown dependency topic')
        if tid in visiting:
            raise ValueError('Knowledge dependency cycle')
        if tid in done:
            return
        visiting.add(tid)
        for parent in edges.get(tid, []):
            visit(parent)
        visiting.remove(tid)
        done.add(tid)
    for tid in spec['topics']:
        visit(tid)
    return {'artifact_kind': 'derived_product_dependency_graph', 'knowledge_authority': False,
            'scope': 'advanced_interpretation_requirements; existing structural claims do not require every advanced module',
            'topics': {tid: {'name': t['label'], 'depends_on': edges.get(tid, []),
                             'ready_execution_rule_ids': report['_audit']['topics'][tid]['phase2_rule_ids'],
                             'missing': t['missing']} for tid, t in spec['topics'].items()},
            'products': {pid: {'required_topics': p['required_topics'], 'ready_claims': p['ready_claims'],
                               'missing_dependencies': p['missing_dependencies']} for pid, p in report.items() if not pid.startswith('_')}}


def markdown_report(report):
    a = report['_audit']
    lines = ['# 产品知识覆盖与缺口', '',
             '由既有来源、Phase1/Phase2、Golden 与 Scenario 派生。报告不是知识库或发布授权；`--check` 检查漂移。', '',
             'READY 表示指定结构 claim 的执行契约、证据、Golden 和测试绑定齐全；PRODUCTIZABLE 表示可做有限结构产品；PARTIAL 表示仍缺关键解释；BLOCKED_ADVANCED 表示聚合基础可用但高级解释受阻；NOT_BUILT 表示没有对应执行链。静态审计不冒充测试执行。', '',
             '| 产品 | 状态 | 已接入的结构 claim 数 | 现有结构公开标志 |', '|---|---|---:|---|']
    for pid, p in report.items():
        if not pid.startswith('_'):
            lines.append(f"| {p['name']} | {p['status']} | {len(p['ready_claims'])} | {p['public_enabled']} |")
    lines += ['', '能力逐项追踪、原典定位与下一批工作见 [KNOWLEDGE_CAPABILITY_MAP.md](KNOWLEDGE_CAPABILITY_MAP.md)。依赖图见 `data/product/knowledge_dependencies.json`。', '',
              f"现有 {sum(e['registered'] for e in a['engines'].values())} 个确定性引擎；{sum(len(e['rules']) for e in a['engines'].values())} 条 Phase2 Rule；{sum(len(e['golden_ids']) for e in a['engines'].values())} 个 Golden。",
              f"证据来源等级 {json.dumps(a['source_grades'], ensure_ascii=False)}。GitHub 实现参考不能成为古籍证据；通用 RAG 可检索不代表已授权推断。", '',
              '结构 claim 由实际 RuleMatch facts 绑定，并核对 Variant、当前 Golden 和逐字 Evidence。不得升级为吉凶、适配分、婚期或财富保证。AI 质量尚未批准，结构可用与 AI 放行分别检查。', '',
              '## 既有治理与开发顺序', '',
              'Source → RAW → Quarantine → Review → Canonical → Terms/Rules → Evidence → Variant/Conflict → Golden → Phase2 → Scenario。沿用现有 schema、来源登记、晋级记录和校验器，禁止另建旁路知识库。',
              '暂停公开页面开发。保留十一产品入口、古风视觉、背景音乐播放/暂停/音量/路由持续播放、后台静音与山水云雾水墨动画需求，待底层阶段验收后实施。',
              '每批一个专题：基础/月令/通根/透干 → 单一旺衰 Variant → 核心格局 → 喜用体系分别治理 → 大运/流年作用 → 婚恋/事业/双人条件解释。梦境来源审查可独立开展，传统与现代心理证据分开。', '',
              '## 冲突和隔离', '', a['conflict_status'],
              '《三命通会》维持 quarantine_only / canonical_ready=false；PUA 完成不代表整本可晋级。原始 snapshot 不改动。', '',
              '## 来源与待审材料', '']
    for row in a['staged_source_candidates']:
        lines.append(f"- `{row['source_path']}` @ `{row['candidate_commit']}`：整本 pending，Quarantine，不能因下载而晋级。")
    for row in a['editorial_review_flags']:
        lines.append(f"- `{row['path']}#{row['pointer']}` 含 {'、'.join(row['markers'])}：逐段排除未审核现代注释。")
    lines += ['', '知命前段新增描述性规则 `bazi.rule.r012` 只禁止机械套财官食印，没有编造旺衰算法或权重。后续 executable 仍须独立完成证据、反例与测试。', '']
    return '\n'.join(lines)


def capability_map(report):
    a = report['_audit']
    lines = ['# 产品知识能力图', '',
             '范围按已实现的 Scenario 与确定性引擎区分。结构事实可用不等于完整预测、前台发布或 AI 校准完成。所有条目由现有注册项派生，不另建知识模型。', '']
    for pid, p in report.items():
        if pid.startswith('_'):
            continue
        s = p['scenario_status']
        lines += [f"## {p['name']} · {p['status']}", '',
                  f"Scenario：`{p['scenario_id']}`；已执行={s['runtime_implemented']}；现有结构公开标志={s['structural_public_release']}；AI=false。", '',
                  '已有知识、Rule 与 Evidence：', '']
        for tid in p['required_topics']:
            t = a['topics'][tid]
            lines.append(f"- {t['name']}：Terms {', '.join('`'+r['id']+'`' for r in t['reviewed_terms']) or '尚无对应审核术语'}；Phase1 Rule {', '.join('`'+r+'`' for r in t['phase1_rule_ids']) or '尚无对应审核规则'}。")
        lines += ['', '已有 Phase2 / Golden / Variant：', '']
        for cap in p['supported_capabilities']:
            for r in a['engines'][cap['engine_id']]['rules']:
                if r['id'] not in cap['rule_ids']:
                    continue
                lines.append(f"- `{r['id']}` / `{r['variant']}`；Golden：{', '.join('`'+g+'`' for g in r['golden_case_ids'])}；测试 `{r['regression_test']}`。")
                for ref in r['evidence']:
                    lines.append(f"  Evidence {ref['evidence_level']}：`{ref['source_id']}` / {ref['classic_title']} / {ref['chapter_title']} / `{ref['locator']}`，引文：{ref['original_text']}。")
        lines += ['', '当前场景可输出结论（只描述事实，不追加吉凶含义）：', '']
        lines += [f"- `{cid}`：READY；匹配 `{c['match_rule_id']}`，事实路径 `{c['fact_path'] or '/'}`；{c['scope']}。" for cid, c in p['claim_capabilities'].items()] or ['- 无已接入的结构 claim；引擎能力如上，场景接线须另审。']
        for cid, c in p['claim_capabilities'].items():
            if c.get('required_input_option'):
                lines.append(f"  `{cid}` 仅在显式输入 `{json.dumps(c['required_input_option'], ensure_ascii=False)}` 且对应 RuleMatch 实际执行时可用。")
        if pid == 'romance':
            lines += ['- 引擎另有配偶宫、传统配偶星 lens、五合/六合/六害/六冲/三合；当前 romance 只接咸池，这些其他能力已在 compatibility 接入，不能宣称 romance 已输出。']
        lines += ['', '当前禁止结论：' + '；'.join(p['blocked_claims']) + '。', '', '缺失能力 / 依赖 / 下一批：', '']
        for tid in p['missing_dependencies']:
            t = a['topics'][tid]
            lines.append(f"- `{tid}`：{t['missing']}")
            if t['classical_text_candidates']:
                ref = t['classical_text_candidates'][0]
                ex = ref['examples'][0]
                lines.append(f"  下一批从 `{ref['path']}#{ex['pointer']}` 核短引、条件和反例；全文命中仅是待审定位，不是 Evidence。")
            elif t['reviewed_terms']:
                refs = sorted({ref['source_id'] for term in t['reviewed_terms'] for ref in term['source_refs']})
                lines.append(f"  下一批复核现有 {', '.join('`'+sid+'`' for sid in refs)}，沿原模型补规则条件及 Golden。")
            else:
                lines.append('  下一批先登记来源及权利，保存 RAW/Quarantine；无审核引文时保持未支持。')
        lines += ['']
    return '\n'.join(lines)
