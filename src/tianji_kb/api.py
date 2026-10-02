"""Unified HTTP transport for the existing six-domain deterministic engine."""
from typing import Any,Literal
from fastapi import FastAPI,HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel,ConfigDict,Field,StrictBool,StrictStr
from starlette.concurrency import run_in_threadpool
from .engine import execute,PROVIDERS
from .resolver import EvidenceResolver
from .runtime_catalog import RuntimeUnavailable

Domain=Literal['liuyao','qimen','liuren','ziwei','fengshui','yijing']
Mode=Literal['production','research']
EXAMPLES={
 'liuyao':{'value':'2000-01-07T12:00:00+08:00','yao_values':[7]*6},
 'qimen':{'value':'2000-01-07T12:00:00+08:00'},
 'liuren':{'value':'2000-01-07T12:00:00+08:00'},
 'ziwei':{'value':'1999-02-16T00:00:00+08:00','year_boundary':'lunar-new-year'},
 'fengshui':{'degrees':37.5},'yijing':{'bits':'111000','changing_lines':[1]},
}

class ExecuteRequest(BaseModel):
    model_config=ConfigDict(extra='forbid')
    domain:Domain
    variant:StrictStr|None=Field(default=None,min_length=1,max_length=160)
    input:dict[str,Any]
    explain:StrictBool=False
    mode:Mode='production'

class ExecuteResponse(BaseModel):
    model_config=ConfigDict(extra='forbid')
    domain:Domain
    variant:str
    mode:Mode
    deterministic:bool
    chart:dict[str,Any]
    rule_matches:list[dict[str,Any]]
    trace:list[dict[str,Any]]
    evidence:dict[str,dict[str,Any]]
    warnings:list[str]
    limitations:list[str]
    explanation:dict[str,Any]|None=None
    explanation_status:Literal['disabled','succeeded','failed']='disabled'
    explanation_error:str|None=None
    calendar:dict[str,Any]|None=None


def response_for(raw):
    warnings=[]
    if raw['mode']=='research':warnings.append('研究模式：实验或待核约定不代表已审 Canonical，不得自动晋级。')
    warnings.extend(dict.fromkeys(step['evidence_scope'] for step in raw['trace'] if 'D' in step.get('evidence_scope','')))
    return ExecuteResponse(domain=raw['domain'],variant=raw['variant'],mode=raw['mode'],deterministic=True,
        chart=raw['result'],rule_matches=raw['rule_matches'],
        trace=[{**step,'variant':raw['variant']} for step in raw['trace']],evidence=raw['evidence'],
        warnings=warnings,limitations=[raw['scope'],*raw['unresolved']],
        calendar=raw.get('input_calendar') or raw['result'].get('calendar'))


def create_app(explanation_service=None):
    app=FastAPI(title='Tianji deterministic knowledge API',version='1.0.0',
        description='Canonical calculation → RuleMatch → trace → Evidence; AI may explain but may not compute charts.')
    app.state.explanation_service=explanation_service

    @app.exception_handler(RequestValidationError)
    async def invalid_request(request,error):
        # Never echo submitted values (including accidental keys/secrets) in error bodies.
        return JSONResponse(status_code=422,content={'detail':[{'loc':list(e['loc']),'type':e['type'],'msg':e['msg']} for e in error.errors()]})

    @app.exception_handler(RuntimeUnavailable)
    async def unavailable(request,error):
        return JSONResponse(status_code=503,content={'detail':{'code':'runtime_unavailable','message':str(error)}})

    @app.get('/health',tags=['system'])
    def health():
        resolver=EvidenceResolver()
        return {'status':'ok','engine':'ready','domains':list(PROVIDERS),
                'production_runtime':'reviewed','explanation_configured':app.state.explanation_service is not None}

    @app.get('/api/v1/capabilities',tags=['system'])
    def capabilities():
        resolver=EvidenceResolver()
        return {'api_version':'v1','default_mode':'production','ai_may_compute_chart':False,
            'domains':[{'domain':domain,'variants':[c['variant']],'default_variant':c['variant'],
                        'scope':c.get('scope',''),'limitations':c.get('unresolved',[]),
                        'example':{'domain':domain,'variant':c['variant'],'input':EXAMPLES[domain],'explain':False,'mode':'production'}}
                       for domain,c in sorted(resolver.contracts.items())]}

    @app.post('/api/v1/execute',response_model=ExecuteResponse,tags=['execution'])
    async def execute_request(request:ExecuteRequest):
        inputs=dict(request.input)
        # The API mode is authoritative; clients cannot bypass it with an engine-only flag.
        if 'research' in inputs:raise HTTPException(422,detail={'code':'invalid_input','message':'Use request.mode to select research, not input.research'})
        if request.domain=='fengshui' and request.mode=='research' and inputs.get('year') is not None:
            inputs['research']=True
        try:
            raw=await run_in_threadpool(execute,request.domain,inputs,request.variant,allow_research=request.mode=='research')
        except RuntimeUnavailable:raise
        except (ValueError,TypeError) as error:
            raise HTTPException(422,detail={'code':'invalid_input','message':str(error)}) from error
        result=response_for(raw)
        if request.explain:
            result.explanation_status='failed'
            result.explanation_error='provider_not_configured'
            result.warnings.append('解释暂不可用；确定性盘面、规则与证据仍正常返回。')
        return result

    return app

app=create_app()
