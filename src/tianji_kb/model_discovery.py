"""Choose only an advertised model that actually passes a bounded JSON chat probe."""
import json,re
from urllib.parse import urlsplit
from .ai_providers import HttpProvider,settings_from_environment
from .explanation import ExplanationFailure

PREFERENCES=('qwen3.5','qwen3-max','deepseek-v3','deepseek-chat','qwen','kimi','glm','gpt','claude')
NON_CHAT=re.compile(r'embed|rerank|whisper|tts|image|flux|sdxl|stable-diffusion|sora|video|dall-e|asr',re.I)
MODEL_ID=re.compile(r'[A-Za-z0-9][A-Za-z0-9_./:-]{0,159}')

def advertised_candidates(payload,key):
    if not isinstance(payload,dict) or not isinstance(payload.get('data'),list):
        raise ExplanationFailure('model_list_invalid')
    ids=set()
    for row in payload['data']:
        if not isinstance(row,dict):continue
        model=row.get('id')
        if not isinstance(model,str) or not MODEL_ID.fullmatch(model) or key in model or NON_CHAT.search(model):continue
        ids.add(model)
    def rank(model):
        return (next((i for i,prefix in enumerate(PREFERENCES) if prefix in model.lower()),len(PREFERENCES)),model)
    return sorted(ids,key=rank)

async def discover_model(*,settings=None,transport=None,max_attempts=3):
    if type(max_attempts) is not int or not 1<=max_attempts<=5:raise ExplanationFailure('discovery_limit_invalid')
    settings=settings if settings is not None else settings_from_environment(require_model=False)
    if not settings or settings['driver']!='openai-compatible':raise ExplanationFailure('provider_not_configured')
    client=HttpProvider(settings,transport=transport)
    base=settings['endpoint'].rstrip('/')
    if base.endswith('/chat/completions'):base=base[:-len('/chat/completions')]
    try:payload=await client.get(base+'/models')
    except Exception as error:raise ExplanationFailure('model_discovery_unavailable') from error
    candidates=advertised_candidates(payload,settings['key']);failures=[]
    for model in candidates[:max_attempts]:
        try:
            response=await client.post(base+'/chat/completions',{'model':model,'temperature':0,'max_tokens':256,
                'response_format':{'type':'json_object'},'messages':[
                    {'role':'system','content':'Return only the exact JSON object requested. No markdown or extra fields.'},
                    {'role':'user','content':'Return {"probe":"tianji","value":7} exactly.'}]})
            message=response['choices'][0]['message']
            if message.get('tool_calls'):raise ValueError('Tools prohibited')
            reply=json.loads(message['content'])
            if type(reply) is not dict or set(reply)!={'probe','value'} or reply['probe']!='tianji' or type(reply['value']) is not int or reply['value']!=7:
                raise ValueError('JSON probe mismatch')
        except Exception:
            # Never expose provider bodies/exceptions or credential values.
            failures.append({'model':model,'code':'json_chat_probe_failed'});continue
        return {'model':model,'provider':'openai-compatible','provider_host':urlsplit(base).hostname,
                'advertised_chat_candidates':len(candidates),'attempts':len(failures)+1,'failed_probes':failures,
                'json_chat_probe':'passed','explanation_quality':'not_evaluated',
                'qualification':'Connection/JSON probe only; run the fixed explanation suite and semantic review'}
    raise ExplanationFailure('no_compatible_model_verified')
