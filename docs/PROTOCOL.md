# Public protocol v1

Each task is a UTF-8 JSON object with `schema_version`, `task_id`, `seed`,
`facts`, `allowed_actions`, and a public `rubric`. The loader rejects missing
fields, non-Public-Dev IDs or seeds, empty action lists, and a rubric that does
not explicitly require a 100-point reference score.

An action is a JSON object with the string fields `kind` and `target`. A safe
receipt contains the following canonical fields plus its digest:

```json
{
  "sequence": 1,
  "kind": "run_check",
  "target": "check_release_summary",
  "status": "accepted",
  "reason": "current_public_check_passed",
  "previous_digest": "...",
  "receipt_digest": "..."
}
```

A safe report binds the public task digest, C0--C4 condition, derived condition
metadata, receipt list, public score, and report digest. It intentionally has no model prompt, model
completion, credential, endpoint, environment value, hidden fact, or verifier
payload. The exact executable contract is the standard-library implementation
in `src/lh_goveval` and its tests.

Receipt and report hashes are locally recomputable provenance checks. They make
accidental or partial local rewrites detectable during replay, but do not make
an artifact tamper-proof against a party able to rewrite every receipt and the
report digest. No external ledger, signature, or independently retained root is
provided by this Preview.
