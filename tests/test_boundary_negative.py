from __future__ import annotations

import copy
import os
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
from audit_release import audit  # noqa: E402

from lh_goveval.runner import RunValidationError, run, run_reference, validate_report
from lh_goveval.tasks import TaskValidationError, load_all_tasks, validate_task


class BoundaryNegativeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tasks = {task["task_id"]: task for task in load_all_tasks()}

    def test_task_schema_and_public_namespace_reject_invalid_inputs(self) -> None:
        missing = copy.deepcopy(self.tasks["LHGE_DEV_EVIDENCE_001"])
        del missing["rubric"]
        with self.assertRaises(TaskValidationError):
            validate_task(missing)
        wrong_namespace = copy.deepcopy(self.tasks["LHGE_DEV_EVIDENCE_001"])
        wrong_namespace["task_id"] = "OTHER_001"
        with self.assertRaises(TaskValidationError):
            validate_task(wrong_namespace)
        wrong_seed = copy.deepcopy(self.tasks["LHGE_DEV_EVIDENCE_001"])
        wrong_seed["seed"] = "not-public-dev"
        with self.assertRaises(TaskValidationError):
            validate_task(wrong_seed)

    def test_report_schema_task_binding_and_digest_tampering_are_rejected(self) -> None:
        task = self.tasks["LHGE_DEV_EVIDENCE_001"]
        report = run_reference(task, "C0")
        malformed_schema = copy.deepcopy(report)
        malformed_schema["schema_version"] = "wrong-schema"
        with self.assertRaises(RunValidationError):
            validate_report(task, malformed_schema)
        wrong_task = copy.deepcopy(report)
        wrong_task["task_digest"] = "0" * 64
        with self.assertRaises(RunValidationError):
            validate_report(task, wrong_task)
        changed_score = copy.deepcopy(report)
        changed_score["score"]["score"] = 0
        with self.assertRaises(RunValidationError):
            validate_report(task, changed_score)

    def test_invalid_condition_and_recovery_before_guard_are_rejected(self) -> None:
        task = self.tasks["LHGE_DEV_RECOVERY_001"]
        with self.assertRaises(RunValidationError):
            run(task, "C5")
        report = run(task, "C4", [{"kind": "recover", "target": "restore_verified_checkpoint"}])
        recovery = next(item for item in report["receipts"] if item["kind"] == "recover")
        self.assertEqual("rejected", recovery["status"])
        self.assertIn("recovery_not_authorized_by_guard_state", recovery["reason"])

    def test_audit_rejects_surplus_path_forbidden_path_and_sensitive_pattern(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "allowlist.txt").write_text("allowlist.txt\nforbidden-paths.txt\nsafe.txt\n", encoding="utf-8")
            (root / "forbidden-paths.txt").write_text("blocked-area\n", encoding="utf-8")
            (root / "safe.txt").write_text("safe", encoding="utf-8")
            self.assertEqual([], audit(root))
            (root / "surplus.txt").write_text("surplus", encoding="utf-8")
            (root / "blocked-area").mkdir()
            (root / "blocked-area" / "item.txt").write_text("x", encoding="utf-8")
            (root / "credential.txt").write_text("sk-" + "x" * 24, encoding="utf-8")
            problems = audit(root)
            self.assertTrue(any("path not allowlisted: surplus.txt" in item for item in problems))
            self.assertTrue(any("forbidden path fragment: blocked-area/item.txt" in item for item in problems))
            self.assertTrue(any("openai_style_key pattern: credential.txt" in item for item in problems))

    def test_audit_rejects_symbolic_links(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "allowlist.txt").write_text("allowlist.txt\nforbidden-paths.txt\nlink.txt\n", encoding="utf-8")
            (root / "forbidden-paths.txt").write_text("", encoding="utf-8")
            target = root / "target.txt"
            target.write_text("outside candidate file", encoding="utf-8")
            link = root / "link.txt"
            try:
                os.symlink(target, link)
            except OSError as error:
                self.skipTest(f"symbolic links unavailable: {error}")
            self.assertTrue(any("symbolic link not permitted: link.txt" in item for item in audit(root)))
