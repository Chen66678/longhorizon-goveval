"""Fail closed if the candidate contains disallowed paths or common secret/path leaks."""
from __future__ import annotations

import fnmatch
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IGNORE_DIRS = {"__pycache__", ".pytest_cache", ".git"}
CONTENT_PATTERNS = {
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "github_token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "openai_style_key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "slack_token": re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"),
    "absolute_home_path": re.compile(r"(?<![A-Za-z0-9_])/(?:Users|home)/"),
}


def _patterns(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith("#")]


def audit(root: Path = ROOT) -> list[str]:
    allowed = _patterns(root / "allowlist.txt")
    forbidden = _patterns(root / "forbidden-paths.txt")
    problems: list[str] = []
    for path in sorted(root.rglob("*")):
        if any(part in IGNORE_DIRS for part in path.relative_to(root).parts):
            continue
        if path.is_dir():
            continue
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            problems.append(f"symbolic link not permitted: {relative}")
            continue
        if not path.is_file():
            problems.append(f"non-regular file not permitted: {relative}")
            continue
        if not any(fnmatch.fnmatch(relative, pattern) for pattern in allowed):
            problems.append(f"path not allowlisted: {relative}")
        if any(
            (fragment in path.relative_to(root).parts if "/" not in fragment else fragment in relative)
            for fragment in forbidden
        ):
            problems.append(f"forbidden path fragment: {relative}")
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            problems.append(f"non-text file not permitted: {relative}")
            continue
        for label, pattern in CONTENT_PATTERNS.items():
            if pattern.search(text):
                problems.append(f"{label} pattern: {relative}")
    return problems


def main() -> int:
    problems = audit()
    if problems:
        print("release audit failed:", *problems, sep="\n- ")
        return 1
    print("release audit passed: paths are allowlisted and no common secret/home-path pattern was found")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
