import asyncio,copy,json,os,unittest
from unittest.mock import patch
import httpx
from fastapi.testclient import TestClient
from tianji_kb.ai_providers import provider_from_environment,provider_configured,JsonHttpProvider,OpenAICompatibleProvider
from tianji_kb.api import create_app,EXAMPLES
from tianji_kb.engine import execute
from tianji_kb.explanation import context_for,validate_reply,ExplanationFailure
from tianji_kb.rag_context import CanonicalRetriever

ENV={'TIANJI_AI_PROVIDER':'json-http','TIANJI_AI_BASE_URL':'https://model.example.test/explain',
     'TIANJI_AI_API_KEY':'test-only-key','TIANJI_AI_MODEL':'test-model','TIANJI_AI_TIMEOUT_SECONDS':'2'}

from phase4_helpers import valid_reply

class ProviderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw=execute('yijing',EXAMPLES['yijing']);cls.context=context_for(raw,CanonicalRetriever().retrieve(raw))
    def test_both_http_adapters_send_env_credentials_and_valid_context(self):
        for driver in ['json-http','openai-compatible']:
            with patch.dict(os.environ,{**ENV,'TIANJI_AI_PROVIDER':driver}):provider=provider_from_environment()
            seen=[]
            def handler(request):
                seen.append(request);self.assertEqual(request.headers['authorization'],'Bearer test-only-key')
                body=json.loads(request.content)
                if driver=='json-http':context=body['context'];return httpx.Response(200,json=valid_reply(context))
                context=json.loads(body['messages'][1]['content'])
                self.assertEqual(request.url.path,'/explain/chat/completions')
                return httpx.Response(200,json={'choices':[{'message':{'content':json.dumps(valid_reply(context))}}]})
            provider.transport=httpx.MockTransport(handler)
            reply=asyncio.run(provider.explain(copy.deepcopy(self.context)))
            self.assertTrue(validate_reply(reply,self.context)['claims']);self.assertEqual(len(seen),1)
            self.assertNotIn('test-only-key',seen[0].content.decode())
    def test_api_uses_environment_adapter_after_rag_without_vendor_binding(self):
        with patch.dict(os.environ,ENV):provider=provider_from_environment()
        provider.transport=httpx.MockTransport(lambda request:httpx.Response(200,json=valid_reply(json.loads(request.content)['context'])))
        with patch('tianji_kb.api.provider_from_environment',return_value=provider):
            data=TestClient(create_app()).post('/api/v1/execute',json={'domain':'yijing','input':EXAMPLES['yijing'],'explain':True}).json()
        self.assertEqual(data['explanation_status'],'succeeded');self.assertNotIn('test-only-key',json.dumps(data))
    def test_false_does_not_read_or_construct_provider_configuration(self):
        with patch('tianji_kb.api.provider_from_environment',side_effect=AssertionError('No provider construction')):
            response=TestClient(create_app()).post('/api/v1/execute',json={'domain':'yijing','input':EXAMPLES['yijing']})
        self.assertEqual(response.status_code,200);self.assertEqual(response.json()['explanation_status'],'disabled')
    def test_invalid_configuration_fails_explanation_only_and_never_echoes_key(self):
        for changes in [{'TIANJI_AI_BASE_URL':'http://external.example/explain'},
                        {'TIANJI_AI_BASE_URL':'https://user:secret@model.example/explain'},
                        {'TIANJI_AI_TIMEOUT_SECONDS':'NaN'},{'TIANJI_AI_PROVIDER':'unknown'}]:
            with patch.dict(os.environ,{**ENV,**changes}):
                self.assertFalse(provider_configured())
                response=TestClient(create_app()).post('/api/v1/execute',json={'domain':'yijing','input':EXAMPLES['yijing'],'explain':True})
                self.assertEqual(response.status_code,200);self.assertEqual(response.json()['explanation_status'],'failed')
                self.assertTrue(response.json()['chart']);self.assertNotIn('test-only-key',response.text)
        with patch.dict(os.environ,{'TIANJI_AI_PROVIDER':'disabled'}):self.assertIsNone(provider_from_environment())
    def test_http_failure_redirect_and_large_response_are_not_accepted(self):
        with patch.dict(os.environ,ENV):provider=provider_from_environment()
        for response in [httpx.Response(401,json={'error':'secret'}),httpx.Response(302,headers={'location':'https://other.example'}),httpx.Response(200,content=b'x'*262145)]:
            provider.transport=httpx.MockTransport(lambda request:response)
            with self.assertRaises(Exception):asyncio.run(provider.explain(copy.deepcopy(self.context)))
    def test_provider_tool_calls_do_not_create_calculation_path(self):
        with patch.dict(os.environ,{**ENV,'TIANJI_AI_PROVIDER':'openai-compatible'}):provider=provider_from_environment()
        provider.transport=httpx.MockTransport(lambda request:httpx.Response(200,json={'choices':[{'message':{'tool_calls':[{}],'content':'{}'}}]}))
        with self.assertRaises(ValueError):asyncio.run(provider.explain(copy.deepcopy(self.context)))
    def test_cors_and_provider_capabilities_are_explicit(self):
        with patch.dict(os.environ,{'TIANJI_CORS_ORIGINS':'https://frontend.example','TIANJI_AI_PROVIDER':'disabled'}):
            client=TestClient(create_app())
            allowed=client.options('/api/v1/execute',headers={'Origin':'https://frontend.example','Access-Control-Request-Method':'POST'})
            self.assertEqual(allowed.headers['access-control-allow-origin'],'https://frontend.example')
            rejected=client.options('/api/v1/execute',headers={'Origin':'https://other.example','Access-Control-Request-Method':'POST'})
            self.assertNotIn('access-control-allow-origin',rejected.headers)
            self.assertIn('json-http',client.get('/api/v1/capabilities').json()['explanation']['provider_drivers'])
            self.assertTrue(client.get('/health').json()['rag_ready'])
    def test_real_http_adapter_loop_for_all_registered_domains_and_failure_downgrade(self):
        import threading
        from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
        calls=[];fail=[False]
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*args):pass
            def do_POST(self):
                body=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                context=body['context'];calls.append(context)
                response={'error':'unavailable'} if fail[0] else valid_reply(context)
                data=json.dumps(response).encode()
                self.send_response(503 if fail[0] else 200)
                self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(data)))
                self.end_headers();self.wfile.write(data)
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
        try:
            with patch.dict(os.environ,{**ENV,'TIANJI_AI_BASE_URL':f'http://127.0.0.1:{server.server_port}/explain'}):
                client=TestClient(create_app())
                for domain in EXAMPLES:
                    body={'domain':domain,'input':EXAMPLES[domain],'explain':True}
                    response=client.post('/api/v1/execute',json=body)
                    self.assertEqual(response.status_code,200)
                    self.assertEqual(response.json()['explanation_status'],'succeeded',response.text)
                    self.assertTrue(calls[-1]['rag']);self.assertEqual(calls[-1]['domain'],domain)
                self.assertEqual(len(calls),7)
                fail[0]=True
                response=client.post('/api/v1/execute',json={'domain':'yijing','input':EXAMPLES['yijing'],'explain':True})
                self.assertEqual(response.status_code,200);self.assertEqual(response.json()['explanation_error'],'provider_failed')
                self.assertTrue(response.json()['chart']);self.assertTrue(response.json()['evidence'])
        finally:
            server.shutdown();server.server_close();worker.join(timeout=2)
