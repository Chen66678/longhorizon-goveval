"""Small standard-library PEP 517 backend for an offline Preview wheel."""
from __future__ import annotations

import base64
import hashlib
import os
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DIST = "longhorizon_goveval"
VERSION = "0.1.0rc1"
DIST_INFO = f"{DIST}-{VERSION}.dist-info"


def _metadata() -> bytes:
    return (
        "Metadata-Version: 2.1\n"
        "Name: longhorizon-goveval\n"
        f"Version: {VERSION}\n"
        "Summary: Offline deterministic Open Preview for LongHorizon GovEval\n"
        "Requires-Python: >=3.11\n"
        "License: Apache-2.0\n"
        "Author: Chen66678\n"
    ).encode("utf-8")


def _wheel_metadata() -> bytes:
    return b"Wheel-Version: 1.0\nGenerator: lhge_build_backend\nRoot-Is-Purelib: true\nTag: py3-none-any\n"


def _record_row(path: str, contents: bytes) -> str:
    digest = base64.urlsafe_b64encode(hashlib.sha256(contents).digest()).decode("ascii").rstrip("=")
    return f"{path},sha256={digest},{len(contents)}"


def _wheel_files() -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    package_root = ROOT / "src" / "lh_goveval"
    for source in sorted(package_root.glob("*.py")):
        files[f"lh_goveval/{source.name}"] = source.read_bytes()
    for source in sorted((ROOT / "public_dev" / "tasks").glob("*.json")):
        files[f"lh_goveval/public_dev/tasks/{source.name}"] = source.read_bytes()
    files[f"{DIST_INFO}/METADATA"] = _metadata()
    files[f"{DIST_INFO}/WHEEL"] = _wheel_metadata()
    files[f"{DIST_INFO}/entry_points.txt"] = b"[console_scripts]\nlhge = lh_goveval.cli:main\n"
    return files


def build_wheel(wheel_directory: str, config_settings: object | None = None, metadata_directory: str | None = None) -> str:
    del config_settings, metadata_directory
    filename = f"{DIST}-{VERSION}-py3-none-any.whl"
    target = Path(wheel_directory) / filename
    files = _wheel_files()
    records = [_record_row(path, contents) for path, contents in sorted(files.items())]
    files[f"{DIST_INFO}/RECORD"] = ("\n".join(records) + f"\n{DIST_INFO}/RECORD,,\n").encode("utf-8")
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path, contents in sorted(files.items()):
            archive.writestr(path, contents)
    return filename


def prepare_metadata_for_build_wheel(metadata_directory: str, config_settings: object | None = None) -> str:
    del config_settings
    target = Path(metadata_directory) / DIST_INFO
    target.mkdir(parents=True, exist_ok=True)
    (target / "METADATA").write_bytes(_metadata())
    (target / "WHEEL").write_bytes(_wheel_metadata())
    (target / "entry_points.txt").write_text("[console_scripts]\nlhge = lh_goveval.cli:main\n", encoding="utf-8")
    (target / "RECORD").write_text("", encoding="utf-8")
    return DIST_INFO


def get_requires_for_build_wheel(config_settings: object | None = None) -> list[str]:
    del config_settings
    return []
