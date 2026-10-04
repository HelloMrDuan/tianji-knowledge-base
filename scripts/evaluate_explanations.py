#!/usr/bin/env python3
"""Internal batch tool; all provider/model/credential settings come from environment."""
import argparse,asyncio,json,os,time
from pathlib import Path
from urllib.parse import urlsplit
from tianji_kb.ai_providers import provider_from_environment,timeout_from_environment
from tianji_kb.engine import PROVIDERS
from tianji_kb.explanation import ExplanationFailure
from tianji_kb.explanation_eval import evaluate_suite,markdown_report
from tianji_kb.prompts import PROMPTS
import httpx

class ProgressProvider:
    """Record bounded transport progress; never imply a case or quality pass."""
    def __init__(self,provider,path,prompt):
        self.provider=provider;self.path=path;self.prompt=prompt;self.calls=0
    async def explain(self,context):
        self.calls+=1;number=self.calls;started=time.monotonic();outcome='call_interrupted';status=None
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
                   'http_status':status,'elapsed_seconds':round(time.monotonic()-started,2)}
            with self.path.open('a',encoding='utf-8') as output:output.write(json.dumps(event)+'\n')
            print(self.prompt,'model request',number,outcome,'; case validation and semantic review are separate',flush=True)

async def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prompts',nargs='+',choices=list(PROMPTS),default=list(PROMPTS))
    parser.add_argument('--domains',nargs='+',choices=list(PROVIDERS))
    parser.add_argument('--output',type=Path,default=Path('build/explanation-evals'))
    parser.add_argument('--dry-run',action='store_true',help='Validate engine/cases without contacting a model; quality is not scored')
    args=parser.parse_args();provider=None;timeout=20
    if not args.dry_run:
        try:provider=provider_from_environment();timeout=timeout_from_environment()
        except (ExplanationFailure,ValueError):print('Provider configuration unavailable; no model invoked')
    host=urlsplit(os.environ.get('TIANJI_AI_BASE_URL','')).hostname
    run_kind='not_run' if provider is None else 'local_test_service' if host in ('localhost','127.0.0.1','::1') else 'configured_external_http'
    args.output.mkdir(parents=True,exist_ok=True);comparison=[]
    for version in args.prompts:
        print(version,'fixed-suite evaluation started;',run_kind,flush=True)
        progress_path=args.output/(version+'-progress.jsonl');progress_path.write_text('',encoding='utf-8')
        progress=ProgressProvider(provider,progress_path,version) if provider else None
        report=await evaluate_suite(progress,prompt_version=version,domains=args.domains,run_kind=run_kind,
            model=os.environ.get('TIANJI_AI_MODEL','not-configured'),timeout=timeout)
        (args.output/(version+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        (args.output/(version+'.md')).write_text(markdown_report(report))
        comparison.append({'prompt':version,'suite_sha256':report['suite_sha256'],'reports':report['reports']})
        print(version,run_kind,'cases',len(report['cases']),'failures',sum(c['status']=='failed' for c in report['cases']))
    (args.output/'comparison.json').write_text(json.dumps(comparison,ensure_ascii=False,indent=2)+'\n')
    if provider is None and not args.dry_run:return 2
    return int(any(row['failures'] for report in comparison for row in report['reports'].values()))

if __name__=='__main__':raise SystemExit(asyncio.run(main()))
