"""Human semantic review binds to exact eval/prompt/model/response; never scores itself."""
import copy
from .runtime_catalog import digest

POSITIVE=('chart_fidelity','rule_fidelity','citation_validity','evidence_grounding','variant_consistency')
NEGATIVE=('hallucination','unsupported_claim','contradiction')
REVIEW_FIELDS=(*POSITIVE,*NEGATIVE)


def review_template(report):
    return {'schema_version':'1.0','evaluation_sha256':digest(report),'suite_sha256':report['suite_sha256'],
        'prompt_sha256':report['prompt']['sha256'],'model':report['model'],'reviews':[
        {'case_id':row['id'],'reply_sha256':row['reply_sha256'],'context_sha256':row['context_sha256'],
         'reviewer':'','reviewed_at':'','notes':'','explanation_completeness':None,
         'claims':[{'claim_index':i,**{field:None for field in REVIEW_FIELDS},'notes':''}
                   for i,_ in enumerate(row['model_reply']['claims'])]}
        for row in report['cases'] if row.get('reply_sha256') and row.get('context_sha256') and isinstance(row.get('model_reply'),dict) and isinstance(row['model_reply'].get('claims'),list) and row['model_reply']['claims'] and all(isinstance(c,dict) for c in row['model_reply']['claims'])]}


def apply_reviews(report,document):
    from datetime import datetime
    required={'schema_version','evaluation_sha256','suite_sha256','prompt_sha256','model','reviews'}
    if set(document)!=required or document['schema_version']!='1.0':raise ValueError('Invalid semantic review document')
    for key,value in [('evaluation_sha256',digest(report)),('suite_sha256',report['suite_sha256']),
                      ('prompt_sha256',report['prompt']['sha256']),('model',report['model'])]:
        if document[key]!=value:raise ValueError('Review provenance mismatch: '+key)
    if not isinstance(document['reviews'],list):raise ValueError('Reviews must be a list')
    rows={r['id']:r for r in report['cases']};by_id={}
    for review in document['reviews']:
        if set(review)!={'case_id','reply_sha256','context_sha256','reviewer','reviewed_at','notes','explanation_completeness','claims'}:
            raise ValueError('Invalid case review fields')
        cid=review['case_id']
        if not isinstance(cid,str) or cid not in rows or cid in by_id:raise ValueError('Unknown or duplicate case review')
        row=rows[cid]
        if review['reply_sha256']!=row.get('reply_sha256') or review['context_sha256']!=row.get('context_sha256'):
            raise ValueError('Review response/context digest mismatch')
        if not isinstance(review['reviewer'],str) or not review['reviewer'].strip() or not isinstance(review['notes'],str) or not review['notes'].strip():
            raise ValueError('Reviewer identity and human notes are required')
        try:
            parsed=datetime.fromisoformat(review['reviewed_at'].replace('Z','+00:00'))
            if parsed.tzinfo is None:raise ValueError('Review time requires timezone')
        except (ValueError,TypeError,AttributeError) as error:raise ValueError('Invalid review timestamp') from error
        if type(review['explanation_completeness']) is not bool:raise ValueError('Human completeness judgment required')
        if digest(row.get('model_reply'))!=row.get('reply_sha256') or digest(row.get('review_context'))!=row.get('context_sha256'):
            raise ValueError('Recorded response/context integrity mismatch')
        original=row.get('model_reply',{})
        count=len(original.get('claims',[]));claims=review['claims']
        if not isinstance(claims,list) or len(claims)!=count or count==0:raise ValueError('Every observed claim needs review')
        indexes=set()
        for claim in claims:
            if set(claim)!={'claim_index',*REVIEW_FIELDS,'notes'}:raise ValueError('Invalid claim review fields')
            index=claim['claim_index']
            if type(index) is not int or not 0<=index<count or index in indexes:raise ValueError('Unknown or duplicate claim index')
            indexes.add(index)
            if any(type(claim[field]) is not bool for field in REVIEW_FIELDS):raise ValueError('Every semantic dimension requires a human boolean judgment')
            if not isinstance(claim['notes'],str):raise ValueError('Claim notes must be text')
            if (any(not claim[k] for k in POSITIVE) or any(claim[k] for k in NEGATIVE)) and not claim['notes'].strip():
                raise ValueError('Failed claim needs a specific human note')
        by_id[cid]=copy.deepcopy(review)
    from .explanation_eval import load_suite
    suite=load_suite()
    fixed_suite_matches=report['suite_sha256']==digest(suite)
    output=copy.deepcopy(report)
    output['manual_review']={'raw_evaluation_sha256':digest(report),'review_sha256':digest(document),
        'reviewed_cases':len(by_id),'basis':'human-authored judgments, not an independent certification'}
    for domain,summary in output['reports'].items():
        positives=[r for r in report['cases'] if r['domain']==domain and r['expected']=='explanation']
        reviewed=[by_id[r['id']] for r in positives if r['id'] in by_id]
        claims=[c for r in reviewed for c in r['claims']]
        n=len(claims)
        mean=lambda key:sum(c[key] for c in claims)/n if n else None
        semantic={key:mean(key) for key in POSITIVE}
        semantic.update(hallucination_rate=mean('hallucination'),unsupported_claim_rate=mean('unsupported_claim'),
            contradiction_rate=mean('contradiction'),
            explanation_completeness=sum(r['explanation_completeness'] for r in reviewed)/len(reviewed) if reviewed else None)
        failures=[{'id':r['case_id'],'notes':r['notes'],'claims':[c for c in r['claims'] if any(not c[k] for k in POSITIVE) or any(c[k] for k in NEGATIVE)]}
                  for r in reviewed if not r['explanation_completeness'] or any(any(not c[k] for k in POSITIVE) or any(c[k] for k in NEGATIVE) for c in r['claims'])]
        complete=len(reviewed)==len(positives) and len(positives)>=10
        domain_cases=[r for r in report['cases'] if r['domain']==domain]
        expected_ids={c['id'] for c in suite['cases'] if c['domain']==domain}
        fixed_domain_complete=fixed_suite_matches and {r['id'] for r in domain_cases}==expected_ids
        qualified=fixed_domain_complete and report['real_model_evaluation'] and report['run_kind']=='configured_external_http' and complete and not failures and all(r['status']=='passed' for r in domain_cases)
        summary.update(semantic_metrics=semantic,semantic_reviewed_cases=len(reviewed),
            semantic_failures=failures,semantic_review='complete' if complete else 'incomplete',
            semantic_hallucination_count=sum(c['hallucination'] for c in claims) if claims else None,
            semantic_unsupported_claims=sum(c['unsupported_claim'] for c in claims) if claims else None,
            semantic_contradiction_count=sum(c['contradiction'] for c in claims) if claims else None,
            online_ready=qualified,readiness='eligible_for_supervised_beta' if qualified else 'not_qualified')
    output['online_ready']=bool(output['reports']) and all(r['online_ready'] for r in output['reports'].values())
    output['release_scope']='Exact evaluated model/prompt/domains and reviewed fixture scope; not all arbitrary user inputs'
    return output
