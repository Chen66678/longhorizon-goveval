"""Verify a fresh local copy; this intentionally makes no claim about a remote clone."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache", "build", "dist", "*.egg-info", "reports")


def invoke(command: list[str], cwd: Path, env: dict[str, str]) -> None:
    subprocess.run(command, cwd=cwd, env=env, check=True)


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="lhge-fresh-copy-") as temporary:
        temporary_root = Path(temporary)
        copy_root = temporary_root / "longhorizon-goveval"
        artifact_root = temporary_root / "artifacts"
        shutil.copytree(ROOT, copy_root, ignore=EXCLUDED)
        if (copy_root / ".git").exists():
            raise RuntimeError("fresh-copy candidate unexpectedly contains Git history")
        environment = {
            "PATH": os.environ.get("PATH", ""),
            "PYTHONPATH": str(copy_root / "src"),
            "PYTHONDONTWRITEBYTECODE": "1",
            "PIP_NO_INDEX": "1",
            "PIP_DISABLE_PIP_VERSION_CHECK": "1",
            "PIP_NO_INPUT": "1",
            "PIP_NO_CACHE_DIR": "1",
        }
        invoke([sys.executable, "tools/audit_release.py"], copy_root, environment)
        invoke([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], copy_root, environment)
        invoke([sys.executable, "-m", "lh_goveval.cli", "smoke", "--output", str(artifact_root / "reports")], copy_root, environment)
        invoke([sys.executable, "tools/build_manifest.py", "--output", str(artifact_root / "release-manifest.json")], copy_root, environment)
        invoke([sys.executable, "-m", "pip", "wheel", "--no-deps", "--no-build-isolation", "--wheel-dir", str(artifact_root / "wheel"), "."], copy_root, environment)
        wheel = next((artifact_root / "wheel").glob("*.whl"), None)
        if wheel is None:
            raise RuntimeError("offline wheel build did not produce a wheel")
        install_root = artifact_root / "installed"
        invoke([sys.executable, "-m", "pip", "install", "--no-deps", "--target", str(install_root), str(wheel)], copy_root, environment)
        installed_environment = {"PATH": os.environ.get("PATH", ""), "PYTHONPATH": str(install_root), "PYTHONDONTWRITEBYTECODE": "1", "PIP_NO_INDEX": "1"}
        invoke([sys.executable, "-m", "lh_goveval.cli", "smoke", "--output", str(artifact_root / "installed-reports")], copy_root, installed_environment)
        summary = artifact_root / "reports" / "summary.json"
        manifest = artifact_root / "release-manifest.json"
        if not summary.is_file() or not manifest.is_file():
            raise RuntimeError("fresh-copy verification did not produce its public artifacts")
    print("fresh-copy verification passed: local copy, no Git history, no API key, no network dependency")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
