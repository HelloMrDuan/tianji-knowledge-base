"""Classical nine-method structural chart; explicit lodged-stem depth convention."""
from ..foundations import BRANCHES,STEMS,CYCLE,CONTROLS,branch_element,stem_element,ganzhi_index
from ..resolver import ExecutionTrace
from .liuren import month_general,sky_plate,four_lessons,base

VARIANT='daquan-nine-methods-lodged-stems-v1'
METHOD_RULE={'贼克':'r001','比用':'r002','涉害':'r003','遥克':'r004','昴星':'r005','别责':'r006','八专':'r007','伏吟':'r008','返吟':'r009'}
PUNISH=dict(zip('寅巳申丑戌未子卯辰午酉亥','巳申寅戌未丑卯子辰午酉亥'))


def advance(branch,n):return BRANCHES[(BRANCHES.index(branch)+n)%12]
def element(symbol):return stem_element(symbol) if symbol in STEMS else branch_element(symbol)
def controls(a,b):return CONTROLS[element(a)]==element(b)
def same_polarity(a,b):return (BRANCHES.index(a)-STEMS.index(b))%2==0


def control_candidates(lessons):
    lower=[l['upper'] for l in lessons if controls(l['lower'],l['upper'])]
    upper=[l['upper'] for l in lessons if controls(l['upper'],l['lower'])]
    return list(dict.fromkeys(lower or upper)),bool(lower)


def choose(candidates,lower_controls,day,sky,lessons):
    if len(candidates)==1:return candidates[0],'贼克',{}
    same=[s for s in candidates if same_polarity(s,day[0])]
    if len(same)==1:return same[0],'比用',{'polarity_candidates':same}
    pool=same or candidates
    inverse={s:e for e,s in sky.items()}
    lodging=base()['stem_lodging']
    depths={}
    for candidate in pool:
        start=inverse[candidate];depth=0
        for i in range((BRANCHES.index(candidate)-BRANCHES.index(start))%12+1):
            place=advance(start,i)
            obstacles=[place]+[stem for stem in STEMS if lodging[stem]==place]
            depth+=sum(controls(x,candidate) if lower_controls else controls(candidate,x) for x in obstacles)
        depths[candidate]=depth
    best=[s for s in pool if depths[s]==max(depths.values())]
    rank=lambda s:0 if inverse[s] in '寅申巳亥' else 1 if inverse[s] in '子午卯酉' else 2
    best=[s for s in best if rank(s)==min(rank(x) for x in best)]
    if len(best)>1:
        preferred=lessons[0]['upper'] if STEMS.index(day[0])%2==0 else lessons[2]['upper']
        if preferred in best:best=[preferred]
    if len(best)!=1:
        raise ValueError(f'Unresolved Shehai tie for this variant: {day}/{depths}')
    return best[0],'涉害',{'depths':depths,'earth_positions':{s:inverse[s] for s in pool}}


def select(day,sky,lessons):
    candidates,lower=control_candidates(lessons)
    yang=STEMS.index(day[0])%2==0
    first,third=lessons[0]['upper'],lessons[2]['upper']
    shift=(BRANCHES.index(sky['子'])-BRANCHES.index('子'))%12
    details={'control_candidates':candidates,'lower_controls_upper':lower,'distinct_uppers':len({l['upper'] for l in lessons})}
    if shift==0:
        initial=candidates[0] if candidates else first if yang else third
        middle=PUNISH[initial]
        if middle==initial:middle=third if yang else first
        final=PUNISH[middle]
        if final==middle or final==initial:final=advance(middle,6)
        return '伏吟',[initial,middle,final],details
    if candidates:
        initial,method,selection=choose(candidates,lower,day,sky,lessons)
        details.update(selection,selection_method=method)
        return '返吟' if shift==6 else method,[initial,sky[initial],sky[sky[initial]]],details
    if shift==6:
        horse=next(v for group,v in [('申子辰','寅'),('寅午戌','申'),('巳酉丑','亥'),('亥卯未','巳')] if day[1] in group)
        return '返吟',[horse,third,first],details
    distinct=details['distinct_uppers']
    if distinct==2:
        initial=advance(first,2) if yang else advance(lessons[3]['upper'],-2)
        return '八专',[initial,first,first],details
    uppers=list(dict.fromkeys(l['upper'] for l in lessons))
    remote=[s for s in uppers if controls(s,day[0])] or [s for s in uppers if controls(day[0],s)]
    if remote:
        same=[s for s in remote if same_polarity(s,day[0])]
        selected=same or remote
        if len(selected)!=1:raise ValueError('Unresolved remote-control candidates')
        initial=selected[0];details['remote_candidates']=remote
        return '遥克',[initial,sky[initial],sky[sky[initial]]],details
    if distinct==3:
        other=STEMS[(STEMS.index(day[0])+5)%10]
        initial=sky[base()['stem_lodging'][other]] if yang else advance(day[1],4)
        return '别责',[initial,first,first],details
    if distinct==4:
        initial=sky['酉'] if yang else next(e for e,s in sky.items() if s=='酉')
        return '昴星',[initial,third,first] if yang else [initial,first,third],details
    raise ValueError('Unsupported lesson structure')


def compute(solar_term,day_ganzhi,hour_branch):
    ganzhi_index(day_ganzhi)
    general=month_general(solar_term)
    sky=sky_plate(general['branch'],hour_branch)
    lessons=four_lessons(day_ganzhi[0],day_ganzhi[1],sky)
    method,transmissions,selection=select(day_ganzhi,sky,lessons)
    return {'month_general':general,'sky_plate':sky,'four_lessons':lessons,
        'method':method,'transmissions':transmissions,'selection':selection}


def chart(solar_term,day_ganzhi,hour_branch,variant=VARIANT):
    if variant!=VARIANT:raise ValueError('Unsupported Liuren variant')
    result=compute(solar_term,day_ganzhi,hour_branch)
    trace=ExecutionTrace('liuren',variant)
    trace.add('liuren.phase2.month_general',{'solar_term':solar_term},result['month_general'])
    trace.add('liuren.phase2.plates',{'month_general':result['month_general']['branch'],'hour_branch':hour_branch},result['sky_plate'])
    trace.add('liuren.phase2.lessons',{'day_ganzhi':day_ganzhi,'sky_plate':result['sky_plate']},result['four_lessons'])
    method=result['method']
    trace.add('liuren.phase2.'+{'贼克':'zeike','比用':'biyong','涉害':'shehai','遥克':'yaoke','昴星':'maoxing','别责':'bieze','八专':'bazhuan','伏吟':'fuyin','返吟':'fanyin'}[method],
        {'four_lessons':result['four_lessons'],'selection':result['selection']},result['transmissions'])
    return trace.finish(result,[{'rule_id':trace.steps[-1]['rule_id'],'phase1_rule_id':'liuren.rule.'+METHOD_RULE[method],'method':method,'matched':True}])
