# Verification record

Verification date: 2026-08-28.

The following checks were run using Python 3.14:

| Check | Result |
| --- | --- |
| Unit tests | The 18-test in-tree suite covers negative evidence, scope, recovery, report tampering, wrong schemas, prohibited paths, sensitive patterns, symbolic links, manifest canonicalization, and all 15 C0--C4 smoke cells. |
| Source smoke | 15 safe reports: 11 deterministic scored passes and 4 explicit C4-control-unavailable, unscored reports; no API key or network dependency. |
| Archive audit | Passed allowlist, prohibited-path, common secret-format, and home-path checks. |
| Public consistency | Passed documentation, license, package metadata, C0--C4 matrix, task contract, and CLI-help consistency checks. |
| Release manifest | Schema `lhge.release-manifest.v2`, created outside the tree from allowlisted files; the release binding is its self-excluding `canonical_manifest_sha256`, not the hash of the pretty output file. |
| Fresh-copy verification | Passed from a temporary copy with no Git history and a minimal environment. |
| Offline package check | Built a wheel without build requirements or package index access, installed it into a temporary target, and ran the installed smoke command. |

The fresh-copy verifier sets `PIP_NO_INDEX=1`, disables pip's version check and
cache, and uses only repository files. This record describes observed
engineering checks. It does not establish independent review, rights clearance,
or hosted clean-clone verification.
