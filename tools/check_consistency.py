"""Check that public docs, package metadata, task contract, and CLI agree."""
from __future__ import annotations

import re
import subprocess
import sys
import tomllib
from pathlib import Path

from lh_goveval import __version__
from lh_goveval.runner import CONDITIONS
from lh_goveval.tasks import load_all_tasks


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_DOCUMENTS = {
    "README.md",
    "LICENSE",
    "LICENSE-DATA.md",
    "COPYRIGHT",
    "NOTICE",
    "docs/PUBLIC_SCOPE.md",
    "docs/INTEGRITY.md",
    "docs/PROTOCOL.md",
    "docs/REPRODUCIBILITY.md",
    "docs/INDEPENDENT-REVIEW-EVIDENCE.md",
}
ATTRIBUTION_FILES = {
    "pyproject.toml",
    "lhge_build_backend.py",
    "README.md",
    "NOTICE",
    "COPYRIGHT",
    "LICENSE-DATA.md",
}
FORBIDDEN_ATTRIBUTION_IDENTITIES = {"Project Owner", "Codex", "OpenAI", "AI agent", "codex@local"}


def check(root: Path = ROOT) -> list[str]:
    problems: list[str] = []
    metadata = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    project = metadata.get("project", {})
    if project.get("name") != "longhorizon-goveval":
        problems.append("package name differs from the public project name")
    if project.get("version") != __version__:
        problems.append("package and module versions differ")
    if project.get("authors") != [{"name": "Chen66678"}]:
        problems.append("public package attribution is not Chen66678 only")
    if metadata.get("project", {}).get("scripts", {}).get("lhge") != "lh_goveval.cli:main":
        problems.append("CLI entry point differs from implementation")
    backend = (root / "lhge_build_backend.py").read_text(encoding="utf-8")
    if f'VERSION = "{__version__}"' not in backend:
        problems.append("offline wheel backend version differs from package")
    if "Author: Chen66678\\n" not in backend:
        problems.append("offline wheel attribution is not Chen66678 only")
    for relative in REQUIRED_DOCUMENTS:
        if not (root / relative).is_file():
            problems.append(f"required public document missing: {relative}")
    if "Apache License" not in (root / "LICENSE").read_text(encoding="utf-8"):
        problems.append("code license text is incomplete")
    if "Creative Commons Attribution 4.0" not in (root / "LICENSE-DATA.md").read_text(encoding="utf-8"):
        problems.append("data/documentation license notice is incomplete")
    for relative in {"README.md", "NOTICE", "COPYRIGHT"}:
        if "Chen66678" not in (root / relative).read_text(encoding="utf-8"):
            problems.append(f"Chen66678 attribution missing: {relative}")
    for relative in ATTRIBUTION_FILES:
        text = (root / relative).read_text(encoding="utf-8")
        for identity in FORBIDDEN_ATTRIBUTION_IDENTITIES:
            if identity in text:
                problems.append(f"forbidden attribution identity in {relative}: {identity}")
    tasks = load_all_tasks(root / "public_dev" / "tasks")
    if len(tasks) != 3 or {task["task_id"] for task in tasks} != {task["task_id"] for task in load_all_tasks()}:
        problems.append("task discovery differs between explicit and default public roots")
    if set(CONDITIONS) != {"C0", "C1", "C2", "C3", "C4"}:
        problems.append("C0--C4 public smoke matrix is incomplete")
    return problems


def main() -> int:
    problems = check()
    if problems:
        print("consistency check failed:", *problems, sep="\n- ")
        return 1
    command = [sys.executable, "-m", "lh_goveval.cli", "--help"]
    help_text = subprocess.run(command, cwd=ROOT, env={"PATH": "", "PYTHONPATH": str(ROOT / "src"), "PYTHONDONTWRITEBYTECODE": "1"}, check=True, capture_output=True, text=True).stdout
    if not re.search(r"\bsmoke\b", help_text) or not re.search(r"\brun\b", help_text):
        print("consistency check failed:\n- CLI help does not expose smoke and run")
        return 1
    print("consistency check passed: docs, licenses, metadata, task contract, C0--C4 matrix, and CLI agree")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
