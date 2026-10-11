"""Regression tests for the strict one-task-and-log GitHub gate."""
from __future__ import annotations

import re
import unittest
from unittest.mock import patch

from scripts import check_task_tracking as task


class TaskTrackerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.wbs = task.read(task.WBS)
        cls.status = task.read(task.STATUS)
        cls.history = task.read(task.HISTORY)

    def test_real_wbs_has_92_unique_atomic_tasks(self):
        rows, events = task.validate(self.wbs, self.status, self.history)
        self.assertEqual(len(rows), 92)
        self.assertEqual(len(events), 9)
        self.assertIn("TJ-004.3", rows)
        self.assertEqual(rows["TJ-004.3"][3], "待做")
        self.assertEqual(rows["TJ-001.4"][3], "进行中")

    def test_duplicate_task_is_rejected(self):
        row = next(x for x in self.status.splitlines() if x.startswith("| TJ-004.3 |"))
        with self.assertRaisesRegex(task.Invalid, "duplicate"):
            task.status_rows(self.status + "\n" + row)

    def test_wbs_task_cannot_be_lost_silently(self):
        updated = "\n".join(x for x in self.status.splitlines() if not x.startswith("| TJ-004.3 |"))
        with self.assertRaisesRegex(task.Invalid, "mismatch"):
            task.validate(self.wbs, updated, self.history)

    def test_finished_event_requires_real_shaped_merged_sha(self):
        corrupted = re.sub(
            r"(E0007 \| 2026-10-11 \| TJ-004\.2 \| 已合并 \|.*? \| )"
            r"a9f0b276d2b506c0cb0768fcb74f57da01de72af",
            r"\1fake",
            self.history, count=1,
        )
        self.assertNotEqual(corrupted, self.history)
        with self.assertRaisesRegex(task.Invalid, "full SHA"):
            task.validate(self.wbs, self.status, corrupted)

    def next_event(self, task_id="TJ-001.4", state="已提交PR"):
        return (f"| E0010 | 2026-10-11 | {task_id} | {state} | "
                "已提交追踪 PR 尚未合并 | "
                "https://github.com/HelloMrDuan/tianji-knowledge-base/pull/9999 "
                "| — | — |")

    def changed_row(self, task_id="TJ-001.4", state="已提交PR"):
        rows = self.status.splitlines()
        for i, row in enumerate(rows):
            if row.startswith(f"| {task_id} |"):
                parts = task.cells(row)
                parts[3] = state
                parts[4] = ("[公开 #9999](https://github.com/"
                            "HelloMrDuan/tianji-knowledge-base/pull/9999)")
                parts[5] = "2026-10-11"
                rows[i] = "| " + " | ".join(parts) + " |"
                break
        else:
            self.fail(f"missing task {task_id}")
        return "\n".join(rows) + "\n"

    def appended_history(self, event):
        anchor = "\n## 怎样追加下一条"
        self.assertIn(anchor, self.history)
        return self.history.replace(anchor, "\n" + event + "\n" + anchor)

    def delta(self, new_status, new_history):
        with patch.object(task, "show", return_value=self.wbs):
            with patch.object(task, "read", return_value=self.wbs):
                return task.validate_pr_delta(
                    "base-sha", self.status, self.history, new_status, new_history
                )

    def test_exactly_one_updated_task_and_event_is_allowed(self):
        self.assertEqual(
            self.delta(self.changed_row(), self.appended_history(self.next_event())),
            "TJ-001.4",
        )

    def test_two_tasks_in_one_pr_is_rejected(self):
        rows = self.changed_row().splitlines()
        for i, row in enumerate(rows):
            if row.startswith("| TJ-004.3 |"):
                parts = task.cells(row)
                parts[3] = "进行中"
                rows[i] = "| " + " | ".join(parts) + " |"
                break
        with self.assertRaisesRegex(task.Invalid, "exactly one"):
            self.delta("\n".join(rows), self.appended_history(self.next_event()))

    def test_missing_new_event_is_rejected(self):
        with self.assertRaisesRegex(task.Invalid, "differs|exactly one"):
            self.delta(self.changed_row(), self.history)

    def test_rewriting_history_is_rejected(self):
        modified = self.appended_history(self.next_event()).replace(
            "原始视觉/场景基线", "人为改写旧事件", 1
        )
        with self.assertRaisesRegex(task.Invalid, "append-only"):
            self.delta(self.changed_row(), modified)

    def test_bootstrap_cannot_be_repeated_with_missing_one_side(self):
        with self.assertRaisesRegex(task.Invalid, "partial loss"):
            task.validate_pr_delta("base", self.status, None, self.status, self.history)


if __name__ == "__main__":
    unittest.main()
