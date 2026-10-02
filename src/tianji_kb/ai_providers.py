"""Replaceable HTTP providers; credentials come exclusively from process environment."""
import json,math,os
from urllib.parse import urlsplit
import httpx
from .explanation import ExplanationFailure

DRIVERS=('disabled','json-http','openai-compatible')


def timeout_from_environment():
    try:value=float(os.environ.get('TIANJI_AI_TIMEOUT_SECONDS','20'))
    except ValueError as error:raise ExplanationFailure('provider_configuration_invalid') from error
    if not math.isfinite(value) or not 0<value<=120:raise ExplanationFailure('provider_configuration_invalid')
    return value


def settings_from_environment():
    driver=os.environ.get('TIANJI_AI_PROVIDER','disabled')
    if driver=='disabled':return None
    if driver not in DRIVERS:raise ExplanationFailure('provider_configuration_invalid')
    endpoint=os.environ.get('TIANJI_AI_BASE_URL','')
    key=os.environ.get('TIANJI_AI_API_KEY','')
    model=os.environ.get('TIANJI_AI_MODEL','')
    try:max_tokens=int(os.environ.get('TIANJI_AI_MAX_OUTPUT_TOKENS','4096'))
    except ValueError as error:raise ExplanationFailure('provider_configuration_invalid') from error
    if not 256<=max_tokens<=16384:raise ExplanationFailure('provider_configuration_invalid')
    parsed=urlsplit(endpoint)
    if not endpoint or not key or (driver=='openai-compatible' and not model):
        raise ExplanationFailure('provider_not_configured')
    if parsed.scheme not in ('http','https') or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ExplanationFailure('provider_configuration_invalid')
    if parsed.scheme=='http' and parsed.hostname not in ('127.0.0.1','localhost','::1'):
        raise ExplanationFailure('provider_configuration_invalid')
    return {'driver':driver,'endpoint':endpoint,'key':key,'model':model,'timeout':timeout_from_environment(),'max_tokens':max_tokens}


def provider_configured():
    try:return settings_from_environment() is not None
    except (ExplanationFailure,ValueError):return False

class HttpProvider:
    def __init__(self,settings,*,transport=None):
        self.settings=settings;self.transport=transport
    async def post(self,url,body):
        # Preserve inherited TLS CA and proxy configuration; never follow credential redirects.
        async with httpx.AsyncClient(timeout=self.settings['timeout'],trust_env=True,transport=self.transport,
                                     follow_redirects=False) as client:
            async with client.stream('POST',url,json=body,headers={'Authorization':'Bearer '+self.settings['key'],
                    'Accept':'application/json'}) as response:
                response.raise_for_status()
                if 300<=response.status_code<400:raise ValueError('Provider redirects are not followed')
                parts=[];size=0
                async for block in response.aiter_bytes():
                    size+=len(block)
                    if size>262144:raise ValueError('Provider response exceeds allowed size')
                    parts.append(block)
                return json.loads(b''.join(parts))

class JsonHttpProvider(HttpProvider):
    async def explain(self,context):
        return await self.post(self.settings['endpoint'],{'context':context,'instruction':context['instructions'],
            'response_schema':context['response_schema'],'model':self.settings['model']})

class OpenAICompatibleProvider(HttpProvider):
    async def explain(self,context):
        endpoint=self.settings['endpoint'].rstrip('/')
        if not endpoint.endswith('/chat/completions'):endpoint+='/chat/completions'
        response=await self.post(endpoint,{'model':self.settings['model'],'temperature':0,'max_tokens':self.settings['max_tokens'],
            'response_format':{'type':'json_object'},'messages':[{'role':'system','content':context['instructions']},
                {'role':'user','content':json.dumps(context,ensure_ascii=False)}]})
        message=response['choices'][0]['message']
        if message.get('tool_calls'):raise ValueError('Provider tool calls are not supported')
        return json.loads(message['content'])


def provider_from_environment():
    settings=settings_from_environment()
    if settings is None:return None
    factory=JsonHttpProvider if settings['driver']=='json-http' else OpenAICompatibleProvider
    return factory(settings)
