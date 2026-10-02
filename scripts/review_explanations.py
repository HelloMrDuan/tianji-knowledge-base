#!/usr/bin/env python3
"""Export an unscored human review packet or attach completed, provenance-bound reviews."""
import argparse,json
from pathlib import Path
from tianji_kb.explanation_review import apply_reviews,review_template
from tianji_kb.explanation_eval import markdown_report

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--report',type=Path,required=True)
p.add_argument('--reviews',type=Path)
p.add_argument('--export-template',action='store_true')
p.add_argument('--output',type=Path,required=True)
a=p.parse_args()
if a.export_template==bool(a.reviews):p.error('Choose --export-template or --reviews')
report=json.loads(a.report.read_text())
try:output=review_template(report) if a.export_template else apply_reviews(report,json.loads(a.reviews.read_text()))
except (ValueError,KeyError,TypeError):raise SystemExit('Review validation failed; no qualification written')
a.output.parent.mkdir(parents=True,exist_ok=True)
a.output.write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
if not a.export_template:a.output.with_suffix('.md').write_text(markdown_report(output))
print('Unscored review template exported' if a.export_template else 'Human review bound; see domain qualification and semantic metrics')
