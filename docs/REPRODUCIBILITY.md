# Reproducibility and verification

The Preview requires Python 3.11 or newer and only the standard library.
`requirements.lock` explicitly records that no third-party dependency is
needed. Reports are canonical JSON and use SHA-256 digests from the standard
library.

Run these commands from the repository root:

```sh
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m lh_goveval.cli smoke --output /tmp/lhge-smoke
python tools/audit_release.py
python tools/build_manifest.py --output /tmp/lhge-release-manifest.json
python tools/fresh_copy_verify.py
```

## Release-manifest canonicalization

`tools/build_manifest.py` writes schema `lhge.release-manifest.v2`. Its
release binding is the `canonical_manifest_sha256` field, **not** the SHA-256
of the human-readable JSON output file. The field is computed from the manifest
payload with the digest field omitted, encoded as UTF-8 compact JSON with
`sort_keys=True` and separators `(',', ':')`. The payload records the release
identifier, sorted POSIX-relative file paths, byte sizes, SHA-256 file digests,
and the canonicalization declaration itself.

Generate the output outside the tree. It is not an input to the manifest, so
formatting, a trailing newline, or output location cannot affect
`canonical_manifest_sha256`. An archive reviewer can regenerate the manifest
from the fixed archive and compare that named field to the release artifact.

`fresh_copy_verify.py` creates a temporary copy that excludes Git history and
generated files; it then runs the audit, tests, and smoke command with a
minimal environment containing only `PATH`, `PYTHONPATH`, and
`PYTHONDONTWRITEBYTECODE`. It makes no network request and does not read an API
key. This is a **fresh-copy** verification, not a hosted clean-clone or
independent-review claim. The release tag and manifest asset provide the fixed
Open Preview release reference.
