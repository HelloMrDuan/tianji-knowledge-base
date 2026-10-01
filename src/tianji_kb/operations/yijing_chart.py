"""Structural six-line algorithms; textual 乾坤无互 is a separate interpretation."""
from ..foundations import hexagram
from ..resolver import ExecutionTrace
from .yijing import transform
VARIANT='bottom-up-six-lines-v1'

def chart(bits,changing_lines=(),variant=VARIANT):
    if variant!=VARIANT:raise ValueError('Unsupported Yijing variant')
    original=hexagram(bits)
    lines=tuple(changing_lines)
    # Validate changing lines even when a caller only requests an unchanged chart.
    changed=transform(bits,'change',lines)
    trace=ExecutionTrace('yijing',variant)
    result={'original':original}
    trace.add('yijing.phase2.structure',{'bits':bits},original)
    for operation,rule in [('opposite','opposite'),('inverse','inverse'),('nuclear','nuclear'),('change','change')]:
        output=hexagram(changed if operation=='change' else transform(bits,operation))
        result[operation]=output
        trace.add('yijing.phase2.'+rule,{'bits':bits,'changing_lines':list(lines) if operation=='change' else []},output)
    result['nuclear_scope']='结构互卦；乾坤无互的解释性文本例外不改写六爻数学结构'
    return trace.finish(result)
