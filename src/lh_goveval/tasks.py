"""Public Dev task loading and deterministic validation."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


TASK_SCHEMA = "lhge.public-dev-task.v1"
_SOURCE_TASK_ROOT = Path(__file__).resolve().parents[2] / "public_dev" / "tasks"
_PACKAGED_TASK_ROOT = Path(__file__).resolve().parent / "public_dev" / "tasks"
TASK_ROOT = _SOURCE_TASK_ROOT if _SOURCE_TASK_ROOT.is_dir() else _PACKAGED_TASK_ROOT
REQUIRED_KEYS = {"schema_version", "task_id", "seed", "title", "facts", "allowed_actions", "rubric"}


class TaskValidationError(ValueError):
    """Raised when a Public Dev task is not in the deliberately small contract."""


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def task_digest(task: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(task)).hexdigest()


def validate_task(task: dict[str, Any]) -> None:
    missing = REQUIRED_KEYS - set(task)
    if missing:
        raise TaskValidationError(f"missing task fields: {sorted(missing)}")
    if task["schema_version"] != TASK_SCHEMA:
        raise TaskValidationError("unsupported task schema")
    if not isinstance(task["task_id"], str) or not task["task_id"].startswith("LHGE_DEV_"):
        raise TaskValidationError("task_id must be a Public Dev LHGE_DEV identifier")
    if not isinstance(task["seed"], str) or not task["seed"].startswith("lhge-public-dev-"):
        raise TaskValidationError("task seed is not a Public Dev seed")
    if not isinstance(task["facts"], dict) or not isinstance(task["rubric"], dict):
        raise TaskValidationError("facts and rubric must be JSON objects")
    if not task["allowed_actions"] or not all(isinstance(item, str) for item in task["allowed_actions"]):
        raise TaskValidationError("allowed_actions must be a non-empty string list")
    if task["rubric"].get("minimum_score") != 100:
        raise TaskValidationError("Public Dev reference tasks require an explicit 100-point rubric")


def discover_tasks(root: Path = TASK_ROOT) -> list[Path]:
    return sorted(root.glob("LHGE_DEV_*.json"))


def load_task(task_id: str, root: Path = TASK_ROOT) -> dict[str, Any]:
    path = root / f"{task_id}.json"
    if path.parent != root or not path.is_file():
        raise TaskValidationError(f"unknown Public Dev task: {task_id}")
    try:
        task = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise TaskValidationError(f"invalid JSON in {path.name}") from error
    validate_task(task)
    return task


def load_all_tasks(root: Path = TASK_ROOT) -> list[dict[str, Any]]:
    tasks = [load_task(path.stem, root) for path in discover_tasks(root)]
    ids = [task["task_id"] for task in tasks]
    seeds = [task["seed"] for task in tasks]
    if len(tasks) != 3 or len(ids) != len(set(ids)) or len(seeds) != len(set(seeds)):
        raise TaskValidationError("Open Preview requires exactly three distinct Public Dev tasks and seeds")
    return tasks
