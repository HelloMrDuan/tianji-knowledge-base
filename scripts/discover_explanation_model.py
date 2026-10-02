#!/usr/bin/env python3
"""Environment-only model discovery; optional continuation into the existing fixed eval."""
import argparse,asyncio,json,os,subprocess,sys
from pathlib import Path
from tianji_kb.model_discovery import discover_model
from tianji_kb.explanation import ExplanationFailure

async def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=Path('build/provider-discovery'))
    parser.add_argument('--evaluate',action='store_true',help='After verified selection, run the fixed v1/v2 six-domain evaluation')
    args=parser.parse_args()
    try:selection=await discover_model()
    except (ExplanationFailure,ValueError) as error:
        print('Model discovery blocked:',error.code if isinstance(error,ExplanationFailure) else 'provider_configuration_invalid')
        return 2
    args.output.mkdir(parents=True,exist_ok=True)
    (args.output/'selection.json').write_text(json.dumps(selection,ensure_ascii=False,indent=2)+'\n')
    print('Verified JSON chat model:',selection['model'],'; explanation quality not yet evaluated')
    if args.evaluate:
        os.environ['TIANJI_AI_MODEL']=selection['model']
        return subprocess.run([sys.executable,str(Path(__file__).with_name('evaluate_explanations.py')),
            '--output',str(args.output/'explanation-evals')],check=False).returncode
    return 0

if __name__=='__main__':raise SystemExit(asyncio.run(main()))
