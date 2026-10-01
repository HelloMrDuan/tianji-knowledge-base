"""Resolve declared rules to verified classical evidence, never unreviewed bodies."""
import hashlib
import copy
import json
from pathlib import Path

from .knowledge import read_json, validate_knowledge

ROOT = Path(__file__).resolve().parents[2]

class EvidenceResolver:
    def __init__(self,root=ROOT):
        self.root=Path(root)
        self.model=validate_knowledge(self.root)
        self.sources=self.model['sources']
        self.entities=self.model['entities']
        self.supplementary_classics={}
        for path in sorted((self.root/'data/canonical').glob('*/phase2_evidence.json')):
            for classic in read_json(path).get('classics',[]):
                if classic['id'] in self.entities or classic['id'] in self.supplementary_classics or classic['domain'] not in self.model['domains']:
                    raise ValueError('Invalid supplementary classic')
                self.supplementary_classics[classic['id']]=classic
        self.contracts={}
        for path in sorted((self.root/'data/canonical').glob('*/phase2_execution.json')):
            obj=read_json(path)
            if obj['domain'] not in self.model['domains']:
                raise ValueError('Unregistered execution domain')
            self.contracts[obj['domain']]=obj

    def rule(self,rule_id):
        if rule_id in self.entities and self.entities[rule_id][0]=='rules':
            return self.entities[rule_id][1]
        for contract in self.contracts.values():
            for rule in contract['rules']:
                if rule['id']==rule_id:
                    return rule
        raise ValueError(f'Unknown rule: {rule_id}')

    def resolve(self,rule_id,variant):
        rule=self.rule(rule_id)
        if rule_id not in self.entities and rule['variant']!=variant:
            raise ValueError('Evidence variant mismatch')
        refs=rule.get('source_refs') or [ref for rid in rule.get('phase1_rule_refs',[]) for ref in self.rule(rid)['source_refs']]
        if not refs:
            raise ValueError('Rule lacks reviewed classical evidence')
        output=[]
        for ref in refs:
            source=self.sources[ref['source_id']]
            if source['kind']!='classical' or source['evidence_level']=='D':
                raise ValueError('Unreviewed source cannot enter explanation evidence')
            section=self.entities[ref['section_id']][1]
            if ref['original_text'] not in section['text'] or section['source_id']!=source['source_id']:
                raise ValueError('Unverifiable quote')
            chapter=self.entities[section['chapter_id']][1]
            classic=self.entities[section['classic_id']][1]
            output.append({**ref,'rule_id':rule_id,'variant':variant,'classic_id':classic['id'],
                'classic_title':classic['name'],'chapter_id':chapter['id'],'chapter_title':chapter['name'],
                'locator':section['locator'],'source_url':source['url'],'commit':source['commit'],
                'sha256':source['sha256'],'evidence_level':source['evidence_level']})
        for path in sorted((self.root/'data/canonical').glob('*/phase2_evidence.json')):
            evidence=read_json(path)
            for ref in evidence['records']:
                if rule_id not in ref['rule_ids']:
                    continue
                source=self.sources[ref['source_id']]
                from .knowledge import source_text
                if ref['review_status']!='approved' or source['kind']!='classical' or source['evidence_level']=='D' or ref['original_text'] not in source_text(self.root,source):
                    raise ValueError('Unreviewed or unverifiable supplementary evidence')
                classic=self.entities[ref['classic_id']][1] if ref['classic_id'] in self.entities else self.supplementary_classics[ref['classic_id']]
                output.append({'source_id':source['source_id'],'section_id':ref['id'],
                    'original_text':ref['original_text'],'role':'classical','rule_id':rule_id,'variant':variant,
                    'classic_id':classic['id'],'classic_title':classic['name'],
                    'chapter_id':ref['id']+'.chapter','chapter_title':ref['chapter_title'],
                    'locator':ref['locator'],'source_url':source['url'],'commit':source['commit'],
                    'sha256':source['sha256'],'evidence_level':source['evidence_level'],
                    'independence_status':ref['independence_status']})
        return output

class ExecutionTrace:
    def __init__(self,domain,variant,resolver=None):
        self.domain=domain;self.variant=variant
        self.resolver=resolver or EvidenceResolver()
        self.steps=[];self.evidence={}

    def add(self,rule_id,inputs,output):
        refs=self.resolver.resolve(rule_id,self.variant)
        for ref in refs:
            key=hashlib.sha256(json.dumps(ref,ensure_ascii=False,sort_keys=True).encode()).hexdigest()[:24]
            self.evidence[key]=ref
        self.steps.append({'rule_id':rule_id,'inputs':copy.deepcopy(inputs),'output':copy.deepcopy(output),'evidence_ids':[
            hashlib.sha256(json.dumps(ref,ensure_ascii=False,sort_keys=True).encode()).hexdigest()[:24] for ref in refs]})
        return output

    def finish(self,result,matches=None):
        return {'domain':self.domain,'variant':self.variant,'deterministic':True,'result':result,
                'trace':self.steps,'rule_matches':matches or [],'evidence':self.evidence,
                'interpretation_contract':{'ai_may_explain':True,'ai_may_compute_chart':False,
                    'must_preserve_variant_and_evidence_level':True}}
