#!/usr/bin/env python3
"""One atomic task per PR, append-only evidence and WBS/status parity.

Usage:
  python scripts/check_task_tracking.py
  python scripts/check_task_tracking.py --base <git-base-sha>

No network or access to private knowledge is necessary. GitHub merge/CI
truth still requires the reviewer to verify the referenced URLs.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WBS = "docs/product/DETAILED_DELIVERY_BACKLOG_V1.md"
STATUS = "docs/product/TASK_STATUS.md"
HISTORY = "docs/product/TASK_HISTORY.md"
VALID = {"待做", "进行中", "已提交PR", "CI待验", "阻塞", "已合并", "已部署验收"}
DONE = {"已合并", "已部署验收"}
TASK = re.compile(r"^TJ-\d{3}\.\d+(?:\.\d+)?$")
SHA = re.compile(r"\b[a-f0-9]{40}\b")
PR = re.compile(r"https://github\.com/HelloMrDuan/tianji-(?:knowledge-base|private-knowledge)/pull/\d+")
CI = re.compile(r"https://github\.com/HelloMrDuan/tianji-(?:knowledge-base|private-knowledge)/(?:actions/runs/\d+|pull/\d+/checks)")
EVENT = re.compile(r"^E\d{4,}$")


class Invalid(RuntimeError):
    pass


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def cells(line: str) -> list[str]:
    return [part.strip() for part in line.strip().strip("|").split("|")]


def wbs_ids(text: str) -> set[str]:
    ids = []
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        parts = cells(line)
        if not parts:
            continue
        possible = parts[0].replace("**", "")
        if TASK.fullmatch(possible):
            ids.append(possible)
    if len(ids) != len(set(ids)):
        raise Invalid("WBS has duplicate atomic task identifiers")
    if not ids:
        raise Invalid("WBS has no atomic tasks")
    return set(ids)


def status_rows(text: str) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        parts = cells(line)
        if len(parts) != 7 or not TASK.fullmatch(parts[0]):
            continue
        key, phase, title, state, proof, updated, next_step = parts
        if key in found:
            raise Invalid(f"duplicate task row: {key}")
        if state not in VALID:
            raise Invalid(f"unknown status {key}: {state}")
        if not title or not phase.startswith("M") or not next_step:
            raise Invalid(f"missing title/phase/next step: {key}")
        found[key] = parts
    if not found:
        raise Invalid("no valid atomic status rows")
    return found


def history_rows(text: str) -> list[list[str]]:
    events: list[list[str]] = []
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        parts = cells(line)
        if len(parts) != 8 or not EVENT.fullmatch(parts[0]):
            continue
        events.append(parts)
    if not events:
        raise Invalid("event history is empty")
    for number, event in enumerate(events, 1):
        if event[0] != f"E{number:04d}":
            raise Invalid(f"event sequence broken at index {number}: {event[0]}")
        if not TASK.fullmatch(event[2]):
            raise Invalid(f"history unknown ID: {event[2]}")
        if event[3] not in VALID:
            raise Invalid(f"history invalid status: {event[3]}")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", event[1]):
            raise Invalid(f"history missing YYYY-MM-DD: {event[0]}")
        if not event[4].strip():
            raise Invalid(f"history empty outcome: {event[0]}")
    return events


def validate(wbs: str, status: str, history: str) -> tuple[dict[str, list[str]], list[list[str]]]:
    defined = wbs_ids(wbs)
    tracked = status_rows(status)
    if defined != set(tracked):
        missing = sorted(defined - set(tracked))
        extras = sorted(set(tracked) - defined)
        raise Invalid(f"status / WBS mismatch; missing={missing}, extra={extras}")
    events = history_rows(history)
    latest = {}
    for event in events:
        if event[2] not in tracked:
            raise Invalid(f"event references a nonexistent task: {event[2]}")
        latest[event[2]] = event
        if event[3] in DONE:
            if not PR.search(event[5]) or not SHA.search(event[6]) or not CI.search(event[7]):
                raise Invalid(f"completed event lacks real-shaped PR, full SHA, CI: {event[0]}")
    for task_id, row in tracked.items():
        event = latest.get(task_id)
        if event and row[3] != event[3]:
            raise Invalid(f"{task_id}: status differs from most recent event")
        if row[3] in DONE:
            if event is None or event[3] not in DONE:
                raise Invalid(f"{task_id}: completed task has no completed event")
            if not PR.search(row[4]):
                raise Invalid(f"{task_id}: completed task row lacks PR link")
            if row[5] == "—":
                raise Invalid(f"{task_id}: completed task has no update date")
    return tracked, events


def show(base: str, rel: str) -> str | None:
    result = subprocess.run(
        ["git", "show", f"{base}:{rel}"],
        cwd=ROOT, text=True, stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL, check=False, encoding="utf-8",
    )
    if result.returncode:
        return None
    return result.stdout


def validate_pr_delta(
    base: str,
    before_status: str | None,
    before_history: str | None,
    after_status: str,
    after_history: str,
) -> str:
    """Check one changed task and one newly appended event per normal PR.

    The first-ever registry bootstrap is special-cased exactly once.
    """
    if before_status is None and before_history is None:
        current = status_rows(after_status)
        events = history_rows(after_history)
        if "TJ-001.4" not in current or current["TJ-001.4"][3] != "进行中":
            raise Invalid("bootstrap requires the one-task-tracking task TJ-001.4 in progress")
        if events[-1][2] != "TJ-001.4":
            raise Invalid("bootstrap last event must claim TJ-001.4")
        return "TJ-001.4 (first registry bootstrap)"
    if before_status is None or before_history is None:
        raise Invalid("partial loss of registry/history in base commit")
    prior, old_events = validate(
        show(base, WBS) or "",
        before_status, before_history,
    )
    now, events = validate(read(WBS), after_status, after_history)
    altered = {k for k in set(prior) | set(now) if prior.get(k) != now.get(k)}
    if len(altered) != 1:
        raise Invalid(f"each PR must update exactly one task status row; got {sorted(altered)}")
    # Preserve the exact old rows: correcting a historical claim is a new event.
    if events[:len(old_events)] != old_events:
        raise Invalid("history is append-only: existing events changed or were reordered")
    if len(events) != len(old_events) + 1:
        raise Invalid("each PR must append exactly one task-history event")
    task_id = next(iter(altered))
    if events[-1][2] != task_id or events[-1][3] != now[task_id][3]:
        raise Invalid("new event ID/status must match the one changed task row")
    return task_id


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", help="Git commit to compare against for one-task PR gate")
    args = parser.parse_args()
    try:
        status = read(STATUS)
        history = read(HISTORY)
        tasks, events = validate(read(WBS), status, history)
        selected = None
        if args.base:
            selected = validate_pr_delta(
                args.base, show(args.base, STATUS), show(args.base, HISTORY), status, history
            )
        completed = sum(1 for x in tasks.values() if x[3] in DONE)
        print(f"PASS task tracking: {len(tasks)} atomic tasks, {completed} completed, "
              f"{len(events)} events; one-task PR={selected or 'not requested'}")
    except (Invalid, OSError) as error:
        print(f"FAIL task tracking: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
