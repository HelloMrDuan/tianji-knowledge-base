#!/usr/bin/env python3
"""Controlled real-model dream evaluation CLI (TJ-028.2).

Runs the fixed suite ``evals/dream/cases-v1.json`` through
``dream_real_eval`` and writes ``audit.jsonl``, ``summary.json`` and
``report.md`` into ``--output-dir``.

Modes:

- ``--mode dry-run`` (default): the full pipeline against a LOCAL
  endpoint only (the configured endpoint host must be loopback).
  Proves the runner, the caps, the scoring and the audit records with
  zero real model calls. No authorization record is needed.
- ``--mode real``: a real provider run. Requires ``--authorization
  <record>`` (placed by the operator after the user approves the run)
  plus the approved AMD gateway
  (``https://developer.amd.com.cn/radeon/api/v1/chat/completions``)
  and the pinned model. The runner validates the record (including
  its binding to the fixed suite and case scope), reads the live
  ``/usage`` quota, and single-use-claims the record in the fixed
  directory next to it; it never authors one.

Exit codes: 0 = the run completed every case (case pass/fail is in
the report, not the exit code); 2 = the run stopped early (a
transport refusal, the attempt cap, the wall-clock cap, or the pts
budget); 1 = a pre-flight refusal (zero provider calls) or a usage
error.

The provider configuration comes only from the trusted process
environment (``TIANJI_AI_*``), exactly like the admin endpoint. The
runner clamps the output cap to ``--max-output-tokens`` (default
384) itself; the operator does not need to set
``TIANJI_AI_MAX_OUTPUT_TOKENS``. The pts budget is an
estimate-based cap (see ``dream_real_eval``): the pre-flight
worst-case estimate, a live quota read, a running estimate gate and
the attempt cap are the executable controls. No credential is ever
printed or written by this script: the summary records the model
name and the endpoint host only.
"""
import argparse
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tianji_kb.dream_eval import load_suite  # noqa: E402
from tianji_kb.dream_provider_config import load_dream_provider_config  # noqa: E402
from tianji_kb.dream_real_eval import (  # noqa: E402
    DEFAULT_MAX_OUTPUT_TOKENS,
    DEFAULT_MAX_POINTS,
    DEFAULT_MAX_REQUESTS,
    DEFAULT_MAX_SECONDS,
    DEFAULT_PER_CALL_TIMEOUT,
    RealEvalConfig,
    RealEvalError,
    run_real_eval,
)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("dry-run", "real"), default="dry-run")
    parser.add_argument(
        "--suite", default=None, help="fixed suite path (default evals/dream/cases-v1.json)"
    )
    parser.add_argument("--output-dir", required=True)
    parser.add_argument(
        "--authorization", default=None,
        help="authorization record path (required in real mode)",
    )
    parser.add_argument("--max-points", type=float, default=DEFAULT_MAX_POINTS)
    parser.add_argument("--max-requests", type=int, default=DEFAULT_MAX_REQUESTS)
    parser.add_argument(
        "--max-output-tokens", type=int, default=DEFAULT_MAX_OUTPUT_TOKENS
    )
    parser.add_argument(
        "--per-call-timeout", type=int, default=DEFAULT_PER_CALL_TIMEOUT
    )
    parser.add_argument("--max-seconds", type=int, default=DEFAULT_MAX_SECONDS)
    parser.add_argument("--case", action="append", default=[], dest="case_ids")
    args = parser.parse_args(argv)

    try:
        suite = load_suite(args.suite) if args.suite else load_suite()
        config = RealEvalConfig(
            mode=args.mode,
            max_points=args.max_points,
            max_requests=args.max_requests,
            max_output_tokens=args.max_output_tokens,
            per_call_timeout=args.per_call_timeout,
            max_seconds=args.max_seconds,
            authorization_path=args.authorization,
            case_ids=list(args.case_ids),
        )
        provider_config = load_dream_provider_config()
        summary = asyncio.run(
            run_real_eval(
                suite=suite,
                config=config,
                provider_config=provider_config,
                output_dir=args.output_dir,
            )
        )
    except RealEvalError as error:
        print(f"real eval refused: {error.code}: {error}", file=sys.stderr)
        return 1
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if summary.get("stopped"):
        print(f"real eval stopped early: {summary['stopped']}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
