"""Deliberately mechanical test replies; these are not real model quality evidence."""
import copy
from tianji_kb.explanation_policy import expected_strength

def valid_reply(context):
    reply={k:context[k] for k in ['domain','variant','mode','chart_digest']}
    if context['prompt_version']=='explanation-prompt-v1':
        fact=next(iter(context['facts']));eid=next(iter(context['evidence']))
        reply['claims']=[{'fact_ref':fact,'fact_value':context['facts'][fact],
            'text':'仅解释程序已计算的字段与所附原典关系。','evidence_ids':[eid],
            'quotes':[{'evidence_id':eid,'text':context['evidence'][eid]['original_text'][:20]}]}]
        return reply
    reply.update(prompt_version=context['prompt_version'],prompt_sha256=context['prompt_sha256']);claims=[]
    rules={r['rule_id']:r for r in context['rules']};policy=context['explanation_policy']
    def claim(kind,rid,pointer):
        refs=list(rules[rid]['evidence_ids'])
        item={'kind':kind,'rule_ids':[rid],'fact_ref':pointer,'fact_value':copy.deepcopy(context['facts'][pointer]),
            'text':'在当前 variant 及材料范围内，可作条件性理解；程序字段与对应引文已列出，待核事项见限制。',
            'evidence_ids':refs,'quotes':[{'evidence_id':eid,'text':context['evidence'][eid]['original_text'][:40]} for eid in refs],
            'uncertainty_refs':list(range(len(policy['uncertainty_notes']))) if kind=='uncertainty' else []}
        item['strength']=expected_strength(item,context);claims.append(item)
    for pointer in policy['required_fact_refs']:
        rid=next(r for r in rules if pointer in policy['rule_fact_refs'][r]);claim('deterministic_fact',rid,pointer)
    for rid in rules:claim('rule_match',rid,policy['rule_fact_refs'][rid][0])
    first=next(iter(rules));pointer=policy['rule_fact_refs'][first][0]
    for kind in ['classical_evidence','synthesis','uncertainty']:claim(kind,first,pointer)
    reply['claims']=claims;return reply

class MechanicalProvider:
    async def explain(self,context):return valid_reply(context)
