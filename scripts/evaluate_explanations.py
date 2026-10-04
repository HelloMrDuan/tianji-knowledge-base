#!/usr/bin/env python3
"""Internal evaluation; credentials from environment, comparison models verified against /models."""
import argparse,asyncio,json,os,re,time
from pathlib import Path
from urllib.parse import urlsplit
from tianji_kb.ai_providers import provider_from_environment,timeout_from_environment
from tianji_kb.engine import PROVIDERS
from tianji_kb.explanation import ExplanationFailure
from tianji_kb.explanation_eval import evaluate_suite,markdown_report,load_suite
from tianji_kb.prompts import PROMPTS
from tianji_kb.model_discovery import advertised_candidates
import httpx

class ProgressProvider:
    """Record bounded transport progress; never imply a case or quality pass."""
    def __init__(self,provider,path,prompt):
        self.provider=provider;self.path=path;self.prompt=prompt;self.calls=0;self.response_metadata={}
        if hasattr(provider,'post'):
            original=provider.post
            async def observed_post(url,body):
                response=await original(url,body)
                self.response_metadata=response_metadata(response)
                return response
            provider.post=observed_post
    async def explain(self,context):
        self.calls+=1;number=self.calls;started=time.monotonic();outcome='call_interrupted';status=None;self.response_metadata={}
        print(self.prompt,'model request',number,context['domain'],'started',flush=True)
        try:
            reply=await self.provider.explain(context);outcome='reply_received';return reply
        except httpx.HTTPStatusError as error:
            outcome='http_error';status=error.response.status_code;raise
        except httpx.TimeoutException:
            outcome='transport_timeout';raise
        except (json.JSONDecodeError,KeyError,TypeError):
            outcome='response_format_error';raise
        except Exception:
            outcome='provider_error';raise
        finally:
            event={'prompt':self.prompt,'request':number,'domain':context['domain'],'outcome':outcome,
                   'http_status':status,'elapsed_seconds':round(time.monotonic()-started,2),
                   'response_metadata':self.response_metadata}
            with self.path.open('a',encoding='utf-8') as output:output.write(json.dumps(event)+'\n')
            print(self.prompt,'model request',number,outcome,'; case validation and semantic review are separate',flush=True)

def response_metadata(response):
    """Only lengths, standard termination enums and bounded token counters."""
    output={}
    if not isinstance(response,dict):return output
    choices=response.get('choices')
    if isinstance(choices,list) and choices and isinstance(choices[0],dict):
        choice=choices[0];reason=choice.get('finish_reason')
        output['finish_reason']=reason if reason in ('stop','length','tool_calls','content_filter') else 'unrecognized'
        message=choice.get('message')
        if isinstance(message,dict):
            for key in ('content','reasoning_content'):
                value=message.get(key);output[key+'_chars']=len(value) if isinstance(value,str) else None
    usage=response.get('usage')
    if isinstance(usage,dict):
        output['usage']={key:value for key,value in usage.items()
            if key in ('prompt_tokens','completion_tokens','total_tokens','input_tokens','output_tokens')
            and type(value) is int and 0<=value<=10000000}
    return output

def smoke_suite(suite):
    selected=set();cases=[]
    for case in suite['cases']:
        if case['expected']!='explanation' or case['domain'] not in selected:
            cases.append(case)
            if case['expected']=='explanation':selected.add(case['domain'])
    return {**suite,'cases':cases}

def private_model_request(output):
    """A non-secret, job-bound override for an already open private worker."""
    root=Path(__file__).resolve().parents[1]/'build/provider-discovery'
    output=output.resolve();session=output.parent
    if session.parent!=root or not all(re.fullmatch('[a-f0-9]{32}',p.name) for p in (session,output)):return None
    path=session/'job-model.json'
    if not path.is_file():return None
    value=json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(value,dict) or set(value)!={'job_id','model'}:raise ValueError('Invalid model request')
    if value['job_id']!=output.name:return None
    if not isinstance(value['model'],str):raise ValueError('Invalid model request')
    return value['model']

async def select_comparison_model(provider,requested,output):
    """Only advertised chat IDs; lightweight is a comparison, not qualification."""
    if provider.settings['driver']!='openai-compatible':raise ValueError('Model comparison requires compatible provider')
    base=provider.settings['endpoint'].rstrip('/')
    if base.endswith('/chat/completions'):base=base[:-len('/chat/completions')]
    candidates=advertised_candidates(await provider.get(base+'/models'),provider.settings['key'])
    if requested=='lightweight':
        light=[m for m in candidates if re.search(r'flash|turbo|(?:^|[-/])(?:7b|8b|14b)(?:$|[-/])',m,re.I)
               and not re.search(r'thinking|reasoner|preview|exp|vision|vl|omni',m,re.I)]
        light.sort(key=lambda m:(0 if 'qwen' in m.lower() and 'flash' in m.lower() else 1,m))
        if not light:raise ValueError('No advertised lightweight chat candidate')
        requested=light[0]
    if requested not in candidates:raise ValueError('Model not advertised')
    provider.settings={**provider.settings,'model':requested}
    output.mkdir(parents=True,exist_ok=True)
    (output/'model-selection.json').write_text(json.dumps({'model':requested,'advertised_candidates':candidates,
        'selection_purpose':'comparison_only','quality_checked':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return requested

async def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prompts',nargs='+',choices=list(PROMPTS),default=list(PROMPTS))
    parser.add_argument('--domains',nargs='+',choices=list(PROVIDERS))
    parser.add_argument('--output',type=Path,default=Path('build/explanation-evals'))
    parser.add_argument('--dry-run',action='store_true',help='Validate engine/cases without contacting a model; quality is not scored')
    parser.add_argument('--smoke',action='store_true',help='One fixed positive per domain plus all controls; cannot qualify for release')
    parser.add_argument('--model',help='Compare an advertised chat model, or lightweight; does not alter production settings')
    args=parser.parse_args();provider=None;timeout=20
    if not args.dry_run:
        try:provider=provider_from_environment();timeout=timeout_from_environment()
        except (ExplanationFailure,ValueError):print('Provider configuration unavailable; no model invoked')
    model=os.environ.get('TIANJI_AI_MODEL','not-configured')
    if provider is not None:
        try:
            requested=args.model or private_model_request(args.output)
            if requested:model=await select_comparison_model(provider,requested,args.output)
        except Exception:
            print('Advertised comparison model unavailable; no explanation invoked');return 2
    host=urlsplit(os.environ.get('TIANJI_AI_BASE_URL','')).hostname
    run_kind='not_run' if provider is None else 'local_test_service' if host in ('localhost','127.0.0.1','::1') else 'configured_external_http'
    args.output.mkdir(parents=True,exist_ok=True);comparison=[]
    suite=smoke_suite(load_suite()) if args.smoke else None
    for version in args.prompts:
        print(version,'fixed-suite evaluation started;',run_kind,flush=True)
        progress_path=args.output/(version+'-progress.jsonl');progress_path.write_text('',encoding='utf-8')
        progress=ProgressProvider(provider,progress_path,version) if provider else None
        report=await evaluate_suite(progress,prompt_version=version,domains=args.domains,suite=suite,run_kind=run_kind,
            model=model,timeout=timeout)
        report['evaluation_scope']='smoke_subset_not_qualified' if args.smoke else 'fixed_full_domain_suite'
        report['request_profile']={'timeout_seconds':timeout,
            'max_output_tokens':provider.settings['max_tokens'] if provider else None,'temperature':0}
        (args.output/(version+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        (args.output/(version+'.md')).write_text(markdown_report(report))
        comparison.append({'prompt':version,'suite_sha256':report['suite_sha256'],'reports':report['reports']})
        print(version,run_kind,'cases',len(report['cases']),'failures',sum(c['status']=='failed' for c in report['cases']))
    (args.output/'comparison.json').write_text(json.dumps(comparison,ensure_ascii=False,indent=2)+'\n')
    if provider is None and not args.dry_run:return 2
    return int(any(row['failures'] for report in comparison for row in report['reports'].values()))

if __name__=='__main__':raise SystemExit(asyncio.run(main()))
