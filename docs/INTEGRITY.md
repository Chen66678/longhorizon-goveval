# Evaluation integrity

The deterministic primary score is calculated only from a Public Dev task's
public rubric and the report's locally hash-chained public receipts. The scorer
does not call a model or a network service, and it does not read a hidden
grader.

Each receipt has a sequence number, previous receipt digest, and digest of its
canonical fields. Each report binds the task digest, condition, derived
condition metadata, receipts, and recomputed score. `validate_report` rejects
a modified receipt, task mismatch, unknown condition, non-derived condition
metadata, non-reproducible score, or inconsistent report digest.

The hash chain and report digest are **local self-consistency checks**, not an
external append-only ledger, signature, or proof against a writer that can
replace the entire report and recompute hashes. They support deterministic
replay only. Crossing a trust boundary requires an independently retained
receipt root and an appropriate signature or other external authority; neither
is implemented in this Preview.

The runner retains all emitted receipts in its safe report. The Preview has no
raw model trajectory because the reference policy is a fixed deterministic
function, not a language-model call.

C0--C4 are interface smoke controls:

| Condition | Public behavior exercised |
| --- | --- |
| C0 | A single reference actor executes the task. |
| C1 | A public governance reminder is recorded as a control label. |
| C2 | The runner rejects an out-of-scope delegation. |
| C3 | Each receipt appends a locally recomputable provenance-hash record. |
| C4 | Only C4 enables a guard denial and at most one explicit recovery action. The recovery demo is explicitly not scored in C0--C3. |

These controls prove neither causal benefit nor security containment. They are
small, deterministic integration checks.
