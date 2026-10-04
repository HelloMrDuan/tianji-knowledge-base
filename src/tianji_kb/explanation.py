"""AI receives immutable chart facts and can only return validated, cited commentary."""
import asyncio,copy,re
from typing import Protocol
from jsonschema import Draft202012Validator,ValidationError
from starlette.concurrency import run_in_threadpool
from .rag_context import CanonicalRetriever,RetrievalUnavailable
from .runtime_catalog import digest
from .prompts import get_prompt,DEFAULT_PROMPT,POLICY_PROMPTS

class ExplanationProvider(Protocol):
    async def explain(self,context:dict)->dict:...

class ExplanationFailure(ValueError):
    def __init__(self,code):self.code=code;super().__init__(code)

REPLY_SCHEMA={
 'type':'object','additionalProperties':False,'required':['domain','variant','mode','chart_digest','claims'],
 'properties':{'domain':{'type':'string'},'variant':{'type':'string'},'mode':{'enum':['production','research']},
  'chart_digest':{'type':'string'},'claims':{'type':'array','minItems':1,'maxItems':12,'items':{
   'type':'object','additionalProperties':False,'required':['fact_ref','fact_value','text','evidence_ids','quotes'],
   'properties':{'fact_ref':{'type':'string'},'fact_value':{},'text':{'type':'string','minLength':1,'maxLength':2000},
    'evidence_ids':{'type':'array','minItems':1,'maxItems':12,'uniqueItems':True,'items':{'type':'string'}},
    'quotes':{'type':'array','maxItems':6,'items':{'type':'object','additionalProperties':False,
     'required':['evidence_id','text'],'properties':{'evidence_id':{'type':'string'},'text':{'type':'string','minLength':1}}}}}}}}}

INSTRUCTION=get_prompt()['instruction']

def fact_map(chart,*,include_containers=False):
    facts={}
    def walk(value,path):
        if include_containers:facts[path]=copy.deepcopy(value)
        if isinstance(value,dict):
            for key,item in value.items():walk(item,path+'/'+str(key).replace('~','~0').replace('/','~1'))
        elif isinstance(value,list):
            for index,item in enumerate(value):walk(item,path+'/'+str(index))
        else:facts[path]=value
    walk(chart,'/chart');return facts

def context_for(raw,rows,prompt_version=DEFAULT_PROMPT):
    prompt=get_prompt(prompt_version)
    context={'domain':raw['domain'],'variant':raw['variant'],'mode':raw['mode'],
        'chart_digest':digest(raw['result']),'chart':copy.deepcopy(raw['result']),
        'facts':fact_map(raw['result'],include_containers=prompt_version in POLICY_PROMPTS),'rules':copy.deepcopy(raw['rule_matches']),
        'trace':copy.deepcopy(raw['trace']),'evidence':copy.deepcopy(raw['evidence']),
        'rag':rows,'limitations':[raw.get('scope',''),*raw.get('unresolved',[])],
        'instructions':prompt['instruction'],'prompt_version':prompt['version'],'prompt_sha256':prompt['sha256'],'response_schema':REPLY_SCHEMA}
    if prompt_version in POLICY_PROMPTS:
        from .explanation_policy import add_policy,reply_schema
        context=add_policy(context);context['response_schema']=reply_schema(REPLY_SCHEMA,prompt_version)
    return context

def validate_citations(claim,evidence):
    if any(eid not in evidence for eid in claim['evidence_ids']):raise ExplanationFailure('citation_rejected')
    refs=[evidence[eid] for eid in claim['evidence_ids']]
    for quote in claim['quotes']:
        if not quote['text'].strip() or quote['evidence_id'] not in claim['evidence_ids'] or quote['text'] not in evidence[quote['evidence_id']]['original_text']:
            raise ExplanationFailure('citation_rejected')
    titles={ref['classic_title'] for ref in refs}|{ref['classic_title'].split('·')[0] for ref in refs}
    if any(title not in titles for title in re.findall(r'《([^》]+)》',claim['text'])):
        raise ExplanationFailure('citation_rejected')
    markers=re.findall(r'\[\[([^\]]+)\]\]|\[([^\]]+)\]',claim['text'])
    if any((a or b) not in claim['evidence_ids'] for a,b in markers):raise ExplanationFailure('citation_rejected')
    quotes=re.findall(r'「([^」]+)」|“([^”]+)”|『([^』]+)』',claim['text'])
    if any(not any(next(x for x in quote if x) in ref['original_text'] for ref in refs) for quote in quotes):
        raise ExplanationFailure('citation_rejected')
    urls=re.findall(r'https?://[^\s<>]+',claim['text'])
    if any(url not in {ref['source_url'] for ref in refs} for url in urls):raise ExplanationFailure('citation_rejected')

def validate_reply(reply,context):
    try:Draft202012Validator(context['response_schema']).validate(reply)
    except ValidationError as error:raise ExplanationFailure('invalid_model_response') from error
    for key in ['domain','variant','mode','chart_digest']:
        if reply[key]!=context[key]:raise ExplanationFailure('immutable_context_mismatch')
    evidence=context['evidence'];claims=[]
    for claim in reply['claims']:
        pointer=claim['fact_ref']
        if pointer not in context['facts'] or digest(claim['fact_value'])!=digest(context['facts'][pointer]):
            raise ExplanationFailure('chart_fact_mismatch')
        validate_citations(claim,evidence)
        claims.append({**copy.deepcopy(claim),'fact_value':copy.deepcopy(context['facts'][pointer]),
            'citations':[{'evidence_id':eid,'source_ref':copy.deepcopy(evidence[eid])} for eid in claim['evidence_ids']]})
    output={key:reply[key] for key in ['domain','variant','mode','chart_digest']}|{'claims':claims,'rag':context['rag']}
    if context['prompt_version'] in POLICY_PROMPTS:
        from .explanation_policy import validate_policy,response_policy
        validate_policy(reply,context);output.update(response_policy(reply,context))
    else:
        output.update(prompt_version=context['prompt_version'],prompt_sha256=context['prompt_sha256'],
            quality_status='legacy_requires_review',semantic_review_required=True,automatic_release_allowed=False,
            uncertainty_notes=context['limitations'],sections={})
    return output

class ExplanationService:
    def __init__(self,provider:ExplanationProvider,*,retriever=None,timeout=20,prompt_version=DEFAULT_PROMPT):
        self.provider=provider;self.retriever=retriever or CanonicalRetriever();self.timeout=timeout;self.prompt_version=prompt_version
    async def explain(self,raw):
        # Version selection and refusal gates run before retrieval/model invocation.
        try:get_prompt(self.prompt_version)
        except ValueError as error:raise ExplanationFailure('prompt_configuration_invalid') from error
        if self.prompt_version in POLICY_PROMPTS:
            from .explanation_policy import preflight
            preflight(raw)
        try:rows=await run_in_threadpool(self.retriever.retrieve,raw)
        except (RetrievalUnavailable,OSError,ValueError) as error:raise ExplanationFailure('retrieval_unavailable') from error
        if not rows:raise ExplanationFailure('insufficient_evidence')
        context=context_for(raw,rows,self.prompt_version)
        try:reply=await asyncio.wait_for(self.provider.explain(copy.deepcopy(context)),timeout=self.timeout)
        except asyncio.TimeoutError as error:raise ExplanationFailure('provider_timeout') from error
        except Exception as error:raise ExplanationFailure('provider_failed') from error
        return validate_reply(reply,context)
