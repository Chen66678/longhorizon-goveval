# Reproduction evidence index

Scope: this index enables repeatable review of the Open Preview without
embedding task text, public truth, action traces, credentials, raw outputs,
host paths, or source-control history.

## Observable behavior

1. The Preview contains exactly three Public Dev task manifests and five smoke
   conditions (C0--C4), producing fifteen deterministic safe reports: eleven
   scored reference passes and four explicitly unscored recovery cells whose
   C4-only mechanism is unavailable.
2. It requires no API key, provider endpoint, model call, or network access.
3. Its allowlist audit rejects surplus files, symbolic links, prohibited source
   fragments, common credential formats, and absolute home-directory paths.
4. A fresh copy excludes Git history and generated artifacts, then runs the
   audit, test suite, source smoke, offline wheel build/install smoke, and
   release-manifest generation.

## Commands

Run from the repository root with Python 3.11 or later:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m lh_goveval.cli smoke --output /tmp/lhge-review-smoke
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python tools/check_consistency.py
PYTHONDONTWRITEBYTECODE=1 python tools/audit_release.py
PYTHONDONTWRITEBYTECODE=1 python tools/fresh_copy_verify.py
```

The smoke output and release manifest remain outside the tree. Record command
exit status, Python version, and the digest of the generated manifest alongside
any reproduction result.

## Scope of this index

This index records reproducible commands and observable behavior for the
published Public Dev pack. Scientific conclusions remain limited to the
published tasks and their deterministic smoke semantics.
