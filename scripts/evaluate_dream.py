#!/usr/bin/env python3
"""Offline dream eval runner (TJ-028.2). Mock provider only.

Never reads TIANJI_AI_* credentials and never contacts a network: the
only provider is the labelled scripted test double in
``tianji_kb.dream_eval``. A real-model run needs separate authorization
and a different runner. ``--dry-run`` validates the suite (fixtures
plus the pure reply validator) without any provider call.
"""

import argparse
import asyncio
import json
from pathlib import Path

from tianji_kb.dream_eval import (
    evaluate_dream_suite,
    load_suite,
    markdown_report,
    validate_suite,
)


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("build/dream-evals"))
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate the suite without running any provider call",
    )
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    if args.dry_run:
        checked = validate_suite(load_suite())
        print(
            "dry-run",
            checked["suite_id"],
            "cases_checked",
            checked["cases_checked"],
            "provider_calls",
            checked["provider_calls"],
        )
        return 0
    report = await evaluate_dream_suite()
    (args.output / "dream-eval-v1.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    )
    (args.output / "dream-eval-v1.md").write_text(markdown_report(report))
    row = report["reports"]["dream"]
    print(
        "dream-eval-v1",
        "run",
        report["run_kind"],
        "cases",
        row["case_count"],
        "positive_pass_rate",
        row["pass_rate"],
        "control_pass_rate",
        row["control_pass_rate"],
        "failures",
        len(row["failures"]),
    )
    for failure in row["failures"]:
        print("FAIL", failure["id"], failure["error"])
    return int(bool(row["failures"]))


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
