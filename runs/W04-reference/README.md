# W04 reference fixture (NOT a run — do not evaluate, do not cite as a result)

This directory is a MANUALLY CONSTRUCTED reference fixture from Phase 1, kept
for documentation only. It was built by hand, not produced by the trusted
runner; it has no trace, no ledger, no observed artifacts, and its
`terminal_outcome` field is a static placeholder. It MUST NEVER be represented
as an actual model execution or used to report model performance.

The v1 evaluator (`evals/w04-evaluator.py`, now superseded) accepted this
manifest's self-reported outcome without opening underlying evidence — that
trust gap is exactly what the corrective work closed.

For genuine execution evidence, see real run directories (e.g.
`runs/W04-smoke/`): runner-written `run-record.json`, hash-chained
`trace.jsonl`, hashed `artifacts/`, `ledger.json`, and an independent
`verdict.json` from `evals/w04-evaluator-v2.py`.
