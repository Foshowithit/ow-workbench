# Runs

Each run directory holds one execution through the trusted boundary:

- `run-record.json` — what the runner observed (configuration, hashes, cost, latency, participant claim). Never an outcome.
- `trace.jsonl` — ordered record of execution events with artifact observations.
- `artifacts/` — participant outputs copied and hashed by the runner at observation time.
- `participant_out/` — quarantine directory: the only place the participant may write.
- `ledger.json` — environment end-state evidence (spend ledger for W04).
- `verdict.json` — the independent evaluator's disposition. The ONLY file that may carry `VERIFIED`/`FAILED`/`BLOCKED`.

Record format: `schemas/run-record.schema.json`. Verdict format: `schemas/verdict.schema.json`. Manifest contract and provenance rules: `EVIDENCE-AND-PROVENANCE.md`. No media blobs.

`runs/W04-reference/` is a manually constructed reference fixture for documentation, NOT a real execution — never evaluated, never a benchmark result. Real executions live in directories like `runs/W04-smoke/` with full evidence packages.
