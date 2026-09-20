# Schemas

Three documents, three authors, three jobs. Never merged:

- `workflow.schema.json` — static workflow DEFINITION (expected behavior, permitted actions, acceptance criteria, evaluation config). Never carries an outcome.
- `run-record.schema.json` — execution observation written by the trusted runner only. Records configuration, hashes, cost, latency, and the participant's claim. MUST NOT contain `terminal_outcome`; the schema rejects it.
- `verdict.schema.json` — the only place a terminal outcome may appear. Written by the independent evaluator named in the definition.

All three use `additionalProperties: false`; outcomes are closed to the `VERIFIED`/`FAILED`/`BLOCKED` enum; content hashes match `^sha256:[0-9a-f]{64}$`. See `WORKFLOW-SPEC.md` ("Definition vs execution record vs verdict") for the doctrine.
