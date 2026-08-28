"""Command line entry point for offline Open Preview smoke runs."""
from __future__ import annotations

import argparse
from pathlib import Path

from .runner import CONDITIONS, render_json, run_reference, validate_report
from .tasks import load_all_tasks, load_task


def _write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def command_smoke(output: Path) -> int:
    reports = []
    for task in load_all_tasks():
        for condition in CONDITIONS:
            report = run_reference(task, condition)
            validate_report(task, report)
            _write(output / "reports" / f"{task['task_id']}__{condition}.json", render_json(report))
            reports.append(report)
    summary = {
        "schema_version": "lhge.public-smoke-summary.v1",
        "report_count": len(reports),
        "scored_passed": sum(report["score"]["passed"] for report in reports if report["score"]["scorable"]),
        "not_scored": sum(not report["score"]["scorable"] for report in reports),
        "scored_failed": sum(report["score"]["scorable"] and not report["score"]["passed"] for report in reports),
        "conditions": list(CONDITIONS),
        "task_ids": [task["task_id"] for task in load_all_tasks()],
        "network_used": False,
        "api_key_required": False,
    }
    _write(output / "summary.json", render_json(summary))
    return 0 if summary["scored_failed"] == 0 and summary["scored_passed"] + summary["not_scored"] == summary["report_count"] else 1


def command_run(task_id: str, condition: str, output: Path) -> int:
    task = load_task(task_id)
    report = run_reference(task, condition)
    validate_report(task, report)
    _write(output, render_json(report))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="lhge", description="Offline LongHorizon GovEval Open Preview")
    commands = parser.add_subparsers(dest="command", required=True)
    smoke = commands.add_parser("smoke", help="run all three Public Dev tasks under C0--C4")
    smoke.add_argument("--output", type=Path, required=True)
    run_parser = commands.add_parser("run", help="run one Public Dev task with the reference policy")
    run_parser.add_argument("--task", required=True)
    run_parser.add_argument("--condition", choices=sorted(CONDITIONS), required=True)
    run_parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "smoke":
        return command_smoke(args.output)
    return command_run(args.task, args.condition, args.output)


if __name__ == "__main__":
    raise SystemExit(main())
