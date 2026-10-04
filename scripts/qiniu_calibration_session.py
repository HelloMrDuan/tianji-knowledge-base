#!/usr/bin/env python3
"""Private local calibration session; one hidden key entry, strictly limited jobs."""
import argparse
import getpass
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from uuid import uuid4
import warnings

from calibrate_qiniu import ROOT, calibration_environment
from tianji_kb.engine import PROVIDERS
from tianji_kb.prompts import DEFAULT_PROMPT, PROMPTS
from tianji_kb.model_discovery import MODEL_ID, NON_CHAT


def job_arguments(job):
    allowed={'id','kind','domains','prompts','timeout_seconds','max_output_tokens','model'}
    if not isinstance(job,dict) or set(job)-allowed:raise ValueError('invalid_job')
    if not isinstance(job.get('id'),str) or not re.fullmatch('[a-f0-9]{32}',job['id']):raise ValueError('invalid_job')
    if job.get('kind') not in ('smoke','full','exit'):raise ValueError('invalid_job')
    domains=job.get('domains',list(PROVIDERS));prompts=job.get('prompts',[DEFAULT_PROMPT])
    for values,choices in ((domains,PROVIDERS),(prompts,PROMPTS)):
        if not isinstance(values,list) or not values or any(not isinstance(v,str) or v not in choices for v in values):raise ValueError('invalid_job')
        if len(set(values))!=len(values):raise ValueError('invalid_job')
    timeout=job.get('timeout_seconds',90);tokens=job.get('max_output_tokens',8192)
    if type(timeout) not in (float,int) or not math.isfinite(timeout) or not 0<timeout<=120:raise ValueError('invalid_job')
    if type(tokens) is not int or not 256<=tokens<=16384:raise ValueError('invalid_job')
    args=['--domains',*domains,'--prompts',*prompts]
    if job['kind']=='smoke':args.append('--smoke')
    if 'model' in job:
        model=job['model']
        if not isinstance(model,str) or not MODEL_ID.fullmatch(model) or NON_CHAT.search(model):raise ValueError('invalid_job')
        args.extend(['--model',model])
    return args,str(timeout),str(tokens)


def write_json(path,value):
    temporary=path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    temporary.replace(path)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--smoke-domain',choices=list(PROVIDERS),default='yijing')
    args=parser.parse_args();key=os.environ.get('TIANJI_AI_API_KEY','')
    if not key:
        if not sys.stdin.isatty():print('Private credential input requires a local terminal');return 2
        try:
            with warnings.catch_warnings():
                warnings.simplefilter('error',getpass.GetPassWarning)
                key=getpass.getpass('Qiniu API Key (hidden, this private session only): ')
        except (getpass.GetPassWarning,EOFError):print('Hidden input unavailable');return 2
    try:environment=calibration_environment(key)
    except ValueError:print('Credential missing');return 2
    session=ROOT/'build/provider-discovery'/uuid4().hex
    result=subprocess.run([sys.executable,str(ROOT/'scripts/discover_explanation_model.py'),'--output',str(session)],
                          cwd=ROOT,env=environment,check=False)
    if result.returncode:return result.returncode
    environment['TIANJI_AI_MODEL']=json.loads((session/'selection.json').read_text(encoding='utf-8'))['model']
    write_json(session/'session.json',{'pid':os.getpid(),'state':'ready','model':environment['TIANJI_AI_MODEL'],
        'credential_storage':'private_process_only','automatic_release_allowed':False})
    write_json(session/'job.json',{'id':uuid4().hex,'kind':'smoke','domains':[args.smoke_domain],
        'timeout_seconds':90,'max_output_tokens':8192})
    print('Private session ready. Initial single-domain smoke starts; later jobs require this task to submit a job.',flush=True)
    print('Close this window to discard the private session. Production AI remains disabled.',flush=True)
    try:
        while True:
            path=session/'job.json'
            if not path.is_file():time.sleep(0.5);continue
            try:
                job=json.loads(path.read_text(encoding='utf-8'));arguments,timeout,tokens=job_arguments(job)
            except (OSError,ValueError,TypeError):
                path.unlink(missing_ok=True);print('Invalid calibration job rejected',flush=True);continue
            path.unlink()
            if job['kind']=='exit':break
            output=session/job['id']
            if output.exists():print('Existing job ID rejected; no stale report reused',flush=True);continue
            write_json(session/'session.json',{'pid':os.getpid(),'state':'running','job_id':job['id'],
                'model':environment['TIANJI_AI_MODEL'],'credential_storage':'private_process_only',
                'automatic_release_allowed':False})
            job_env={**environment,'TIANJI_AI_TIMEOUT_SECONDS':timeout,'TIANJI_AI_MAX_OUTPUT_TOKENS':tokens}
            result=subprocess.run([sys.executable,str(ROOT/'scripts/evaluate_explanations.py'),*arguments,
                '--output',str(output)],cwd=ROOT,env=job_env,check=False)
            write_json(session/'last-job.json',{'id':job['id'],'kind':job['kind'],'exit_code':result.returncode,
                'output':output.relative_to(ROOT).as_posix(),'automatic_release_allowed':False})
            write_json(session/'session.json',{'pid':os.getpid(),'state':'ready','model':environment['TIANJI_AI_MODEL'],
                'credential_storage':'private_process_only','automatic_release_allowed':False})
            print('Job finished. Results require examination; waiting for the next calibration job.',flush=True)
    finally:
        environment.pop('TIANJI_AI_API_KEY',None);key=''
        write_json(session/'session.json',{'pid':os.getpid(),'state':'closed','automatic_release_allowed':False})
    return 0


if __name__=='__main__':raise SystemExit(main())
