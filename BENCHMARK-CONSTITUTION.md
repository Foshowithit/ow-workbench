# Benchmark Constitution

## Thesis

Can this model reliably participate in real workflows that produce verified outcomes?

## Non-negotiables

- Public failures stay public. A failed or blocked run is part of the benchmark record, subject to privacy, licensing, and security obligations.
- Claimed completion != verified completion. A model statement that work is complete never substitutes for an evaluator checking the resulting state and artifacts.
- Every result traces to an executed run with a retained run identifier, configuration, trace, and evidence record.
- The full run record names the model, provider, harness, workflow, tools, environment, relevant versions, and date.
- Fixtures are versioned, reviewable, and addressable so that a result can be tied to the exact task state used.
- Hidden injections are deterministic for a given workflow and fixture version; their presence and effect are auditable without exposing protected holdouts.
- Raw evidence is retained where licensing and privacy allow, with redaction or durable pointers when direct retention is not permitted.
- A methodology change renders prior results historical. Results from different methodology versions are not silently pooled or compared as if they were identical.
- The model under test is separated from the harness and the rest of the system. Harness assistance, tool behavior, scaffolding, and orchestration are not attributed to the model.
- Routing, multi-model use, retries, human intervention, and scaffolding are disclosed rather than hidden inside an aggregate score.

## Refusals

- No benchmark theater: tasks and reports must represent real, checkable work rather than demonstrations optimized for appearance.
- No cherry-picked demos: favorable examples cannot replace the complete declared evaluation set and its failures.
- No invented results: unpublished, simulated, inferred, or otherwise unexecuted outcomes are not presented as benchmark findings.
- No vibes scoring: judgments must be grounded in executable checks over state, artifacts, and declared evidence.
- No single-number leaderboard: the benchmark reports a metrics fingerprint, including completion, false completion, recovery, reliability, evidence, intervention, authority, latency, cost, and degradation measures.

