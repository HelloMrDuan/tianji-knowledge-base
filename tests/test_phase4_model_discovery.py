import asyncio,json,os,unittest
from unittest.mock import patch
import httpx
from tianji_kb.ai_providers import settings_from_environment,provider_configured
from tianji_kb.model_discovery import discover_model,advertised_candidates
from tianji_kb.explanation import ExplanationFailure

ENV={'TIANJI_AI_PROVIDER':'openai-compatible','TIANJI_AI_BASE_URL':'https://api.qnaigc.com/v1',
     'TIANJI_AI_API_KEY':'unit-only-credential','TIANJI_AI_MODEL':''}

class DiscoveryTests(unittest.TestCase):
    def settings(self,extra=None):
        with patch.dict(os.environ,{**ENV,**(extra or {})}):return settings_from_environment(require_model=False)
    def test_only_advertised_chat_models_are_selected_after_exact_json_probe(self):
        calls=[]
        def handler(request):
            calls.append(request)
            self.assertEqual(request.headers['authorization'],'Bearer unit-only-credential')
            if request.method=='GET':
                self.assertEqual(request.url.path,'/v1/models')
                return httpx.Response(200,json={'data':[{'id':'text-embedding-v1'},{'id':'qwen3.5-chat'},{'id':'other-chat'}]})
            body=json.loads(request.content);self.assertEqual(body['model'],'qwen3.5-chat')
            self.assertEqual(body['response_format'],{'type':'json_object'})
            self.assertNotIn('unit-only-credential',request.content.decode())
            return httpx.Response(200,json={'choices':[{'message':{'content':'{"probe":"tianji","value":7}'}}]})
        selected=asyncio.run(discover_model(settings=self.settings(),transport=httpx.MockTransport(handler)))
        self.assertEqual(selected['model'],'qwen3.5-chat');self.assertEqual(len(calls),2)
        self.assertEqual(selected['explanation_quality'],'not_evaluated');self.assertNotIn('unit-only-credential',json.dumps(selected))
    def test_unavailable_model_is_skipped_but_attempts_are_bounded(self):
        probes=[]
        def handler(request):
            if request.method=='GET':return httpx.Response(200,json={'data':[{'id':'qwen3.5-a'},{'id':'qwen3.5-b'},{'id':'qwen3.5-c'}]})
            model=json.loads(request.content)['model'];probes.append(model)
            if model.endswith('-b'):return httpx.Response(200,json={'choices':[{'message':{'content':'{"probe":"tianji","value":7}'}}]})
            return httpx.Response(400,json={'error':'unit-only-credential'})
        selected=asyncio.run(discover_model(settings=self.settings(),transport=httpx.MockTransport(handler)))
        self.assertEqual(selected['model'],'qwen3.5-b');self.assertEqual(selected['attempts'],2)
        self.assertNotIn('unit-only-credential',str(selected))
        with self.assertRaises(ExplanationFailure) as error:asyncio.run(discover_model(settings=self.settings(),transport=httpx.MockTransport(handler),max_attempts=1))
        self.assertEqual(error.exception.code,'no_compatible_model_verified')
    def test_domain_auth_or_server_failure_stops_without_guessing_or_leaking_body(self):
        for status in [401,403,503]:
            calls=[]
            def handler(request):calls.append(request);return httpx.Response(status,text='unit-only-credential')
            with self.assertRaises(ExplanationFailure) as error:asyncio.run(discover_model(settings=self.settings(),transport=httpx.MockTransport(handler)))
            self.assertEqual(error.exception.code,'model_discovery_unavailable');self.assertEqual(len(calls),1)
            self.assertNotIn('unit-only-credential',str(error.exception))
    def test_non_json_tools_changed_value_and_extra_fields_do_not_verify_model(self):
        for message in [{'content':'not JSON'}, {'content':'{"probe":"tianji","value":true}'},
                        {'content':'{"probe":"tianji","value":7,"extra":true}'},
                        {'content':'{"probe":"tianji","value":7}','tool_calls':[{}]}]:
            def handler(request):
                if request.method=='GET':return httpx.Response(200,json={'data':[{'id':'chat-one'}]})
                return httpx.Response(200,json={'choices':[{'message':message}]})
            with self.assertRaises(ExplanationFailure):asyncio.run(discover_model(settings=self.settings(),transport=httpx.MockTransport(handler)))
    def test_discovery_can_read_list_without_model_but_execution_still_requires_model(self):
        with patch.dict(os.environ,ENV):
            self.assertFalse(provider_configured());self.assertTrue(settings_from_environment(require_model=False))
            with self.assertRaises(ExplanationFailure):settings_from_environment()
    def test_model_ids_cannot_include_secret_or_arbitrary_url_parameters(self):
        ids=advertised_candidates({'data':[{'id':'safe-chat'},{'id':'unit-only-credential'}, {'id':'https://bad/?key=secret'},
                                   {'id':'chat\nmalicious'},{'id':'embedding-model'}, {'id':True}]},'unit-only-credential')
        self.assertEqual(ids,['safe-chat'])
    def test_complete_endpoint_supported_and_unsafe_configuration_rejected(self):
        paths=[]
        def handler(request):
            paths.append(request.url.path)
            if request.method=='GET':return httpx.Response(200,json={'data':[{'id':'safe-chat'}]})
            return httpx.Response(200,json={'choices':[{'message':{'content':'{"probe":"tianji","value":7}'}}]})
        asyncio.run(discover_model(settings=self.settings({'TIANJI_AI_BASE_URL':'https://api.qnaigc.com/v1/chat/completions'}),transport=httpx.MockTransport(handler)))
        self.assertEqual(paths,['/v1/models','/v1/chat/completions'])
        with self.assertRaises(ExplanationFailure):self.settings({'TIANJI_AI_BASE_URL':'https://user:secret@api.qnaigc.com/v1'})
