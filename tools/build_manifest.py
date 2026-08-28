"""Create a deterministic, archive-recomputable manifest for a candidate tree."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from audit_release import ROOT, audit


IGNORED_PARTS = {".git", "__pycache__", ".pytest_cache", "build", "dist"}
SCHEMA_VERSION = "lhge.release-manifest.v2"
CANDIDATE_ID = "longhorizon-goveval-open-preview-0.1.0rc1"
CANONICALIZATION = {
    "digest_scope": "all manifest payload fields excluding canonical_manifest_sha256",
    "encoding": "utf-8",
    "json": "sort_keys=true; separators=(',', ':')",
    "path_order": "ascending POSIX-relative paths",
    "generated_output": "write outside candidate tree; generated output is not a manifest input",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_manifest_bytes(payload: dict[str, object]) -> bytes:
    """Encode the digest payload independently of presentation formatting."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def build_manifest(root: Path = ROOT) -> dict[str, object]:
    problems = audit(root)
    if problems:
        raise ValueError("candidate is not audit-clean: " + "; ".join(problems))
    files = []
    for path in sorted(root.rglob("*")):
        if path.is_dir() or any(part in IGNORED_PARTS for part in path.relative_to(root).parts):
            continue
        files.append({"path": path.relative_to(root).as_posix(), "sha256": sha256(path), "bytes": path.stat().st_size})
    body = {
        "schema_version": SCHEMA_VERSION,
        "candidate": CANDIDATE_ID,
        "canonicalization": CANONICALIZATION,
        "file_count": len(files),
        "files": files,
    }
    body["canonical_manifest_sha256"] = hashlib.sha256(canonical_manifest_bytes(body)).hexdigest()
    return body


def main() -> int:
    parser = argparse.ArgumentParser(description="write a deterministic LH-GovEval candidate manifest")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text(json.dumps(build_manifest(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote release manifest: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
