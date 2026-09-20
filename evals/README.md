# Evaluators

Versioned, independent evaluator definitions that check executed state, artifacts, acceptance contracts, evidence completeness, and authority boundaries without making an LLM opinion the sole binding verdict. LLM-as-judge is banned as decider (Phase-1 freeze).

- `evals/w04-evaluator.py` (v1) — SUPERSEDED. Trusted the manifest's self-reported outcome without opening underlying evidence. Retained for history; never use for new runs.
- `evals/w04-evaluator-v2.py` (v2, binding) — verdict from execution evidence only. Usage: `python3 evals/w04-evaluator-v2.py <run-dir>`; writes `verdict.json`; exit 0=VERIFIED 1=FAILED 2=BLOCKED. Rehashes fixture, trace, artifact, and ledger bytes; checks evaluator/workflow binding; enforces refusal reason and fixture binding; fails closed on tampering.
- `evals/w04-evaluator-v2-test.py` — adversarial suite (17 legs): forged/mutated/absent evidence, violator and sneaky modes, false SHIP claims, corrupt fixture, missing trace/ledger, tampered trace. Proves the evaluator rejects falsified success even when the run record claims it. Publish test results separately from model benchmark results.

Evaluator and fixture protection: the participant writes only inside the runner's quarantine directory. Fixtures, evaluator scripts, ledger, trace, and run record live outside the participant's writable area. The evaluator pins its own `evaluator_ref`/`evaluator_version` against the run record before checking anything else.
