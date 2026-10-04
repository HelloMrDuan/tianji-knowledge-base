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
        output[pid] = {'name': p['name'], 'status': 'partial' if supported or any(t['legacy_references'] or t['reviewed_terms'] for t in topics) else 'missing',
                       'scenario_id': p['scenario_id'], 'required_topics': p['topics'],
                       'supported_capabilities': supported,
                       'existing_knowledge': [{'topic_id': tid, 'legacy_files': len(topic_rows[tid]['legacy_references']),
                                               'text_candidate_files': len(topic_rows[tid]['classical_text_candidates']),
                                               'terms': len(topic_rows[tid]['reviewed_terms']),
                                               'phase1_rules': len(topic_rows[tid]['phase1_rule_ids']),
                                               'phase2_rules': len(topic_rows[tid]['phase2_rule_ids'])} for tid in p['topics']],
                       'missing_capabilities': [{'topic_id': tid, 'reason': topic_rows[tid]['missing']} for tid in p['topics']],
                       'production_claims': [], 'blocked_claims': p['blocked_claims'],
                       'production_ready': False, 'public_enabled': False, 'ai_enabled': False,
                       'scenario_status': {'registered': scenario is not None,
                                           'runtime_implemented': bool(scenario and scenario['id'] in _EXECUTORS),
                                           'structural_public_release': bool(scenario and scenario['public_release']),
                                           'status': scenario['status'] if scenario else None,
                                           'scope': scenario['scope'] if scenario else None,
                                           'depends_on': scenario['depends_on'] if scenario else [],
                                           'ai_enabled': False},
                       'blockers': ['所需解释模块尚无产品级审核授权', 'AI未完成真实质量校准及人工语义复核',
                                    '已实现结构Scenario不等于运势/占断；完整解释与发布绑定尚未完成'],
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
                         'conflict_status': '沿用既有governance.school_conflicts：传统配偶星口径已限定范围，三刑争议未解决；Rule difference/exceptions、执行unresolved与来源审计继续保留。',
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
                         'new_execution_promotions': 0}
    return output


def markdown_report(report):
    a = report['_audit']
    lines = ['# 测算产品 × 知识库覆盖及缺口', '',
             '由 `scripts/build_product_coverage.py` 扫描实际 JSON、来源、执行契约、Golden、代码和 RAG 自动生成。运行 `--check` 检查漂移。', '',
             '这是现有知识库的派生报告，不是新知识模型、Rule 或上线授权。所有产品解释均未开放；结构计算与完整测算报告分开评估。', '',
             f"实际文件：Canonical {a['inventory_counts']['canonical']}，Quarantine {a['inventory_counts']['quarantine']}；来源登记 {a['legacy_source_registry_count']}；逐项证据来源 {len(a['knowledge_sources'])}。",
             f"已注册确定性引擎 {sum(e['registered'] for e in a['engines'].values())} 个，Phase2 Rule {sum(len(e['rules']) for e in a['engines'].values())} 条，Golden {sum(len(e['golden_ids']) for e in a['engines'].values())} 个；八字结构已注册，梦境未建立。",
             f"证据等级 {json.dumps(a['source_grades'], ensure_ascii=False)}；旧 registry trust_level A/B 不等于独立古典 Evidence A/B。",
             f"RAG：已审核实体 {a['retrieval']['reviewed_entity_chunks']} 块；通用 {a['retrieval']['general_rag_chunks']} 块，含旧资料，不能代替执行命中。", '',
             '| 产品 | 所需专题 | 已有 | 缺失/阻塞 | 完整产品可生产 |',
             '|---|---|---|---|---|']
    for pid, p in report.items():
        if pid.startswith('_'):
            continue
        supported = ', '.join(s['engine_id'] + '结构' for s in p['supported_capabilities'])
        if not supported:
            supported = '旧表/正文候选' if p['status'] == 'partial' else '未建立'
        lines.append(f"| {p['name']} | {'、'.join(a['topics'][tid]['name'] for tid in p['required_topics'])} | {supported} | 缺产品解释及门控链路，详见下文 | 否 |")
    lines += ['', '## 现有治理路径', '',
              '补库只走已有 Source → RAW → Quarantine → Review → Canonical → Terms/Rules → Evidence → Variant/Conflict → Golden → Phase2 → Scenario。',
              '使用 `config/source_registry.json` / `source_file_manifest.json` / `public_domain_manifest.json` 的既有采纳范围；固定来源通过 `stage_phase1_sources.py` / `acquisition.stage_candidate` 隔离。',
              '现有七域（包括八字）`phase1_knowledge.json` 与 `knowledge_sources.json` 使用既有 schema / `validate_knowledge`；Phase2 用既有执行、补充证据、来源审计、晋级记录、Golden 和 `validate_phase2.py`。',
              '八字结构与条件化配偶星口径已接入同一模型；梦境尚未接入。补库必须沿用既有模型及校验，不另外造知识结构；本批不修改 schema、不自动晋级。', '',
              '## 迭代顺序与小批量验收', '',
              'P0：八字基础/十神 → 旺衰（先选并核单一 Variant）→ 格局 → 四套喜用体系分别治理 → 大运/流年 → 婚恋/事业财富 → 双人关系；梦境来源审查可独立进行。',
              'P1：六爻解释深化、流月、流日、人生聚合；P2：紫微、奇门、六壬、风水扩展、周易专业。',
              '首批优先复核现有《滴天髓阐微》知命/夫妻/女命、《渊海子平》月令/大运及《穷通宝鉴》月令材料。先抽少量原文与限制，保存反例；不得从整本存在直接推规则已审核。',
              '每批只处理一个明确条件关系及反例：检查来源权利/版本/字面 → 已有模型引用 → 命名 Variant 与适用边界 → 固定 Golden/反例 → 测试 → 执行晋级记录；缺任何一步继续隔离。',
              '六爻优先复用已登记《增删卜易》《卜筮正宗》；专业域优先复用下列真实 source_id。梦境当前无已登记专库，先做来源/权利审核，不能借命理语料或模型先验填充。', '',
              '## 结论能力门控', '',
              '`product_claims.py` 复用 EvidenceResolver、现有 explanation_policy 和 validate_reply；检查事实存在、可执行 Rule、Golden、等级/Variant、来源冲突。产品入口在模型调用前拒绝尚未审核的完整解释。现有结构API继续按原范围工作。',
              '完整产品授权/claim白名单与模型人工复核绑定契约尚未实现；当前不接受改几个布尔值作为发布授权。此门控保持关闭，不宣称已完成全部生产放行能力。',
              '当前全部 `production_claims=[]`，公开解释一律拒绝。新 Prompt v3 明示 “Absence of knowledge is not permission to use model prior knowledge.”；旧 v1/v2 保持不可变，仅供既有评测比较。',
              '自由文本的语义蕴涵不能只靠 JSON/关键词证明；现有人工语义审核仍是必要步骤，门控测试不等于模型质量达标。', '',
              '## 冲突与隔离边界', '', a['conflict_status'],
              '《三命通会》保持 quarantine_only / canonical_ready=false；原始 snapshot、已确认 PUA/OCR 映射未修改，不能进入 Canonical/RAG。', '',
              '## 实查现有模型', '', '| 域 | Classics | Chapters | Sections | Terms | Rules | Concepts |', '|---|---:|---:|---:|---:|---:|---:|']
    for d, counts in a['phase1'].items():
        lines.append('| ' + d + ' | ' + ' | '.join(str(counts[k]) for k in ('classics', 'chapters', 'sections', 'terms', 'rules', 'concepts')) + ' |')
    lines += ['', '## 首批来源隔离及编辑标记审核', '',
              '已按现有 `acquisition.stage_candidate` 保存以下固定来源的 RAW（忽略缓存）及 Quarantine 元数据；Git blob校验通过，整本review_status=pending，promotion_allowed=false。仅知命前段单独审核后入既有Phase1模型，整本不晋级，来源等级不变。', '']
    lines += ['- `' + row['source_path'] + '` @ `' + row['candidate_commit'] + '`，blob `' + row['blob_sha'] + '`。' for row in a['staged_source_candidates']]
    lines += ['', '原典审核前须处理下列编者/增补标记（定位到实际 JSON；不自动删改旧文件）：', '']
    lines += ['- `' + row['path'] + '#' + row['pointer'] + '`：' + '、'.join(row['markers']) + '。' for row in a['editorial_review_flags']]
    lines += ['', f"现有来源 schema 未显式包含 edition；{len(a['knowledge_sources'])}条来源的 edition 不可从书名推定。版本核验仍按现有来源审计记录，正式扩展应保持同一治理模型。", '',
              '实查 API：' + '；'.join(row['method'] + ' `' + row['path'] + '`' for row in a['api_routes']) + '。已有真实Scenario执行与后台只读治理 API；历史记录与管理写入尚未完成。']
    for pid, p in report.items():
        if pid.startswith('_'):
            continue
        lines += ['', '## ' + p['name'], '', '已有：', '']
        state = p['scenario_status']
        if state['registered']:
            lines.append(f"- 现有 Scenario `{p['scenario_id']}`：{state['status']}，结构执行={state['runtime_implemented']}，结构公开标志={state['structural_public_release']}；{state['scope']}")
        for tid in p['required_topics']:
            t = a['topics'][tid]
            lines.append(f"- {t['name']}：术语 {len(t['reviewed_terms'])}，关联 Phase1 Rule {len(t['phase1_rule_ids'])}，列入结构映射的 Phase2 Rule {len(t['phase2_rule_ids'])}。")
            for ref in t['legacy_references']:
                lines.append(f"  旧资料 `{ref['path']}`（实现/描述参考，未授权解释）。")
            for ref in t['classical_text_candidates']:
                example = ref['examples'][0]
                lines.append(f"  原文候选 `{ref['path']}#{example['pointer']}`；{ref['hit_count']} 个字段命中，仅作待审查定位。")
        lines += ['', '缺失：', ''] + [f"- {a['topics'][tid]['name']}：{a['topics'][tid]['missing']}" for tid in p['required_topics']]
        lines += ['', '阻塞：', ''] + ['- ' + reason for reason in p['blockers']]
        lines += ['', '禁止结论：' + '；'.join(p['blocked_claims']) + '。', '', '推荐复核来源（本地已存在；不因列在这里自动升 Evidence）：', '']
        lines += ['- `' + s + '`' for s in p['recommended_sources']] or ['- 当前无已审核专属来源；先来源登记与 Quarantine，不编造书名/摘录。']
        lines += ['', '前台降级：' + p['degraded_message']]
    lines += ['', '## 本批范围及未完成项', '',
              '本批完成实查报告、两部既有来源的隔离复核候选、知命前段一条描述性解释边界及失败即拒绝的产品解释门控；未新增可执行推断、未开放产品、未上线 AI。',
              '新增 `bazi.rule.r012`、`bazi.term.strength_review_boundary`、`bazi.section.s022` 与章节均沿用既有模型。规则保持descriptive_only，不参与执行RuleMatch，不伪造算法或Golden；已有34个结构Golden保留，解释性Golden与Phase2编译继续阻塞。',
              '八字旺衰/格局/喜用/岁运解释治理、独立梦境资料、解释性 Golden、产品授权与模型质量校准仍须按上述批次完成。', '']
    return '\n'.join(lines)
