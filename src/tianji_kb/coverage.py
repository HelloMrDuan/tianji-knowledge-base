"""Deterministic registered-domain coverage; book-body counts do not imply full collation."""
from __future__ import annotations

import ast
from collections import Counter
from pathlib import Path

from .knowledge import validate_knowledge, validate_protected_files
from .knowledge_index import iter_phase1_chunks

PENDING = {
    'yijing': ['C 为可追溯电子本；十翼复用旧正式全文，不声明新刊本校勘。'],
    'liuyao': ['旺衰及日月条件、墓绝刑害等仍需分流派编译。'],
    'qimen': ['精确节气转盘单一 variant；置闰/超接及其他盘法未实现。'],
    'ziwei': ['壬年府/辅疑字待刊本；四化、亮度、长生及完整排盘仍保留版本差异。'],
    'fengshui': ['1864锚点/20年九运年份表为 D，显式研究模式；古籍与时间边界待核。'],
    'liuren': ['九宗门初传分支未完整编译；贵人两表及天后位置异文待逐句核定。'],
    'bazi': ['生产范围含四柱、日主、十神、藏干；咸池、五合/六合/六害/六冲/三合、日支传统配偶宫结构位及用户显式选择的传统配偶星候选位置已核；三刑存在流派分歧，跨盘三合、旺衰、格局、喜用、调候、大运起运及婚恋解释尚未裁定。'],
}


def build_coverage(root: Path) -> dict:
    validate_protected_files(root)
    model = validate_knowledge(root)
    chunks = list(iter_phase1_chunks(root, model))
    report = {'schema_version': '1.0', 'scope': '七域最小完整骨架；不等于完整排盘、占断或整本校勘', 'domains': []}
    for bundle in model['bundles']:
        domain = bundle['domain']
        source_ids = set()
        for classic in bundle['classics']:
            source_ids.update([classic['source_id']] + classic.get('source_ids', []))
        for collection in ('sections', 'terms', 'rules', 'concepts'):
            for entity in bundle[collection]:
                source_ids.update(r['source_id'] for r in entity.get('source_refs', []))
                operation = entity.get('operation', {})
                if operation.get('source_id'):
                    source_ids.add(operation['source_id'])
                if operation.get('parameters', {}).get('calendar_source_id'):
                    source_ids.add(operation['parameters']['calendar_source_id'])
        grades = Counter(model['sources'][sid]['evidence_level'] for sid in source_ids)
        bodies = Counter(c['body_stage'] for c in bundle['classics'])
        tests = root / f'tests/test_phase1_{domain}.py'
        test_count = sum(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith('test_') for node in ast.walk(ast.parse(tests.read_text()))) if tests.exists() else 0
        indexed = [c for c in chunks if c['metadata']['domain'] == domain]
        criteria = {
            'domain_definition': domain in model['domains'],
            'source_registry': bool(source_ids),
            'reviewed_core_material': bool(bundle['sections']),
            'terms': bool(bundle['terms']), 'structured_rules': bool(bundle['rules']),
            'resolved_evidence': all(c['metadata']['source_refs'] for c in indexed),
            'domain_tests': test_count > 0, 'coverage_report': True,
            'production_isolation': bool(indexed) and all(c['metadata']['canonical_path'].startswith(f'data/canonical/{domain}/') for c in indexed),
        }
        rules = Counter(r['execution_status'] for r in bundle['rules'])
        report['domains'].append({
            'domain': domain, 'name': model['domains'][domain]['name'],
            'classics': {
                'canonical': bodies['canonical'], 'quarantine': bodies['quarantine'],
                'metadata_only': bodies['metadata_only'],
                'with_reviewed_excerpts': len({s['classic_id'] for s in bundle['sections']}),
            },
            'chapters': len(bundle['chapters']), 'sections': len(bundle['sections']),
            'terms': {'canonical': len(bundle['terms'])}, 'concepts': len(bundle['concepts']),
            'rules': {s: rules[s] for s in ('executable', 'partially_structured', 'descriptive_only')},
            'sources': {g: grades[g] for g in 'ABCD'}, 'source_ids': sorted(source_ids),
            'tests': test_count, 'production_chunks': len(indexed),
            'completion_criteria': criteria, 'pending_evidence': PENDING[domain],
            'status': 'phase1_complete' if all(criteria.values()) else 'in_progress',
        })
    return report


def markdown_coverage(report: dict) -> str:
    lines = [
        '<!-- PHASE1_COVERAGE_START -->', '## 七域横向扩充 Phase 1', '',
        '完成状态按本轮九项最小骨架标准核验；不等于所有流派算法、整本校勘或完整占断已完成。',
        '机器报告：`data/coverage/phase1.json`；运行 `python scripts/build_phase1_coverage.py --check` 检查统计一致。', '',
        '| 域 | 经典正文正式/隔离 | 已核选段 | 术语 | 规则：执行/部分/描述 | 来源：A/B/C/D | 状态 |',
        '|---|---:|---:|---:|---:|---:|---|',
    ]
    for d in report['domains']:
        c = d['classics']; r = d['rules']; s = d['sources']
        lines.append(f"| {d['domain']} | {c['canonical']}/{c['quarantine']} | {d['sections']} | {d['terms']['canonical']} | {r['executable']}/{r['partially_structured']}/{r['descriptive_only']} | {s['A']}/{s['B']}/{s['C']}/{s['D']} | {d['status']} |")
    lines += ['',
        '经典正式/隔离按 `body_stage` 分开计数；隔离经典也可拥有逐段审核通过的正式短引，',
        '并不表示其整本已晋级。经典实体包括《周易》《易传》等传世文献单元，',
        '不把64份卦文文件计作64部书。来源计数是引用记录数，周易的逐卦文件来自同一整理项目，',
        '不能据文件数量升为多个独立版本的 A/B 证据。D 仅为实现、日历辅助来源，',
        '保留于隔离区；新增核心实体的经典引用全部为 C。旧 Canonical 实现不因本轮注册被提升证据等级。', '',
        '默认 RAG 与新增 `build/phase1_knowledge.jsonl` 逐实体索引只加载 Canonical；',
        '引用可指向隔离区的固定证据文件作审计，索引只包含已审查的正式选段与实体，',
        '不会加载隔离正文、候选异文或三元九运 D 级研究表。', '',
        '待核事项：', '',
    ]
    lines += [f"- {d['domain']}：{'；'.join(d['pending_evidence'])}" for d in report['domains']]
    lines += ['', 'Phase 1 至此收束。后续先评估七域覆盖，再决定 Phase 2 优先级；不自动继续深挖单书。', '<!-- PHASE1_COVERAGE_END -->']
    return '\n'.join(lines) + '\n'
