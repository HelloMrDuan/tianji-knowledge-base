"""Explanation governance only: no chart calculations, source promotion or engine edits."""
import copy,re
from .runtime_catalog import digest

KINDS=('deterministic_fact','rule_match','classical_evidence','synthesis','uncertainty')
KEY_FACTS={
 'liuyao':['/original/number','/changed/number','/palace/shi','/palace/ying','/changing_lines','/empty_branches'],
 'qimen':['/solar_term','/dun','/bureau','/chief_star','/chief_door'],
 'liuren':['/month_general','/method','/transmissions'],
 'ziwei':['/life_palace','/body_palace','/bureau','/major_stars','/four_transformations'],
 'fengshui':['/mountain','/trigram','/opposite','/period'],
 'yijing':['/original/number','/opposite/number','/inverse/number','/nuclear/number','/change/number'],
 'bazi':['/day_master/stem','/stem_ten_gods','/hidden_stems']}
ROOTS={
 'liuyao':{'motion':['original','changed','changing_lines'],'palace':['palace','changed_palace'],
           'najia':['lines/*/najia','lines/*/changed_najia'],'spirits':['lines/*/spirit'],
           'empty':['empty_branches','lines/*/empty'],'relatives':['lines/*/relative','lines/*/changed_relative_to_original_palace'],
           'month_break':['lines/*/month_break']},
 'qimen':{'calendar':['calendar','solar_term','day_ganzhi','hour_ganzhi'],
          'bureau':['solar_term','dun','bureau','yuan'],'earth':['earth_plate'],
          'chiefs':['chief_star','chief_door'],'plates':['sky_plate','stars','doors','deities','star_positions','door_positions','deity_positions','center_star_policy']},
 'liuren':{'month_general':['month_general'],'plates':['sky_plate'],'lessons':['four_lessons']},
 'ziwei':{'life_body':['life_palace','body_palace'],'bureau':['life_ganzhi','bureau'],'palaces':['palaces'],
          'major_stars':['major_stars'],'auxiliary_stars':['auxiliary_stars'],
          'mutagens':['four_transformations','mutagen_variant','mutagen_evidence']},
 'fengshui':{'compass':['degrees','mountain','mountain_element','trigram','trigram_element','opposite'],
             'relative_period':['period']},
 'yijing':{'structure':['original'],'opposite':['opposite'],'inverse':['inverse'],'nuclear':['nuclear'],'change':['change']},
 'bazi':{'pillars':['pillars','day_master'],'ten_gods':['stem_ten_gods','pillars/*/stem/ten_god'],
         'hidden_stems':['hidden_stems','pillars/*/branch/hidden_stems']}}


def fail(code):
    from .explanation import ExplanationFailure
    raise ExplanationFailure(code)


def preflight(raw):
    if raw.get('source_conflicts'):fail('source_conflict_unresolved')
    if not raw.get('evidence') or not raw.get('rule_matches'):fail('insufficient_evidence')
    for rule in raw['rule_matches']:
        if rule.get('variant')!=raw['variant'] or not rule.get('matched'):fail('variant_policy_mismatch')
        if not rule.get('evidence_ids'):fail('insufficient_evidence')
        for eid in rule['evidence_ids']:
            ref=raw['evidence'].get(eid)
            if not ref or not ref.get('original_text','').strip():fail('insufficient_evidence')
            if ref.get('variant')!=raw['variant']:fail('variant_policy_mismatch')
    if raw['mode']=='production' and (raw['result'].get('period') or {}).get('production_eligible') is False:
        fail('research_content_in_production')


def matches(pointer,root):
    pattern='/chart/'+root
    return re.fullmatch(re.escape(pattern).replace(r'\*',r'\d+')+r'(?:/.*)?',pointer) is not None


def add_policy(context):
    rules={r['rule_id']:r for r in context['rules']};facts=context['facts'];bindings={};strengths={}
    for rid,rule in rules.items():
        suffix=rid.rsplit('.',1)[-1]
        roots=ROOTS[context['domain']].get(suffix)
        if roots is None and context['domain']=='liuren':roots=['method','transmissions']
        if roots is None:fail('unreviewed_explanation_binding')
        bindings[rid]=[pointer for pointer in facts if any(matches(pointer,root) for root in roots)]
        if not bindings[rid]:fail('insufficient_evidence')
        refs=[context['evidence'][eid] for eid in rule['evidence_ids']]
        strengths[rid]='D' if 'D' in rule.get('evidence_scope','') or any(ref['evidence_level']=='D' for ref in refs) else 'C' if any(ref['evidence_level']=='C' for ref in refs) else 'B'
    required=['/chart'+pointer for pointer in KEY_FACTS[context['domain']] if '/chart'+pointer in facts]
    # Period=null is a fact of no implemented period, bound to compass rather than an epoch rule.
    if context['domain']=='fengshui' and context['chart']['period'] is None:
        bindings['fengshui.phase2.compass'].append('/chart/period')
    context['explanation_policy']={'required_kinds':list(KINDS),'required_fact_refs':required,
        'required_rule_ids':sorted(rules),'rule_fact_refs':bindings,'rule_evidence_levels':strengths,
        'uncertainty_notes':['C 可追溯材料尚无真正独立 A/B 证据；不能据此作确定预测。',
                             *context['limitations']],
        'free_prose_requires_semantic_review':True}
    return context


def reply_schema(base):
    schema=copy.deepcopy(base)
    schema['required']+=['prompt_version','prompt_sha256']
    schema['properties'].update(prompt_version={'const':'explanation-prompt-v2'},prompt_sha256={'type':'string'})
    claims=schema['properties']['claims'];claims.update(minItems=5,maxItems=40)
    item=claims['items'];item['required']+=['kind','rule_ids','strength','uncertainty_refs']
    item['properties'].update(kind={'enum':list(KINDS)},rule_ids={'type':'array','minItems':1,'uniqueItems':True,'items':{'type':'string'}},
        strength={'enum':['computed','conditional','unverified']},
        uncertainty_refs={'type':'array','uniqueItems':True,'items':{'type':'integer','minimum':0}})
    item['properties']['quotes'].update(minItems=1,maxItems=12)
    return schema


def expected_strength(claim,context):
    policy=context['explanation_policy']
    if claim['kind']=='uncertainty' or context['mode']=='research' or any(policy['rule_evidence_levels'][rid]=='D' for rid in claim['rule_ids']):return 'unverified'
    if claim['kind']=='deterministic_fact':return 'computed'
    return 'conditional'


# Conservative explicit-assertion checks; these do not prove all free-prose entailment.
TEXT_FACTS={
 'liuyao':[(r'世爻(?:为|是|在|[:：])\s*([一二三四五六0-9]+)','/chart/palace/shi'),
           (r'应爻(?:为|是|在|[:：])\s*([一二三四五六0-9]+)','/chart/palace/ying')],
 'qimen':[(r'(?:采用|当前为|属于|遁法为)\s*([阴阳])遁','/chart/dun'),
          (r'局数(?:为|是|[:：])\s*([一二三四五六七八九0-9]+)','/chart/bureau')],
 'liuren':[(r'(?:采用|取法为|三传法为)\s*(贼克|比用|涉害|遥克|昴星|别责|八专|伏吟|返吟)','/chart/method')],
 'ziwei':[(r'命宫(?:为|在|是|[:：])\s*([子丑寅卯辰巳午未申酉戌亥])','/chart/life_palace'),
          (r'身宫(?:为|在|是|[:：])\s*([子丑寅卯辰巳午未申酉戌亥])','/chart/body_palace')],
 'fengshui':[(r'坐山(?:为|是|[:：])\s*([壬子癸丑艮寅甲卯乙辰巽巳丙午丁未坤申庚酉辛戌乾亥])','/chart/mountain')],
 'yijing':[(r'本卦编号(?:为|是|[:：])\s*([0-9]+)','/chart/original/number'),
           (r'变卦编号(?:为|是|[:：])\s*([0-9]+)','/chart/change/number')]}

def validate_text_facts(claim,context):
    text=claim['text']
    for pattern,pointer in TEXT_FACTS[context['domain']]:
        for match in re.finditer(pattern,text):
            if re.search(r'不|非|未|禁止',text[max(0,match.start()-2):match.start()]):continue
            value=match.group(1);expected=context['facts'][pointer]
            if type(expected) is int:
                value=int(value) if value.isdigit() else {'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9}.get(value)
            if digest(value)!=digest(expected):fail('chart_text_contradiction')
    pattern=r'[a-z][a-z0-9]*(?:-[a-z0-9]+)+-v[0-9]+'
    allowed={context['variant']}|{value for value in context['facts'].values() if isinstance(value,str) and re.fullmatch(pattern,value)}
    if any(token not in allowed for token in re.findall(pattern,text)):fail('variant_policy_mismatch')

def validate_claim_policy(claim,context):
    policy=context['explanation_policy'];rules={r['rule_id']:r for r in context['rules']}
    validate_text_facts(claim,context)
    if any(rid not in rules for rid in claim['rule_ids']):fail('unmatched_rule_claim')
    # Each rule must have its own cited evidence; valid IDs for unrelated rules are insufficient.
    for rid in claim['rule_ids']:
        if claim['fact_ref'] not in policy['rule_fact_refs'][rid]:fail('rule_fact_binding_mismatch')
        if not set(claim['evidence_ids']).intersection(rules[rid]['evidence_ids']):fail('evidence_rule_binding_mismatch')
    allowed={eid for rid in claim['rule_ids'] for eid in rules[rid]['evidence_ids']}
    if not set(claim['evidence_ids'])<=allowed:fail('evidence_rule_binding_mismatch')
    if not set(claim['evidence_ids'])<={q['evidence_id'] for q in claim['quotes']}:fail('evidence_grounding_missing')
    if claim['strength']!=expected_strength(claim,context):fail('evidence_strength_overstated')
    if re.search(r'必然|一定|绝对正确|铁口|百分之百|命中注定|毫无争议|确定结论|独立[ABＡＢ]|[ABＡＢ]\s*级|保证.*(?:吉|凶|发财|成功)',claim['text']):fail('unsupported_certainty')
    if re.search(r'吉凶预测|必发财|必大凶|必大吉|应期断定|大限吉凶|流年吉凶',claim['text']):fail('out_of_scope_claim')
    for index in claim['uncertainty_refs']:
        if index>=len(policy['uncertainty_notes']):fail('unknown_uncertainty_reference')

def validate_policy(reply,context):
    if reply['prompt_version']!=context['prompt_version'] or reply['prompt_sha256']!=context['prompt_sha256']:fail('prompt_version_mismatch')
    policy=context['explanation_policy'];rules={r['rule_id']:r for r in context['rules']}
    kinds=set();covered_rules=set();covered_facts=set();uncertainties=set()
    for claim in reply['claims']:
        kinds.add(claim['kind'])
        if any(rid not in rules for rid in claim['rule_ids']):fail('unmatched_rule_claim')
        validate_claim_policy(claim,context)
        if claim['kind']=='rule_match':covered_rules.update(claim['rule_ids'])
        if claim['kind']=='deterministic_fact':covered_facts.add(claim['fact_ref'])
        if claim['kind']=='uncertainty':uncertainties.update(claim['uncertainty_refs'])
    if kinds!=set(KINDS) or not set(policy['required_rule_ids'])<=covered_rules or not set(policy['required_fact_refs'])<=covered_facts:
        fail('explanation_incomplete')
    if uncertainties!=set(range(len(policy['uncertainty_notes']))):fail('limitations_omitted')


def response_policy(reply,context):
    policy=context['explanation_policy']
    degraded=context['mode']=='research' or 'D' in policy['rule_evidence_levels'].values() or any(context['limitations'][1:])
    return {'prompt_version':context['prompt_version'],'prompt_sha256':context['prompt_sha256'],
        'quality_status':'degraded_requires_review' if degraded else 'requires_semantic_review',
        'semantic_review_required':True,'automatic_release_allowed':False,
        'uncertainty_notes':policy['uncertainty_notes'],
        'sections':{kind:[i for i,c in enumerate(reply['claims']) if c['kind']==kind] for kind in KINDS}}
