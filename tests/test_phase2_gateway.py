import copy,json,unittest
from unittest.mock import patch
from tianji_kb.engine import execute,PROVIDERS
from tianji_kb.knowledge import read_json
from tianji_kb.phase2_quality import validate_evidence,validate_source_audit
from tianji_kb.resolver import EvidenceResolver

class GatewayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.resolver=EvidenceResolver()
    def test_each_domain_golden_uses_gateway_and_citation_closed_matches(self):
        for domain in PROVIDERS:
            fixture=read_json(self.resolver.root/f'data/canonical/{domain}/phase2_golden.json')['cases'][0]
            output=execute(domain,fixture['input'])
            self.assertTrue(output['deterministic'])
            self.assertFalse(output['interpretation_contract']['ai_may_compute_chart'])
            fired={m['rule_id'] for m in output['rule_matches']}
            self.assertEqual(fired,{s['rule_id'] for s in output['trace']})
            for match in output['rule_matches']:
                self.assertEqual(match['variant'],output['variant'])
                for evidence_id in match.get('evidence_ids',[]):
                    self.assertIn(evidence_id,output['evidence'])
            self.assertEqual(execute(domain,fixture['input']),output)
    def test_closed_variants_domains_and_research_epochs(self):
        with self.assertRaises(ValueError):execute('taiyi',{})
        with self.assertRaises(ValueError):execute('yijing',{'bits':'111111'},'AI-generated')
        with self.assertRaises(ValueError):execute('yijing',{'bits':'111111','variant':'x'})
        with self.assertRaises(ValueError):execute('fengshui',{'degrees':0,'year':2024,'epoch_year':1864,'research':True})
        result=execute('fengshui',{'degrees':0,'year':2024,'epoch_year':1864,'research':True},allow_research=True)
        self.assertEqual(result['mode'],'research')
        self.assertFalse(result['result']['period']['production_eligible'])
    def test_source_duplicates_and_unverified_upgrades_fail(self):
        audit=read_json(self.resolver.root/'config/phase2_source_audit.json')
        fake=copy.deepcopy(audit)
        next(r for r in fake['lineages'] if r['source_id']=='ziwei.source.quanshu-phase2')['lineage_group']='separate-mirror'
        with self.assertRaises(ValueError):validate_source_audit(self.resolver,fake)
        fake=copy.deepcopy(audit);fake['claim_comparisons'][0]['independent_source_count']=2
        with self.assertRaises(ValueError):validate_source_audit(self.resolver,fake)
        resolver=copy.copy(self.resolver);resolver.sources=copy.deepcopy(resolver.sources)
        resolver.sources['liuyao.source.bushi']['evidence_level']='A'
        with self.assertRaises(ValueError):validate_source_audit(resolver,audit)
    def test_forged_supplementary_quotes_variants_and_source_rejected(self):
        target=self.resolver.root/'data/canonical/ziwei/phase2_evidence.json'
        original=read_json(target)
        for key,value in [('original_text','伪造原文'),('variants',['unreviewed']),('review_status','pending'),('rule_ids',['liuren.phase2.zeike'])]:
            fake=copy.deepcopy(original);fake['records'][0][key]=value
            def reader(path):return fake if path==target else read_json(path)
            with patch('tianji_kb.phase2_quality.read_json',side_effect=reader):
                with self.assertRaises(Exception):validate_evidence(self.resolver)
    def test_motion_does_not_claim_to_execute_strength_interpretation(self):
        rule=self.resolver.rule('liuyao.phase2.motion')
        self.assertEqual(rule['phase1_rule_refs'],['yijing.rule.r002'])
        refs=self.resolver.resolve('liuyao.phase2.motion',rule['variant'])
        self.assertTrue(any('動則必變' in r['original_text'] for r in refs))
    def test_shared_datetime_adapter_for_liuyao_and_liuren(self):
        value='2000-01-07T12:00:00+08:00'
        ly=execute('liuyao',{'value':value,'yao_values':[7]*6})
        self.assertEqual(ly['input_calendar']['day_ganzhi'],'甲子')
        self.assertEqual(ly['input_calendar']['month_ganzhi'],'丁丑')
        self.assertEqual(ly['result']['empty_branches'],['戌','亥'])
        lr=execute('liuren',{'value':value})
        self.assertEqual(lr['input_calendar']['hour_ganzhi'],'庚午')
        self.assertEqual(lr['result']['month_general']['branch'],'丑')
        with self.assertRaises(ValueError):execute('liuyao',{'value':value,'yao_values':[7]*6,'day_ganzhi':'甲子'})
    def test_ziwei_lunar_year_adapter_and_leap_scope(self):
        z=execute('ziwei',{'value':'1999-02-16T00:00:00+08:00','year_boundary':'lunar-new-year'})
        self.assertEqual(z['input_calendar']['lunar_year'],1999)
        self.assertEqual(z['input_calendar']['lunar_month'],1)
        self.assertEqual(z['input_calendar']['lunar_day'],1)
        self.assertEqual(z['result']['bureau'],{'element':'火','number':6})
        self.assertEqual(z['result']['major_stars']['紫微'],'酉')
        with self.assertRaises(ValueError):execute('ziwei',{'value':'1999-02-16T00:00:00+08:00'})
        with self.assertRaises(ValueError):execute('ziwei',{'value':'2017-07-23T00:00:00+08:00','year_boundary':'lunar-new-year'})
    def test_chart_runs_without_network_or_model_calls(self):
        with patch('socket.socket',side_effect=RuntimeError('No network computation allowed')):
            output=execute('qimen',{'value':'2000-01-07T12:00:00+08:00'})
        self.assertEqual(output['result']['bureau'],2)
