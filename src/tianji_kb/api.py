"""Unified HTTP transport for the existing six-domain deterministic engine."""
import copy,os,hashlib,secrets
from typing import Any,Literal
from fastapi import FastAPI,HTTPException,Header,Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel,ConfigDict,Field,StrictBool,StrictStr
from starlette.concurrency import run_in_threadpool
from .engine import execute,PROVIDERS
from .resolver import EvidenceResolver
from .runtime_catalog import RuntimeUnavailable
from .explanation import ExplanationService,ExplanationFailure
from .ai_providers import provider_from_environment,provider_configured,timeout_from_environment,DRIVERS
from .runtime_catalog import load_catalog
from .resolver import ROOT
from .prompts import DEFAULT_PROMPT,PROMPTS
from .scenario_engine import execute_scenario,registry as scenario_registry
from .public_projection import project_execution,PUBLIC_EXECUTION_DOMAINS,PUBLIC_SCENARIO_STATES
from .operations.dream_knowledge import retrieve as retrieve_dream_culture
from .rag_context import RetrievalUnavailable
from .governance import school_conflicts,reviewed_rules,reviewed_evidence,reviewed_classics,reviewed_chapters,reviewed_terms,reviewed_sources,reviewed_layers,reviewed_algorithms,provider_configuration,prompt_registry
from .admin_scopes import ADMIN_READ_SCOPES,parse_admin_scopes,resolve_admin_access
from .admin_roles import parse_admin_role_tokens,resolve_role_access
from .admin_audit import AuditLog
from .admin_drafts import DraftStore,DraftNotFoundError,InvalidTransitionError,InvalidDraftInputError,STORAGE_NOTE,DRAFT_ACTION_OPERATION

Domain=Literal['liuyao','qimen','liuren','ziwei','fengshui','yijing','bazi']
Mode=Literal['production','research']
EXAMPLES={
 'liuyao':{'value':'2000-01-07T12:00:00+08:00','yao_values':[7]*6},
 'qimen':{'value':'2000-01-07T12:00:00+08:00'},
 'liuren':{'value':'2000-01-07T12:00:00+08:00'},
 'ziwei':{'value':'1999-02-16T00:00:00+08:00','year_boundary':'lunar-new-year'},
 'fengshui':{'degrees':37.5},'yijing':{'bits':'111000','changing_lines':[1]},
 'bazi':{'value':'2000-01-07T12:00:00+08:00'},
}

class PublicDreamCultureRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    dream_text: StrictStr = Field(min_length=2, max_length=500)

class PublicDreamCultureMatch(BaseModel):
    model_config = ConfigDict(extra='forbid')
    scene: str
    matched_texts: list[str]
    cultural_reading: str
    short_quote: str
    source_title: str
    evidence_level: str

class PublicDreamInputTopic(BaseModel):
    model_config = ConfigDict(extra='forbid')
    label: Literal['考试', '怀孕', '结婚', '工作', '被追', '故人', '死亡']
    matched_texts: list[str]


class PublicDreamCultureResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')
    api_version: Literal['v1'] = 'v1'
    status: Literal['reviewed_cultural_matches', 'no_reviewed_interpretation']
    public_release: Literal[True] = True
    cultural_reference_only: Literal[True] = True
    ai_enabled: Literal[False] = False
    personal_prediction: Literal[False] = False
    matches: list[PublicDreamCultureMatch]
    unreviewed_topics: list[PublicDreamInputTopic] = Field(default_factory=list)
    notice: str = '仅展示已审核传统占梦条目，不代表个人运势、健康或未来事件。'

class AdminDreamResearchRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    dream_text: StrictStr = Field(min_length=2, max_length=500)

class ExecuteRequest(BaseModel):
    model_config=ConfigDict(extra='forbid')
    domain:Domain
    variant:StrictStr|None=Field(default=None,min_length=1,max_length=160)
    input:dict[str,Any]
    explain:StrictBool=False
    mode:Mode='production'

class ScenarioExecuteRequest(BaseModel):
    model_config=ConfigDict(extra='forbid')
    scenario_id:StrictStr=Field(min_length=1,max_length=120)
    input:dict[str,Any]

class ScenarioExecuteResponse(BaseModel):
    model_config=ConfigDict(extra='forbid')
    scenario_id:str
    status:str
    public_release:bool
    deterministic:bool
    result:dict[str,Any]
    rule_matches:list[dict[str,Any]]
    trace:list[dict[str,Any]]
    evidence:dict[str,dict[str,Any]]
    warnings:list[str]
    limitations:list[str]

class AdminWriteProbeRequest(BaseModel):
    model_config=ConfigDict(extra='forbid')
    operation:Literal['draft','approve','publish']

class AdminDraftCreateRequest(BaseModel):
    model_config=ConfigDict(extra='forbid')
    title:str
    body:str

class AdminDraftEditRequest(BaseModel):
    model_config=ConfigDict(extra='forbid')
    title:str|None=None
    body:str|None=None

class AdminDraftRollbackRequest(BaseModel):
    model_config=ConfigDict(extra='forbid')
    version:int

class ExplanationQuote(BaseModel):
    model_config=ConfigDict(extra='forbid')
    evidence_id:str
    text:str

class ExplanationCitation(BaseModel):
    model_config=ConfigDict(extra='forbid')
    evidence_id:str
    source_ref:dict[str,Any]

class ExplanationClaim(BaseModel):
    model_config=ConfigDict(extra='forbid')
    fact_ref:str
    fact_value:Any
    text:str
    evidence_ids:list[str]
    quotes:list[ExplanationQuote]
    citations:list[ExplanationCitation]
    kind:Literal['deterministic_fact','rule_match','classical_evidence','synthesis','uncertainty']|None=None
    rule_ids:list[str]=Field(default_factory=list)
    strength:Literal['computed','conditional','unverified']|None=None
    uncertainty_refs:list[int]=Field(default_factory=list)

class ExplanationResponse(BaseModel):
    model_config=ConfigDict(extra='forbid')
    domain:Domain
    variant:str
    mode:Mode
    chart_digest:str
    claims:list[ExplanationClaim]
    rag:list[dict[str,Any]]
    prompt_version:str
    prompt_sha256:str
    quality_status:Literal['legacy_requires_review','degraded_requires_review','requires_semantic_review']
    semantic_review_required:bool
    automatic_release_allowed:bool
    uncertainty_notes:list[str]
    sections:dict[str,list[int]]

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
    explanation:ExplanationResponse|None=None
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


def create_app(provider=None,*,explanation_timeout=None,admin_read_token=None,admin_read_scopes=None,admin_role_tokens=None):
    app=FastAPI(title='Tianji deterministic knowledge API',version='1.0.0',
        description='Canonical calculation → RuleMatch → trace → Evidence; AI may explain but may not compute charts.')
    app.state.provider=provider
    app.state.admin_read_token=admin_read_token if admin_read_token is not None else os.environ.get('TIANJI_ADMIN_READ_TOKEN')
    # Scope model (TJ-026.3): server-side configuration of the read token.
    # None means all scopes (backward compatible single-token deployments).
    # Explicit param wins; otherwise TIANJI_ADMIN_READ_SCOPES (comma list).
    app.state.admin_read_scopes=(parse_admin_scopes(os.environ.get('TIANJI_ADMIN_READ_SCOPES')) if admin_read_scopes is None else frozenset(s for s in admin_read_scopes if s in ADMIN_READ_SCOPES))
    # Role model (TJ-026.4 batch 1): server-side token-to-role mapping.
    # None means fall back to TIANJI_ADMIN_ROLE_TOKENS (comma list of
    # token:role pairs); an empty mapping means roles are not configured.
    app.state.admin_role_tokens = (parse_admin_role_tokens(os.environ.get('TIANJI_ADMIN_ROLE_TOKENS')) if admin_role_tokens is None else dict(admin_role_tokens))
    # Append-only audit log skeleton (TJ-026.4 batch 1): one per app
    # instance, process memory. Every write attempt is recorded here.
    app.state.audit_log = AuditLog()
    # Draft store (TJ-026.4 batch 2): one per app instance, process
    # memory — same lifecycle decision as the audit skeleton. Drafts
    # are lost on restart; every draft response says so (STORAGE_NOTE).
    app.state.draft_store = DraftStore()
    origins=[origin.strip() for origin in os.environ.get('TIANJI_CORS_ORIGINS','').split(',') if origin.strip()]
    if origins:app.add_middleware(CORSMiddleware,allow_origins=origins,allow_methods=['GET','POST'],allow_headers=['Content-Type','Authorization'])

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
        payload=load_catalog(ROOT);path=ROOT/'build/production_rag.jsonl'
        rag_ready=path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest()==payload['retrieval_index_sha256']
        return {'status':'ok','engine':'ready','domains':list(PROVIDERS),
                'production_runtime':'reviewed','rag_ready':rag_ready,
                'explanation_configured':app.state.provider is not None or provider_configured()}

    @app.get('/api/v1/capabilities',tags=['system'])
    def capabilities():
        resolver=EvidenceResolver()
        return {'api_version':'v1','default_mode':'production','ai_may_compute_chart':False,
            'explanation':{'provider_drivers':list(DRIVERS),'configured':app.state.provider is not None or provider_configured(),'keys_in_request':False,'prompt_versions':list(PROMPTS),'default_prompt':os.environ.get('TIANJI_EXPLANATION_PROMPT_VERSION',DEFAULT_PROMPT),'automatic_release_allowed':False,'production_prompt_versions':[DEFAULT_PROMPT]},
            'domains':[{'domain':domain,'variants':[c['variant']],'default_variant':c['variant'],
                        'scope':c.get('scope',''),'limitations':c.get('unresolved',[]),
                        'example':{'domain':domain,'variant':c['variant'],'input':EXAMPLES[domain],'explain':False,'mode':'production'}}
                       for domain,c in sorted(resolver.contracts.items())]}

    @app.get('/api/v1/scenarios',tags=['scenarios'])
    def scenarios():
        return {'api_version':'v1','scenarios':scenario_registry()}

    def require_admin_read_token(authorization,scope=None):
        outcome,detail=resolve_admin_access(app.state.admin_read_token,app.state.admin_read_scopes,authorization,scope)
        if outcome=='not_configured':
            raise HTTPException(503,detail={'code':'admin_auth_not_configured','message':'Admin read access is not configured'})
        if outcome=='unauthorized':
            if detail=='missing':
                raise HTTPException(401,detail={'code':'admin_unauthorized','message':'Admin bearer token required'},headers={'WWW-Authenticate':'Bearer'})
            raise HTTPException(401,detail={'code':'admin_unauthorized','message':'Invalid admin bearer token'},headers={'WWW-Authenticate':'Bearer'})
        if outcome=='forbidden':
            raise HTTPException(403,detail={'code':'admin_forbidden','message':f'Admin token scope does not include {detail}'})

    def require_role(authorization, operation):
        # TJ-026.4 batch 1: role-gated write checkpoint. Every attempt is
        # audited (allowed or denied); `who` is a role name or 'unknown',
        # never a raw token. 403 reuses the admin_forbidden semantics.
        outcome, detail = resolve_role_access(app.state.admin_role_tokens, authorization, operation)
        what = f'write_probe:{operation}'
        if outcome == 'not_configured':
            app.state.audit_log.record('unknown', what, 'denied', 'not_configured')
            raise HTTPException(503, detail={'code': 'admin_role_not_configured', 'message': 'Admin role access is not configured'})
        if outcome == 'unauthorized':
            app.state.audit_log.record('unknown', what, 'denied', detail)
            if detail == 'missing':
                raise HTTPException(401, detail={'code': 'admin_unauthorized', 'message': 'Admin bearer token required'}, headers={'WWW-Authenticate': 'Bearer'})
            raise HTTPException(401, detail={'code': 'admin_unauthorized', 'message': 'Invalid admin bearer token'}, headers={'WWW-Authenticate': 'Bearer'})
        if outcome == 'forbidden':
            app.state.audit_log.record(_role_name_for(authorization), what, 'denied', 'forbidden')
            raise HTTPException(403, detail={'code': 'admin_forbidden', 'message': f'Admin role does not allow {operation}'})
        app.state.audit_log.record(detail, what, 'allowed')
        return detail

    def _role_name_for(authorization):
        # Best-effort role lookup for audit records of denied attempts
        # (the credential was valid, only the operation was forbidden).
        if not authorization or not authorization.startswith('Bearer '):
            return 'unknown'
        supplied = authorization[len('Bearer '):]
        for token, role in app.state.admin_role_tokens.items():
            if secrets.compare_digest(supplied, token):
                return role
        return 'unknown'

    def check_draft_role(authorization, operation, what):
        # TJ-026.4 batch 2: like require_role, but the caller records
        # the 'allowed' entry only after the business step succeeds, so
        # one draft attempt leaves exactly one audit record whether it
        # succeeds (allowed) or fails at the business step (denied).
        # Denied auth attempts are recorded here, as in batch 1.
        outcome, detail = resolve_role_access(app.state.admin_role_tokens, authorization, operation)
        if outcome == 'not_configured':
            app.state.audit_log.record('unknown', what, 'denied', 'not_configured')
            raise HTTPException(503, detail={'code': 'admin_role_not_configured', 'message': 'Admin role access is not configured'})
        if outcome == 'unauthorized':
            app.state.audit_log.record('unknown', what, 'denied', detail)
            if detail == 'missing':
                raise HTTPException(401, detail={'code': 'admin_unauthorized', 'message': 'Admin bearer <redacted> required'}, headers={'WWW-Authenticate': 'Bearer'})
            raise HTTPException(401, detail={'code': 'admin_unauthorized', 'message': 'Invalid admin bearer <redacted>'}, headers={'WWW-Authenticate': 'Bearer'})
        if outcome == 'forbidden':
            app.state.audit_log.record(_role_name_for(authorization), what, 'denied', 'forbidden')
            raise HTTPException(403, detail={'code': 'admin_forbidden', 'message': f'Admin role does not allow {operation}'})
        return detail

    def require_valid_role(authorization):
        # TJ-026.4 batch 2: draft reads (list/get) need a valid role
        # token but no write operation, and are not audited: only write
        # attempts leave audit traces (batch-1 rule).
        if not app.state.admin_role_tokens:
            raise HTTPException(503, detail={'code': 'admin_role_not_configured', 'message': 'Admin role access is not configured'})
        role = _role_name_for(authorization)
        if role == 'unknown':
            if not authorization or not authorization.startswith('Bearer ') or not authorization[len('Bearer '):]:
                raise HTTPException(401, detail={'code': 'admin_unauthorized', 'message': 'Admin bearer <redacted> required'}, headers={'WWW-Authenticate': 'Bearer'})
            raise HTTPException(401, detail={'code': 'admin_unauthorized', 'message': 'Invalid admin bearer <redacted>'}, headers={'WWW-Authenticate': 'Bearer'})
        return role

    def require_internal_execution(authorization):
        # Detailed Evidence / internal trace is only callable with a separate
        # server-held credential in the sealed backend deployment.
        if os.environ.get('TIANJI_RUNTIME_MODE') != 'sealed':
            return
        configured=os.environ.get('TIANJI_INTERNAL_EXECUTE_TOKEN')
        if not configured:
            raise HTTPException(503,detail={'code':'internal_execution_not_configured'})
        if (not authorization or not authorization.startswith('Bearer ')
                or not secrets.compare_digest(authorization[7:],configured)):
            raise HTTPException(401,detail={'code':'internal_execution_unauthorized'},
                                headers={'WWW-Authenticate':'Bearer'})

    @app.post('/api/v1/dream/culture',response_model=PublicDreamCultureResponse,
              tags=['public-dream'])
    async def public_dream_culture(request: PublicDreamCultureRequest):
        # This is a distinct public projection, not an alias to the internal research API.
        # Never expose source refs, canonical paths, entity/rule IDs, raw text or trace.
        if len(request.dream_text.strip()) < 2:
            raise HTTPException(422,detail={'code':'invalid_dream_input',
                                            'message':'Describe the dream in 2–500 characters'})
        try:
            reviewed = await run_in_threadpool(retrieve_dream_culture, request.dream_text.strip())
        except RetrievalUnavailable:
            raise HTTPException(503,detail={'code':'reviewed_retrieval_unavailable',
                                            'message':'Reviewed dream lookup temporarily unavailable'})
        except (ValueError,TypeError):
            raise HTTPException(422,detail={'code':'invalid_dream_input',
                                            'message':'Invalid dream narrative'})
        if (reviewed.get('mode') != 'research' or reviewed.get('public_enabled') is not False
                or reviewed.get('ai_enabled') is not False or reviewed.get('chart_generated') is not False):
            raise HTTPException(503,detail={'code':'dream_review_contract_mismatch',
                                            'message':'Reviewed cultural lookup unavailable'})
        matches=[]
        for candidate in reviewed['matched_interpretations']:
            if (candidate.get('match_kind') != 'reviewed_cultural_scene_retrieval'
                    or candidate.get('personal_prediction') is not False
                    or not candidate.get('evidence_ids')
                    or not all(eid in reviewed['evidence'] for eid in candidate['evidence_ids'])):
                raise HTTPException(503,detail={'code':'dream_evidence_contract_mismatch',
                                                'message':'Reviewed cultural lookup unavailable'})
            # Only echo exact portions of this caller's narrative that the
            # reviewed scene matcher actually marked as input evidence.
            # Reject malformed positions rather than claiming an unmatched scene.
            matched_texts = []
            for hit in candidate.get('input_matches', []):
                for span in hit.get('input_spans', []):
                    start, end, quote = span.get('start'), span.get('end'), span.get('text')
                    if (type(start) is not int or type(end) is not int
                            or not isinstance(quote, str) or not quote
                            or start < 0 or end > len(request.dream_text.strip())
                            or end <= start or request.dream_text.strip()[start:end] != quote):
                        raise HTTPException(503,detail={'code':'dream_input_evidence_mismatch',
                                                        'message':'Reviewed cultural lookup unavailable'})
                    if quote not in matched_texts:
                        matched_texts.append(quote)
            if not matched_texts:
                raise HTTPException(503,detail={'code':'dream_input_evidence_missing',
                                                'message':'Reviewed cultural lookup unavailable'})
            matches.append(PublicDreamCultureMatch(
                scene=candidate['scene'],
                matched_texts=matched_texts,
                cultural_reading=candidate['interpretation'],
                short_quote=candidate['original_text_short_quote'],
                source_title='《周公解梦》固定电子本',
                evidence_level=candidate['evidence_level'],
            ))
        # A mention is never a review or interpretation. Only project fixed
        # topic labels and exact caller-owned substrings; no pending sources,
        # source IDs, internal evidence, or raw source bodies enter the response.
        input_topics = []
        for item in reviewed.get('unreviewed_input_topics', []):
            if (not isinstance(item, dict)
                    or item.get('label') not in ('考试', '怀孕', '结婚', '工作', '被追', '故人', '死亡')
                    or item.get('status') != 'input_observation_only'
                    or item.get('reviewed_interpretation_available') is not False
                    or item.get('evidence_ids') != []):
                raise HTTPException(503, detail={'code':'unreviewed_topic_contract_mismatch'})
            original = request.dream_text.strip()
            texts = []
            for span in item.get('input_spans', []):
                start, end, quote = span.get('start'), span.get('end'), span.get('text')
                if (type(start) is not int or type(end) is not int
                        or not isinstance(quote, str) or not quote or
                        start < 0 or end <= start or end > len(original)
                        or original[start:end] != quote):
                    raise HTTPException(503, detail={'code':'unreviewed_topic_input_mismatch'})
                if quote not in texts:
                    texts.append(quote)
            if not texts:
                raise HTTPException(503, detail={'code':'unreviewed_topic_input_missing'})
            input_topics.append(PublicDreamInputTopic(label=item['label'], matched_texts=texts))
        response=PublicDreamCultureResponse(
            status='reviewed_cultural_matches' if matches else 'no_reviewed_interpretation',
            matches=matches, unreviewed_topics=input_topics)
        return JSONResponse(content=response.model_dump(),headers={'Cache-Control':'no-store'})

    @app.post('/api/v1/admin/research/dream',tags=['admin'])
    async def admin_research_dream(request: AdminDreamResearchRequest,
                                   authorization: str | None = Header(default=None)):
        require_admin_read_token(authorization,scope='research')
        try:
            result = await run_in_threadpool(retrieve_dream_culture, request.dream_text)
        except RetrievalUnavailable:
            raise HTTPException(
                503,
                detail={'code':'reviewed_retrieval_unavailable',
                        'message':'Reviewed dream evidence index is unavailable'},
            )
        except (ValueError, TypeError):
            raise HTTPException(
                422,
                detail={'code':'invalid_dream_input',
                        'message':'Dream narrative is not valid for this research variant'},
            )
        if (result.get('mode') != 'research' or result.get('public_enabled') is not False
                or result.get('ai_enabled') is not False):
            raise HTTPException(503,detail={'code':'dream_research_contract_mismatch',
                                           'message':'Dream release restrictions not satisfied'})
        return {'api_version':'v1','read_only':True,'public_release':False,
                'research_only':True,'result':result}

    @app.get('/api/v1/admin/governance/conflicts',tags=['admin'])
    def admin_governance_conflicts(authorization: str | None = Header(default=None)):
        require_admin_read_token(authorization,scope='governance')
        return {
            'api_version':'v1',
            'read_only':True,
            'public_release':False,
            'records':school_conflicts(),
        }

    @app.get('/api/v1/admin/governance/rules',tags=['admin'])
    def admin_governance_rules(authorization: str | None = Header(default=None)):
        require_admin_read_token(authorization,scope='governance')
        return {
            'api_version':'v1',
            'read_only':True,
            'public_release':False,
            'records':reviewed_rules(),
        }

    @app.get('/api/v1/admin/governance/evidence',tags=['admin'])
    def admin_governance_evidence(authorization: str | None = Header(default=None)):
        require_admin_read_token(authorization,scope='governance')
        return {
            'api_version':'v1',
            'read_only':True,
            'public_release':False,
            'records':reviewed_evidence(),
        }

    @app.get('/api/v1/admin/governance/classics',tags=['admin'])
    def admin_governance_classics(authorization: str | None = Header(default=None)):
        require_admin_read_token(authorization,scope='governance')
        return {
            'api_version':'v1',
            'read_only':True,
            'public_release':False,
            'records':reviewed_classics(),
        }

    @app.get('/api/v1/admin/governance/chapters',tags=['admin'])
    def admin_governance_chapters(authorization: str | None = Header(default=None)):
        require_admin_read_token(authorization,scope='governance')
        return {
            'api_version':'v1',
            'read_only':True,
            'public_release':False,
            'records':reviewed_chapters(),
        }

    @app.get('/api/v1/admin/governance/terms',tags=['admin'])
    def admin_governance_terms(authorization: str | None = Header(default=None)):
        require_admin_read_token(authorization,scope='governance')
        return {
            'api_version':'v1',
            'read_only':True,
            'public_release':False,
            'records':reviewed_terms(),
        }

    @app.get('/api/v1/admin/governance/sources',tags=['admin'])
    def admin_governance_sources(authorization: str | None = Header(default=None)):
        require_admin_read_token(authorization,scope='governance')
        return {
            'api_version':'v1',
            'read_only':True,
            'public_release':False,
            'records':reviewed_sources(),
        }

    @app.get('/api/v1/admin/governance/layers',tags=['admin'])
    def admin_governance_layers(authorization: str | None = Header(default=None)):
        require_admin_read_token(authorization,scope='governance')
        return {
            'api_version':'v1',
            'read_only':True,
            'public_release':False,
            'records':reviewed_layers(),
        }

    @app.get('/api/v1/admin/governance/algorithms',tags=['admin'])
    def admin_governance_algorithms(authorization: str | None = Header(default=None)):
        require_admin_read_token(authorization,scope='governance')
        return {
            'api_version':'v1',
            'read_only':True,
            'public_release':False,
            'records':reviewed_algorithms(),
        }

    @app.get('/api/v1/admin/system/provider',tags=['admin'])
    def admin_provider_configuration(authorization: str | None = Header(default=None)):
        require_admin_read_token(authorization,scope='system')
        return {
            'api_version':'v1',
            'read_only':True,
            'public_release':False,
            'records':provider_configuration(),
        }

    @app.get('/api/v1/admin/system/prompts',tags=['admin'])
    def admin_prompt_registry(authorization: str | None = Header(default=None)):
        require_admin_read_token(authorization,scope='system')
        return {
            'api_version':'v1',
            'read_only':True,
            'public_release':False,
            'records':prompt_registry(),
        }

    @app.post('/api/v1/admin/write/probe', tags=['admin'])
    def admin_write_probe(request: AdminWriteProbeRequest, authorization: str | None = Header(default=None)):
        # TJ-026.4 batch 1: controlled write CHECKPOINT, not a business
        # write. No draft/approval/publish business exists behind this
        # endpoint; the response always reports write_applied=False so
        # the probe can never be mistaken for an applied write.
        role = require_role(authorization, request.operation)
        return {
            'api_version': 'v1',
            'probe': True,
            'operation': request.operation,
            'role': role,
            'write_applied': False,
            'note': 'Batch 1 checkpoint only: no draft, approval, publish, or rollback business exists yet.',
        }

    @app.get('/api/v1/admin/system/audit', tags=['admin'])
    def admin_audit_log(authorization: str | None = Header(default=None)):
        # TJ-026.4 batch 1: audit reads are gated by the TJ-026.3 read
        # token's system scope — an ordinary read role cannot read audit.
        require_admin_read_token(authorization, scope='system')
        return {
            'api_version': 'v1',
            'read_only': True,
            'public_release': False,
            'entries': app.state.audit_log.entries(),
        }

    def _draft_response(draft):
        # Draft records never carry audit content; the storage note is
        # part of every draft response so no client can mistake these
        # for durable records.
        return {'api_version': 'v1', 'draft': draft, 'storage': 'process_memory', 'storage_note': STORAGE_NOTE}

    @app.get('/api/v1/admin/drafts', tags=['admin'])
    def admin_draft_list(authorization: str | None = Header(default=None)):
        # TJ-026.4 batch 2: draft reads need a valid role token but no
        # write operation, and are not audited (batch-1 rule: only
        # write attempts leave traces).
        require_valid_role(authorization)
        return {'api_version': 'v1', 'drafts': app.state.draft_store.list(), 'storage': 'process_memory', 'storage_note': STORAGE_NOTE}

    @app.get('/api/v1/admin/drafts/{draft_id}', tags=['admin'])
    def admin_draft_get(draft_id: str, authorization: str | None = Header(default=None)):
        require_valid_role(authorization)
        draft = app.state.draft_store.get(draft_id)
        if draft is None:
            raise HTTPException(404, detail={'code': 'draft_not_found', 'message': f'No draft with id {draft_id}'})
        return _draft_response(draft)

    @app.post('/api/v1/admin/drafts', tags=['admin'])
    def admin_draft_create(request: AdminDraftCreateRequest, authorization: str | None = Header(default=None)):
        # TJ-026.4 batch 2: create a draft (role operation 'draft').
        role = check_draft_role(authorization, 'draft', 'draft:create')
        try:
            draft = app.state.draft_store.create(request.title, request.body, role)
        except InvalidDraftInputError as error:
            app.state.audit_log.record(role, 'draft:create', 'denied', 'invalid_input')
            raise HTTPException(422, detail={'code': 'invalid_draft_input', 'message': str(error)}) from error
        app.state.audit_log.record(role, 'draft:create', 'allowed', draft['id'])
        return _draft_response(draft)

    @app.patch('/api/v1/admin/drafts/{draft_id}', tags=['admin'])
    def admin_draft_edit(draft_id: str, request: AdminDraftEditRequest, authorization: str | None = Header(default=None)):
        # TJ-026.4 batch 2: edit in place, legal only in 'draft' status.
        what = f'draft:edit:{draft_id}'
        role = check_draft_role(authorization, 'draft', what)
        if request.title is None and request.body is None:
            app.state.audit_log.record(role, what, 'denied', 'invalid_input')
            raise HTTPException(422, detail={'code': 'invalid_draft_input', 'message': 'Nothing to edit: supply title and/or body'})
        try:
            draft = app.state.draft_store.edit(draft_id, title=request.title, body=request.body, role=role)
        except DraftNotFoundError:
            app.state.audit_log.record(role, what, 'denied', 'draft_not_found')
            raise HTTPException(404, detail={'code': 'draft_not_found', 'message': f'No draft with id {draft_id}'})
        except InvalidTransitionError as error:
            app.state.audit_log.record(role, what, 'denied', 'invalid_transition')
            raise HTTPException(422, detail={'code': 'invalid_draft_transition', 'message': str(error)}) from error
        except InvalidDraftInputError as error:
            app.state.audit_log.record(role, what, 'denied', 'invalid_input')
            raise HTTPException(422, detail={'code': 'invalid_draft_input', 'message': str(error)}) from error
        app.state.audit_log.record(role, what, 'allowed')
        return _draft_response(draft)

    @app.post('/api/v1/admin/drafts/{draft_id}/rollback', tags=['admin'])
    def admin_draft_rollback(draft_id: str, request: AdminDraftRollbackRequest, authorization: str | None = Header(default=None)):
        # TJ-026.4 batch 3: rollback to a version snapshot. This route
        # MUST stay registered before the generic /{action} route below:
        # otherwise 'rollback' would be captured as an action and rejected
        # as unknown (fail-closed, but the dedicated endpoint would be
        # unreachable). Role operation 'rollback' is publisher-only
        # (batch-1 WRITE_OPERATIONS); the store enforces the rest:
        # rejected stays terminal, unknown versions fail closed, and
        # every rollback lands in 'draft' status. The audit record here
        # is the compensating record: appended only, carrying the draft
        # id and restored version and no draft content, exactly like the
        # batch-1 rule that audit records never contain draft content.
        what = f'draft:rollback:{draft_id}'
        role = check_draft_role(authorization, 'rollback', what)
        try:
            draft = app.state.draft_store.rollback(draft_id, request.version, role)
        except DraftNotFoundError:
            app.state.audit_log.record(role, what, 'denied', 'draft_not_found')
            raise HTTPException(404, detail={'code': 'draft_not_found', 'message': f'No draft with id {draft_id}'})
        except InvalidTransitionError as error:
            app.state.audit_log.record(role, what, 'denied', 'invalid_transition')
            raise HTTPException(422, detail={'code': 'invalid_draft_transition', 'message': str(error)}) from error
        app.state.audit_log.record(role, what, 'allowed', f'version:{request.version}')
        return _draft_response(draft)

    @app.post('/api/v1/admin/drafts/{draft_id}/{action}', tags=['admin'])
    def admin_draft_act(draft_id: str, action: str, authorization: str | None = Header(default=None)):
        # TJ-026.4 batch 2: submit/approve/reject/publish. The action
        # maps to a batch-1 write operation (DRAFT_ACTION_OPERATION);
        # unknown actions are rejected before any state is touched
        # (fail-closed) and audited as denied attempts.
        operation = DRAFT_ACTION_OPERATION.get(action)
        what = f'draft:{action}:{draft_id}'
        if operation is None:
            if not app.state.admin_role_tokens:
                app.state.audit_log.record('unknown', what, 'denied', 'not_configured')
                raise HTTPException(503, detail={'code': 'admin_role_not_configured', 'message': 'Admin role access is not configured'})
            app.state.audit_log.record(_role_name_for(authorization), what, 'denied', 'unknown_action')
            raise HTTPException(403, detail={'code': 'admin_forbidden', 'message': f'Unknown draft action {action}'})
        role = check_draft_role(authorization, operation, what)
        try:
            draft = app.state.draft_store.transition(draft_id, action, role)
        except DraftNotFoundError:
            app.state.audit_log.record(role, what, 'denied', 'draft_not_found')
            raise HTTPException(404, detail={'code': 'draft_not_found', 'message': f'No draft with id {draft_id}'})
        except InvalidTransitionError as error:
            app.state.audit_log.record(role, what, 'denied', 'invalid_transition')
            raise HTTPException(422, detail={'code': 'invalid_draft_transition', 'message': str(error)}) from error
        app.state.audit_log.record(role, what, 'allowed')
        return _draft_response(draft)

    @app.post('/api/v1/scenarios/public',response_model=ScenarioExecuteResponse,tags=['public-execution'])
    async def public_scenario_request(request:ScenarioExecuteRequest,response:Response):
        available={item['id']:item for item in scenario_registry()}
        scenario=available.get(request.scenario_id)
        if scenario is None or scenario['status'] not in PUBLIC_SCENARIO_STATES:
            raise HTTPException(422,detail={'code':'unsupported_public_scenario'})
        try:
            raw=await run_in_threadpool(execute_scenario,request.scenario_id,dict(request.input))
        except RuntimeUnavailable:raise
        except (ValueError,TypeError) as error:
            raise HTTPException(422,detail={'code':'invalid_scenario_input','message':str(error)}) from error
        response.headers['Cache-Control']='no-store'
        return ScenarioExecuteResponse.model_validate(project_execution(raw))

    @app.post('/api/v1/scenarios/execute',response_model=ScenarioExecuteResponse,tags=['scenarios'])
    async def execute_scenario_request(request:ScenarioExecuteRequest,
                                       authorization: str | None = Header(default=None)):
        require_internal_execution(authorization)
        try:
            return ScenarioExecuteResponse.model_validate(
                await run_in_threadpool(execute_scenario,request.scenario_id,dict(request.input))
            )
        except (ValueError,TypeError) as error:
            raise HTTPException(422,detail={'code':'invalid_scenario_input','message':str(error)}) from error

    @app.post('/api/v1/public/execute',response_model=ExecuteResponse,tags=['public-execution'])
    async def public_execute_request(request:ExecuteRequest,response:Response):
        if request.domain not in PUBLIC_EXECUTION_DOMAINS or request.mode!='production' or request.explain:
            raise HTTPException(422,detail={'code':'unsupported_public_execution'})
        if 'research' in request.input:
            raise HTTPException(422,detail={'code':'invalid_input'})
        try:
            raw=await run_in_threadpool(execute,request.domain,dict(request.input),
                                        request.variant,allow_research=False)
        except RuntimeUnavailable:raise
        except (ValueError,TypeError) as error:
            raise HTTPException(422,detail={'code':'invalid_input','message':str(error)}) from error
        response.headers['Cache-Control']='no-store'
        return ExecuteResponse.model_validate(project_execution(response_for(raw).model_dump()))

    @app.post('/api/v1/execute',response_model=ExecuteResponse,tags=['execution'])
    async def execute_request(request:ExecuteRequest,
                              authorization: str | None = Header(default=None)):
        require_internal_execution(authorization)
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
            try:
                if raw.get('interpretation_contract', {}).get('ai_may_explain') is False:
                    raise ExplanationFailure('interpretation_not_authorized')
                selected_provider=app.state.provider if app.state.provider is not None else provider_from_environment()
                if selected_provider is None:raise ExplanationFailure('provider_not_configured')
                timeout=explanation_timeout if explanation_timeout is not None else timeout_from_environment()
                selected_prompt=os.environ.get('TIANJI_EXPLANATION_PROMPT_VERSION',DEFAULT_PROMPT)
                if request.mode=='production' and selected_prompt in ('explanation-prompt-v1','explanation-prompt-v3'):raise ExplanationFailure('prompt_not_production_eligible')
                service=ExplanationService(selected_provider,timeout=timeout,prompt_version=selected_prompt)
                result.explanation=ExplanationResponse.model_validate(await service.explain(copy.deepcopy(raw)))
                result.explanation_status='succeeded'
            except Exception as error:
                result.explanation_status='failed'
                result.explanation_error=error.code if isinstance(error,ExplanationFailure) else 'explanation_failed'
                result.warnings.append('解释暂不可用或未通过引用校验；确定性盘面、规则与证据仍正常返回。')
        return result

    return app

app=create_app()
