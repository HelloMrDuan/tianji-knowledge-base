"""Fixed-suite regression: structural scores are not semantic quality certification."""
import asyncio,copy,json,statistics
from pathlib import Path
from .engine import execute
from .explanation import ExplanationService,ExplanationFailure,validate_reply,validate_citations
from .prompts import get_prompt
from .resolver import ROOT
from .runtime_catalog import digest

SUITE_PATH=ROOT/'evals/explanations/cases-v1.json'
DIMENSIONS=('chart_fidelity','rule_fidelity','citation_validity','evidence_grounding',
            'variant_consistency','hallucination_rate','unsupported_claim_rate',
            'contradiction_rate','explanation_completeness')
KINDS={'deterministic_fact','rule_match','classical_evidence','synthesis','uncertainty'}

def contains(actual,expected):
    if isinstance(expected,dict):
        return isinstance(actual,dict) and all(k in actual and contains(actual[k],v) for k,v in expected.items())
    if isinstance(expected,list):
        return isinstance(actual,list) and len(actual)==len(expected) and all(contains(a,b) for a,b in zip(actual,expected))
    return digest(actual)==digest(expected)

def load_suite(path=SUITE_PATH):
    suite=json.loads(Path(path).read_text())
    ids=set()
    for case in suite['cases']:
        if case['id'] in ids:raise ValueError('Duplicate eval case ID')
        ids.add(case['id'])
        if 'golden_ref' in case:
            ref=case['golden_ref'];golden=json.loads((ROOT/ref['path']).read_text())
            if digest(golden)!=ref['sha256']:raise ValueError('Golden oracle changed; explicit suite review required')
            match=next(c for c in golden['cases'] if c['id']==ref['id'])
            if match['expected']!=case['expected_chart_subset']:raise ValueError('Golden expectations differ')
    return suite

def execute_case(case):
    inputs=copy.deepcopy(case['input'])
    if 'research' in inputs:raise ValueError('Use eval mode, not input.research')
    if case['domain']=='fengshui' and case['mode']=='research' and inputs.get('year') is not None:inputs['research']=True
    raw=execute(case['domain'],inputs,case['variant'],allow_research=case['mode']=='research')
    if case['expected']=='explanation':
        if digest(raw['result'])!=case['expected_chart_sha256'] or not contains(raw['result'],case.get('expected_chart_subset',{})):
            raise RuntimeError('Engine oracle drift; do not adjust engine to improve explanation score')
        if [r['rule_id'] for r in raw['rule_matches']]!=case['expected_rule_ids']:raise RuntimeError('Rule oracle drift')
    if case.get('context_fault')=='no_evidence':raw['evidence']={}
    if case.get('context_fault')=='source_conflict':raw['source_conflicts']=[{'status':'unresolved','scope':'eval injected source conflict'}]
    return raw

def score_reply(reply,context):
    """Measure verifiable fields; free-prose entailment still requires human review."""
    claims=reply.get('claims',[]) if isinstance(reply,dict) else []
    claims=[c for c in claims if isinstance(c,dict)] if isinstance(claims,list) else []
    facts=context['facts'];evidence=context['evidence'];rules={r['rule_id']:r for r in context['rules']}
    fact_checks=[];rule_checks=[];citation_checks=[];ground_checks=[];hallucinations=0;contradictions=0;hallucinated_claims=0;contradictory_claims=0;variant_claim_error=False
    for claim in claims:
        before=hallucinations;before_contradictions=contradictions
        pointer=claim.get('fact_ref');valid_fact=isinstance(pointer,str) and pointer in facts and digest(claim.get('fact_value'))==digest(facts[pointer])
        fact_checks.append(valid_fact)
        if not valid_fact:hallucinations+=1;contradictions+=1
        ids=claim.get('rule_ids',[]);ids=ids if isinstance(ids,list) else []
        valid_rules=bool(ids) and all(isinstance(r,str) and r in rules for r in ids)
        rule_checks.append(valid_rules)
        hallucinations+=sum(not isinstance(r,str) or r not in rules for r in ids)
        refs=claim.get('evidence_ids',[]);refs=refs if isinstance(refs,list) else []
        valid_refs=bool(refs) and all(isinstance(e,str) and e in evidence for e in refs)
        citation_checks.extend(isinstance(e,str) and e in evidence for e in refs)
        hallucinations+=sum(not isinstance(e,str) or e not in evidence for e in refs)
        quotes=claim.get('quotes',[]);quotes=quotes if isinstance(quotes,list) else []
        valid_quotes=bool(quotes)
        for quote in quotes:
            ok=isinstance(quote,dict) and isinstance(quote.get('evidence_id'),str) and quote['evidence_id'] in evidence and isinstance(quote.get('text'),str) and bool(quote['text'].strip()) and quote['text'] in evidence[quote['evidence_id']]['original_text']
            citation_checks.append(ok);valid_quotes=valid_quotes and ok;hallucinations+=not ok
        allowed={e for r in ids if isinstance(r,str) and r in rules for e in rules[r]['evidence_ids']}
        ground_checks.append(valid_fact and valid_rules and valid_refs and valid_quotes and set(refs)<=allowed)
        try:validate_citations(claim,evidence)
        except (ExplanationFailure,KeyError,TypeError):
            citation_checks.append(False);ground_checks[-1]=False;hallucinations+=1
        if 'explanation_policy' in context:
            from .explanation_policy import validate_claim_policy
            try:validate_claim_policy(claim,context)
            except ExplanationFailure as error:
                ground_checks[-1]=False
                if error.code in ('unmatched_rule_claim','rule_fact_binding_mismatch'):rule_checks[-1]=False
                if error.code=='variant_policy_mismatch':variant_claim_error=True
                if error.code=='chart_text_contradiction':fact_checks[-1]=False;contradictions+=1
                if error.code in ('unsupported_certainty','out_of_scope_claim','variant_policy_mismatch','chart_text_contradiction'):hallucinations+=1
            except (KeyError,TypeError):ground_checks[-1]=False
        hallucinated_claims+=hallucinations>before
        contradictory_claims+=contradictions>before_contradictions
    valid_variant=isinstance(reply,dict) and all(reply.get(k)==context[k] for k in ('domain','variant','mode','chart_digest'))
    if not valid_variant:hallucinations+=1
    if variant_claim_error:valid_variant=False
    kinds={c.get('kind') for c in claims if isinstance(c.get('kind'),str)}
    complete=len(kinds&KINDS)/len(KINDS)
    if 'explanation_policy' in context:
        policy=context['explanation_policy']
        covered_facts={c.get('fact_ref') for c in claims if c.get('kind')=='deterministic_fact' and isinstance(c.get('fact_ref'),str)}
        covered_rules={rid for c in claims if c.get('kind')=='rule_match' and isinstance(c.get('rule_ids'),list) for rid in c['rule_ids'] if isinstance(rid,str)}
        covered_notes={index for c in claims if c.get('kind')=='uncertainty' and isinstance(c.get('uncertainty_refs'),list) for index in c['uncertainty_refs'] if type(index) is int}
        coverage=lambda expected,actual:len(set(expected)&actual)/max(len(expected),1)
        complete=min(complete,coverage(policy['required_fact_refs'],covered_facts),
                     coverage(policy['required_rule_ids'],covered_rules),coverage(range(len(policy['uncertainty_notes'])),covered_notes))
    average=lambda values:sum(values)/len(values) if values else 0.0
    n=max(len(claims),1)
    metrics={'chart_fidelity':average(fact_checks),'rule_fidelity':average(rule_checks),
        'citation_validity':average(citation_checks),'evidence_grounding':average(ground_checks),
        'variant_consistency':float(valid_variant),'hallucination_rate':hallucinated_claims/n if valid_variant else 1.0,
        'unsupported_claim_rate':sum(not v for v in ground_checks)/n,
        'contradiction_rate':contradictory_claims/n,'explanation_completeness':complete}
    try:validate_reply(reply,context);validation_error=None
    except ExplanationFailure as error:validation_error=error.code
    # A passing transport/validator alone is insufficient for the stricter eval gates.
    passed=validation_error is None and bool(claims) and all(metrics[k]==1 for k in
        ('chart_fidelity','rule_fidelity','citation_validity','evidence_grounding','variant_consistency','explanation_completeness')) and hallucinations==0
    return {'metrics':metrics,'passed':passed,'validation_error':validation_error,
            'hallucination_count':hallucinations,'unsupported_claims':sum(not v for v in ground_checks),
            'contradiction_count':contradictions,'claim_count':len(claims),
            'semantic_review':'required','scoring_scope':'structural bindings and policy; prose entailment is not proven'}

class RecordingProvider:
    def __init__(self,provider):self.provider=provider;self.context=None;self.reply=None
    async def explain(self,context):
        self.context=copy.deepcopy(context)
        self.reply=await self.provider.explain(context)
        return self.reply

async def evaluate_suite(provider=None,*,prompt_version='explanation-prompt-v1',domains=None,suite=None,
                         run_kind='test_provider',model='not-configured',timeout=20):
    suite=suite or load_suite();prompt=get_prompt(prompt_version);results=[]
    for case in suite['cases']:
        if domains and case['domain'] not in domains:continue
        row={'id':case['id'],'domain':case['domain'],'expected':case['expected'],'tags':case['tags']}
        try:raw=execute_case(case)
        except (ValueError,TypeError):
            row.update(status='passed' if case['expected']=='input_rejected' else 'failed',error='input_rejected')
            results.append(row);continue
        except RuntimeError:
            row.update(status='failed',error='engine_oracle_drift');results.append(row);continue
        if case['expected']=='input_rejected':
            row.update(status='failed',error='unexpected_input_acceptance');results.append(row);continue
        if provider is None:
            row.update(status='not_run',error='provider_not_configured');results.append(row);continue
        recording=RecordingProvider(provider)
        try:
            validated=await ExplanationService(recording,timeout=timeout,prompt_version=prompt_version).explain(raw)
            row['reply_sha256']=digest(recording.reply)
            row['context_sha256']=digest(recording.context);row['review_context']=recording.context;row['model_reply']=recording.reply
            row['explanation']=validated
            row['scores']=score_reply(recording.reply,recording.context)
            row['status']='passed' if case['expected']=='explanation' and row['scores']['passed'] else 'failed'
            if case['expected']=='refused':row['error']='expected_refusal_missing'
        except ExplanationFailure as error:
            expected={'no_evidence':'insufficient_evidence','source_conflict':'source_conflict_unresolved'}.get(case.get('context_fault'))
            row.update(status='passed' if case['expected']=='refused' and error.code==expected else 'failed',error=error.code)
            if recording.reply is not None:
                row['reply_sha256']=digest(recording.reply);row['rejected_reply']=recording.reply
                row['context_sha256']=digest(recording.context);row['review_context']=recording.context;row['model_reply']=recording.reply
                row['scores']=score_reply(recording.reply,recording.context)
        results.append(row)
    reports={}
    for domain in sorted({r['domain'] for r in results}):
        rows=[r for r in results if r['domain']==domain];positive=[r for r in rows if r['expected']=='explanation']
        observed=[r for r in positive if 'scores' in r];scored=[r['scores'] for r in observed]
        avg=lambda key:statistics.mean(s['metrics'][key] for s in scored) if scored else None
        reports[domain]={'case_count':len(rows),'positive_cases':len(positive),'completed_model_responses':len(observed),
            'pass_rate':sum(r['status']=='passed' for r in positive)/len(positive) if provider is not None and positive else None,
            'metrics':{k:avg(k) for k in DIMENSIONS},'citation_accuracy':avg('citation_validity'),
            'chart_fidelity':avg('chart_fidelity'),'unsupported_claims':sum(s['unsupported_claims'] for s in scored) if scored else None,
            'hallucination_count':sum(s['hallucination_count'] for s in scored) if scored else None,
            'control_pass_rate':None if any(r['status']=='not_run' for r in rows if r['expected']!='explanation') else sum(r['status']=='passed' for r in rows if r['expected']!='explanation')/max(sum(r['expected']!='explanation' for r in rows),1),
            'not_run':[r['id'] for r in rows if r['status']=='not_run'],
            'failures':[{'id':r['id'],'error':r.get('error') or (r.get('scores',{}).get('validation_error')) or 'eval_gate_failed'} for r in rows if r['status']=='failed'],
            'online_ready':False,'semantic_review':'required; automatic bindings do not certify free prose',
            'semantic_metrics':{k:None for k in DIMENSIONS},'semantic_hallucination_count':None,
            'semantic_unsupported_claims':None,'semantic_contradiction_count':None}
    return {'schema_version':'1.0','suite_id':suite['suite_id'],'suite_sha256':digest(suite),'prompt':prompt,
            'run_kind':run_kind,'model':model,'real_model_evaluation':run_kind=='configured_external_http' and provider is not None,
            'reports':reports,'cases':results,'online_ready':False}

def markdown_report(report):
    lines=['# Explanation evaluation report','',f"Suite `{report['suite_id']}` / `{report['suite_sha256']}`",'',
        f"Prompt `{report['prompt']['version']}` / `{report['prompt']['sha256']}`; model `{report['model']}`; run `{report['run_kind']}`.",'',
        'Automatic scores measure structural bindings and policy, not semantic entailment. All domains require human review. Missing model results are N/A, never zero hallucinations or a passing score.','',
        '| Domain | Positive cases | Model responses | Pass rate | Citation accuracy | Chart fidelity | Unsupported claims | Hallucinations |',
        '| --- | --- | --- | --- | --- | --- | --- | --- |']
    def cell(value):return 'N/A' if value is None else str(round(value,4) if isinstance(value,float) else value)
    for domain,row in report['reports'].items():
        lines.append('| '+' | '.join([domain,*[cell(row[k]) for k in ['positive_cases','completed_model_responses','pass_rate','citation_accuracy','chart_fidelity','unsupported_claims','hallucination_count']]])+' |')
    for domain,row in report['reports'].items():
        lines.extend(['',f'## {domain}',''])
        lines.extend(f"- {failure['id']}: {failure['error']}" for failure in row['failures'])
        if row['not_run']:lines.append('- Not run: '+', '.join(row['not_run']))
        if not row['failures'] and not row['not_run']:lines.append('- No automatically detected failure; semantic review remains required.')
        lines.append('- Semantic review: '+row['semantic_review']+'; online readiness: '+str(row['online_ready']))
        if report.get('manual_review'):
            lines.append('- Human semantic metrics (reviewed claims only): '+json.dumps(row['semantic_metrics'],ensure_ascii=False))
            lines.extend('- Human failure '+failure['id']+': '+failure['notes'] for failure in row.get('semantic_failures',[]))
    return '\n'.join(lines)+'\n'
