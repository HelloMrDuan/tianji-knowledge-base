"""Tests for scripts/check_task_tracking.py (single-task + batch gates).

The gate module is loaded from the script file so the tests exercise the
exact code CI runs. Fixtures are minimal WBS / TASK_STATUS / TASK_HISTORY
texts; check_delta() is pure and needs no git.
"""
import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_task_tracking.py"
_spec = importlib.util.spec_from_file_location("check_task_tracking", SCRIPT)
gate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gate)

WBS = """| TJ-001.4 | 一任务一闭环 | x | y |
| TJ-001.5 | 批次开发门禁 | x | y |
| TJ-003.1 | 公开分区盘点 | x | y |
| TJ-003.2 | 私有hash核对 | x | y |
| TJ-003.3 | 泄漏红线测试 | x | y |
| TJ-005.1 | 部署路径确认 | x | y |
| TJ-005.2 | 冒烟测试 | x | y |
"""

STATUS_ROW = "| {tid} | M0 | {title} | {state} | {proof} | {date} | {next} |"
STATUS_HEAD = "| 任务 | 阶段 | 标题 | 状态 | 证据 | 更新 | 下一步 |\n"


def status_text(rows):
    return STATUS_HEAD + "\n".join(
        STATUS_ROW.format(tid=t, title="t", state=s, proof=p, date=d, next="n")
        for t, s, p, d in rows) + "\n"


def history_text(events):
    head = "| 事件 | 日期 | 任务 | 状态 | 结果 | PR | SHA | CI |\n"
    return head + "\n".join(
        "| %s | %s | %s | %s | %s | %s | %s | %s |" % e for e in events) + "\n"


BASE_STATUS = status_text([
    ("TJ-001.4", "已合并", "[#228](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/228)", "2026-10-11"),
    ("TJ-001.5", "待做", "—", "—"),
    ("TJ-003.1", "待做", "—", "—"),
    ("TJ-003.2", "待做", "—", "—"),
    ("TJ-003.3", "待做", "—", "—"),
    ("TJ-005.1", "待做", "—", "—"),
    ("TJ-005.2", "待做", "—", "—"),
])
BASE_HISTORY = history_text([
    ("E0001", "2026-10-11", "TJ-001.4", "已合并", "ok",
     "https://github.com/HelloMrDuan/tianji-knowledge-base/pull/228",
     "6a22f29f2ec2e0b3a2bd9689c0dd9df5fd3d883d",
     "https://github.com/HelloMrDuan/tianji-knowledge-base/actions/runs/38101246241"),
])


def run_delta(after_status, after_history):
    prior, old_events = gate.validate(WBS, BASE_STATUS, BASE_HISTORY)
    now, events = gate.validate(WBS, after_status, after_history)
    return gate.check_delta(prior, old_events, now, events)


PR_URL = "https://github.com/HelloMrDuan/tianji-knowledge-base/pull/999"
CI_URL = "https://github.com/HelloMrDuan/tianji-knowledge-base/actions/runs/1"
SHA40 = "a" * 40


class SingleTaskGateTests(unittest.TestCase):
    def test_single_task_pr_passes(self):
        after_status = status_text([
            ("TJ-001.4", "已合并", "[#228](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/228)", "2026-10-11"),
            ("TJ-001.5", "已提交PR", PR_URL, "2026-10-22"),
            ("TJ-003.1", "待做", "—", "—"),
            ("TJ-003.2", "待做", "—", "—"),
            ("TJ-003.3", "待做", "—", "—"),
            ("TJ-005.1", "待做", "—", "—"),
            ("TJ-005.2", "待做", "—", "—"),
        ])
        after_history = BASE_HISTORY + "| E0002 | 2026-10-22 | TJ-001.5 | 已提交PR | claim | %s |  |  |\n" % PR_URL
        self.assertEqual(run_delta(after_status, after_history), "TJ-001.5")

    def test_two_rows_one_event_fails(self):
        after_status = status_text([
            ("TJ-001.4", "已合并", "[#228](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/228)", "2026-10-11"),
            ("TJ-001.5", "已提交PR", PR_URL, "2026-10-22"),
            ("TJ-003.1", "进行中", "—", "2026-10-22"),
            ("TJ-003.2", "待做", "—", "—"),
            ("TJ-003.3", "待做", "—", "—"),
            ("TJ-005.1", "待做", "—", "—"),
            ("TJ-005.2", "待做", "—", "—"),
        ])
        after_history = BASE_HISTORY + "| E0002 | 2026-10-22 | TJ-001.5 | 已提交PR | claim | %s |  |  |\n" % PR_URL
        with self.assertRaises(gate.Invalid):
            run_delta(after_status, after_history)


class BatchGateTests(unittest.TestCase):
    def _batch(self, batch_id, items):
        """items: list of (task, status, outcome). Returns (status, history)."""
        rows = [
            ("TJ-001.4", "已合并", "[#228](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/228)", "2026-10-11"),
            ("TJ-001.5", "待做", "—", "—"),
            ("TJ-003.1", "待做", "—", "—"),
            ("TJ-003.2", "待做", "—", "—"),
            ("TJ-003.3", "待做", "—", "—"),
            ("TJ-005.1", "待做", "—", "—"),
            ("TJ-005.2", "待做", "—", "—"),
        ]
        changed = {t: s for t, s, _ in items}
        rows = [(t, changed.get(t, s), PR_URL if t in changed else p,
                 "2026-10-22" if t in changed else d)
                for t, s, p, d in rows]
        after_status = status_text(rows)
        hist = BASE_HISTORY
        for i, (t, s, outcome) in enumerate(items, 2):
            hist += ("| E%04d | 2026-10-22 | %s | %s | [%s] %s | %s |  |  |\n"
                     % (i, t, s, batch_id, outcome, PR_URL))
        return after_status, hist

    def test_batch_three_tasks_mixed_status_passes(self):
        after_status, after_history = self._batch("B001", [
            ("TJ-001.5", "已提交PR", "gate upgrade submitted"),
            ("TJ-003.1", "进行中", "inventory started"),
            ("TJ-003.2", "阻塞", "waiting on runner access"),
        ])
        result = run_delta(after_status, after_history)
        self.assertIn("B001", result)
        self.assertIn("TJ-001.5", result)

    def test_batch_two_tasks_passes(self):
        after_status, after_history = self._batch("B001", [
            ("TJ-001.5", "已提交PR", "gate upgrade submitted"),
            ("TJ-003.1", "进行中", "inventory started"),
        ])
        self.assertIn("B001", run_delta(after_status, after_history))

    def test_batch_seven_tasks_fails(self):
        items = [("TJ-001.5", "进行中", "x"), ("TJ-003.1", "进行中", "x"),
                 ("TJ-003.2", "进行中", "x"), ("TJ-003.3", "进行中", "x"),
                 ("TJ-005.1", "进行中", "x"), ("TJ-005.2", "进行中", "x"),
                 ("TJ-001.4", "阻塞", "x")]
        after_status, after_history = self._batch("B001", items)
        with self.assertRaisesRegex(gate.Invalid, "2-6 tasks"):
            run_delta(after_status, after_history)

    def test_batch_duplicate_task_fails(self):
        items = [("TJ-001.5", "已提交PR", "a"), ("TJ-001.5", "阻塞", "b"),
                 ("TJ-003.1", "进行中", "c")]
        after_status, after_history = self._batch("B001", items)
        with self.assertRaisesRegex(gate.Invalid, "duplicate task"):
            run_delta(after_status, after_history)

    def test_batch_mixed_batch_ids_fails(self):
        after_status, hist = self._batch("B001", [
            ("TJ-001.5", "已提交PR", "a"),
            ("TJ-003.1", "进行中", "b"),
        ])
        hist = hist.replace("[B001] b", "[B002] b")
        with self.assertRaises(gate.Invalid):
            run_delta(after_status, hist)

    def test_batch_missing_event_fails(self):
        # change 3 rows but only 2 events
        after_status, after_history = self._batch("B001", [
            ("TJ-001.5", "已提交PR", "a"),
            ("TJ-003.1", "进行中", "b"),
            ("TJ-003.2", "进行中", "c"),
        ])
        lines = after_history.strip().split("\n")
        after_history = "\n".join(lines[:-1]) + "\n"
        with self.assertRaises(gate.Invalid):
            run_delta(after_status, after_history)

    def test_batch_illegal_task_fails(self):
        with self.assertRaises(gate.Invalid):
            gate.validate(WBS, BASE_STATUS,
                          BASE_HISTORY + "| E0002 | 2026-10-22 | TJ-999.9 | 进行中 | [B001] x | %s |  |  |\n" % PR_URL)

    def test_history_tampering_fails(self):
        tampered = BASE_HISTORY.replace("已合并", "进行中", 1)
        after_status, _ = self._batch("B001", [
            ("TJ-001.5", "已提交PR", "a"),
            ("TJ-003.1", "进行中", "b"),
        ])
        lines = after_history_lines(after_status, tampered)
        with self.assertRaises(gate.Invalid):
            run_delta_with_history(after_status, lines)

    def test_reused_batch_id_fails(self):
        base_with_batch = BASE_HISTORY + "| E0002 | 2026-10-22 | TJ-001.5 | 已提交PR | [B001] old | %s |  |  |\n" % PR_URL
        base_status2 = BASE_STATUS.replace(
            STATUS_ROW.format(tid="TJ-001.5", title="t", state="待做",
                              proof="—", date="—", next="n"),
            STATUS_ROW.format(tid="TJ-001.5", title="t", state="已提交PR",
                              proof=PR_URL, date="2026-10-22", next="n"))
        rows = [
            ("TJ-001.4", "已合并", "[#228](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/228)", "2026-10-11"),
            ("TJ-001.5", "已提交PR", PR_URL, "2026-10-22"),
            ("TJ-003.1", "进行中", PR_URL, "2026-10-22"),
            ("TJ-003.2", "进行中", PR_URL, "2026-10-22"),
            ("TJ-003.3", "待做", "—", "—"),
            ("TJ-005.1", "待做", "—", "—"),
            ("TJ-005.2", "待做", "—", "—"),
        ]
        after_status = status_text(rows)
        after_history = (base_with_batch
                         + "| E0003 | 2026-10-22 | TJ-003.1 | 进行中 | [B001] b | %s |  |  |\n" % PR_URL
                         + "| E0004 | 2026-10-22 | TJ-003.2 | 进行中 | [B001] c | %s |  |  |\n" % PR_URL)
        prior, old_events = gate.validate(WBS, base_status2, base_with_batch)
        now, events = gate.validate(WBS, after_status, after_history)
        with self.assertRaisesRegex(gate.Invalid, "already used"):
            gate.check_delta(prior, old_events, now, events)

    def test_batch_completed_task_needs_real_evidence(self):
        after_status = status_text([
            ("TJ-001.4", "已合并", "[#228](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/228)", "2026-10-11"),
            ("TJ-001.5", "已合并", PR_URL, "2026-10-22"),
            ("TJ-003.1", "进行中", PR_URL, "2026-10-22"),
            ("TJ-003.2", "待做", "—", "—"),
            ("TJ-003.3", "待做", "—", "—"),
            ("TJ-005.1", "待做", "—", "—"),
            ("TJ-005.2", "待做", "—", "—"),
        ])
        # fake completion: no SHA/CI in the event
        after_history = (BASE_HISTORY
                         + "| E0002 | 2026-10-22 | TJ-001.5 | 已合并 | [B001] fake done | %s |  |  |\n" % PR_URL
                         + "| E0003 | 2026-10-22 | TJ-003.1 | 进行中 | [B001] wip | %s |  |  |\n" % PR_URL)
        with self.assertRaises(gate.Invalid):
            run_delta(after_status, after_history)


def after_history_lines(after_status, hist):
    return hist


def run_delta_with_history(after_status, hist):
    prior, old_events = gate.validate(WBS, BASE_STATUS, BASE_HISTORY)
    now, events = gate.validate(WBS, after_status, hist)
    return gate.check_delta(prior, old_events, now, events)


if __name__ == "__main__":
    unittest.main()
