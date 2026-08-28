# LongHorizon GovEval — Open Preview

LongHorizon GovEval (LH-GovEval) is published as an offline Open Preview/pilot.
The immutable [`v0.1.0-preview`](https://github.com/Chen66678/longhorizon-goveval/releases/tag/v0.1.0-preview)
release provides the release manifest and a fixed public snapshot. Chen66678 is
the credited copyright holder.

The Preview contains three synthetic Public Dev demos and an offline
deterministic reference policy. It uses only the Python standard library: no
API key, network access, provider request, or model adapter is needed.

## What is included

- Three Public Dev tasks with public seeds, facts, rubrics, and truth.
- C0--C4 smoke controls: solo, prompt-only, structural authority, local
  provenance hash-chain, and C4-only bounded guard recovery.
- A deterministic state-machine runner, locally hash-chained receipts, safe
  report, public scorer, and negative tests.
- An allowlist and safety audit that rejects unknown files, common secret
  formats, home-directory paths, and prohibited source fragments.

The task pack is intentionally small. It is for integration and development;
it must not be used to make claims about governance effectiveness or model
ranking.

## Run

From the repository root:

```sh
PYTHONPATH=src python -m lh_goveval.cli smoke --output /tmp/lhge-smoke
PYTHONPATH=src python -m unittest discover -s tests -v
python tools/audit_release.py
python tools/build_manifest.py --output /tmp/lhge-release-manifest.json
python tools/fresh_copy_verify.py
```

The smoke command writes 15 safe reports (3 tasks × 5 conditions) plus a
public summary. Eleven cells are scored reference passes; the recovery demo is
explicitly unscored in C0--C3 because its guard/recovery mechanism is available
only in C4. The reference policy is deterministic and is named in every
reference report. A custom adapter is not included in this Preview.

## Deliberate limits

- All task truth is public because this is a Public Dev pack. It is not a
  substitute for sealed evaluation.
- C0--C4 are smoke semantics, not causal treatment estimates.
- Safe reports retain only public actions and deterministic receipts. There are
  no model prompts, raw model completions, credentials, or provider payloads.
- Receipt/report hashes are local replay checks, not an external append-only
  ledger or tamper-proof evidence across a trust boundary.
- A successful fresh-copy check is reproducibility evidence, not an independent
  review claim. See [docs/REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md).

See [docs/PUBLIC_SCOPE.md](docs/PUBLIC_SCOPE.md),
[docs/INTEGRITY.md](docs/INTEGRITY.md), and
[docs/REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md) for scope and verification
details.
