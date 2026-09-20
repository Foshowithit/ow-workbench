# Workflow Specification

Every benchmark workflow is defined by the following canonical chain, in order:

`Initial State -> Objective -> Inputs -> Available Capabilities/Tools -> Environment -> Constraints -> Hidden Deterministic Fixtures -> Authority Boundary -> Acceptance Contract -> Independent Evaluation -> Required Evidence -> Terminal Outcome`

## Initial State

The initial state is the complete, inspectable starting condition presented to the
system: files, records, messages, application state, permissions, known defects,
and any declared history. It is versioned or content-addressed where practical so
that independent runs begin from the same contractually relevant state.

## Objective

The objective states the outcome the participant is asked to achieve, in language a
real operator or customer could use. It describes the intended result and material
success conditions without prescribing an implementation path or granting authority
that belongs elsewhere in the chain.

## Inputs

Inputs are the information and artifacts available at task start or through
declared interactions. Each input has a provenance, an availability rule, and a
clear distinction between participant-visible information and information reserved
for evaluation.

## Available Capabilities/Tools

This link enumerates the capabilities and tools the evaluated system may use,
including their interfaces, limits, and observable side effects. Tool availability
is part of the run configuration; tool behavior must not be mistaken for model
capability, and any routing or orchestration layer is recorded separately.

## Environment

The environment defines the software, services, data stores, identities,
permissions, network conditions, clocks, versions, and resource limits in which the
workflow executes. It includes enough pinning and provenance to explain meaningful
differences between runs without claiming that distinct environments are
equivalent.

## Constraints

Constraints state time, budget, format, safety, privacy, licensing, rate, authority,
and operational limits. They also identify prohibited shortcuts and conditions that
must cause a stop, escalation, or explicit failure rather than an unverified claim
of success.

## Hidden Deterministic Fixtures

Hidden deterministic fixtures provide controlled defects, contradictions, stale
revisions, unavailable dependencies, or other failure conditions needed to test
recovery and verification. For a fixed workflow and fixture version, injections are
reproducible; protected holdouts remain private while their generation and
evaluation contracts remain governable.

## Authority Boundary

The authority boundary specifies what the participant may inspect, change, approve,
send, publish, purchase, delete, or otherwise commit, and what requires a human or
other named authority. Crossing the boundary is evaluated as a distinct event, even
when the resulting artifact appears useful.

## Acceptance Contract

The acceptance contract defines the observable conditions for each intended
deliverable, including required state transitions, artifact properties, evidence,
and safe terminal behavior. It distinguishes a verified deliverable from a merely
plausible response and states what counts as an acceptable partial or stopped
outcome.

## Independent Evaluation

Independent evaluation runs scripted checks against executed state and artifacts,
not against the model's narrative alone. Evaluators are versioned separately from
the workflow and harness, and their checks report both success conditions and
material violations such as false completion, authority-boundary violations, or
missing evidence.

## Required Evidence

Required evidence is the minimum retained record needed to reproduce and audit the
evaluation: run manifest, relevant trace, artifacts, evaluator evidence, hashes,
and configuration provenance. Evidence may use pointers when raw retention is
restricted; inspectable video can supplement a record but is never proof by itself.

## Terminal Outcome

The terminal outcome records the evaluator-supported disposition of the workflow.
For Phase 0, the proposed outcomes are `VERIFIED`, `FAILED`, and `BLOCKED`, with
semantics marked provisional pending open decision 1. A terminal label must be
derived from the acceptance contract and independent evaluation, not from the
participant's assertion.

## Harness independence

RCOS may serve as one execution harness among many. The spec is portable; no workflow may assume RCOS semantics, and tasks must not be biased toward what RCOS does well.


## Successful stop vs blocked execution (Phase-1)

- Successful stop: the runner correctly refused or stopped at the authority boundary, produced the required refusal evidence, and the evaluator accepts the refusal as the intended outcome. Terminal outcome is `VERIFIED`.
- Blocked execution: broken tools, missing fixtures, or harness failure prevented a verdict. Terminal outcome is `BLOCKED` and never counts as a model result.
- W04 approval-stop is the reference proof for this distinction.

## Schema hardening (Phase-1)

Free-form objects are no longer sufficient for the load-bearing links. Every workflow definition must carry `environment_identity` plus `environment_start_state_hash`, `fixture_version` plus `fixture_content_hash`, and `evaluator_ref` plus `evaluator_version`. Acceptance criteria must be observable checks in `acceptance_checks` against executed state or artifacts. Definitions missing these fail validation before they can run.

## Definition vs execution record vs verdict (Phase-1 P3)

Three documents, three authors, three jobs. Never merged:

1. **Workflow definition** (`workflows/<ID>-*.json`, validated by
   `schemas/workflow.schema.json`) — static. Specifies expected behavior,
   permitted actions, acceptance criteria, and evaluation config. Carries the
   load-bearing bindings: `environment_identity` +
   `environment_start_state_hash`, `fixture_version` + `fixture_content_hash`,
   `evaluator_ref` + `evaluator_version`, and an `acceptance_checks` array.
   Never carries an outcome: its `terminal_outcome` field names the *intended*
   disposition for correct behavior under the acceptance contract (a stop-task
   such as W04 intends `VERIFIED` for a correct stop), never what happened.
   The narrative markdown beside it (`workflows/<ID>-*.md`) is documentation;
   the JSON definition is the binding artifact.

2. **Run record** (`runs/<run-id>/run-record.json`, validated by
   `schemas/run-record.schema.json`) — written by the trusted runner only,
   after execution. Records configuration (model, provider, harness, runner
   version), fixture and environment hashes, trace hash, artifact path+hash
   list, cost, latency, and the participant's terminal *claim*. MUST NOT
   contain `terminal_outcome`. The schema rejects it: a run record that
   declares its own outcome is malformed, full stop. `execution_class` is
   `real-execution` for genuine runs through the trusted boundary; anything
   else (reference fixtures, drafts) is never evaluated as a benchmark run.

3. **Verdict** (`runs/<run-id>/verdict.json`, validated by
   `schemas/verdict.schema.json`) — written by the independent evaluator
   named in the definition, and only by that evaluator. The sole place a
   terminal outcome may appear. `VERIFIED` = executed state plus required
   evidence satisfied the acceptance contract. `FAILED` = the evaluator
   rejected. `BLOCKED` = harness, tool, or fixture failure prevented a
   verdict; never counts as a model result.

Why the split: the corrective review of W04 v1 showed an evaluator that
trusted the manifest's self-reported outcome without opening the underlying
evidence. Separation makes that class of failure structural instead of
attentional — no single file can assert success, because no single file is
allowed to contain both the observation and the disposition.

## Executable acceptance checks

Acceptance criteria are not prose. Each entry in `acceptance_checks`
declares:

- `id` — stable check name referenced by the workflow spec,
- `statement` — what must hold, in plain language,
- `proven_by` — the evaluator check ids that enforce it (prose alone
  enforces nothing),
- `evidence` — the run-record, trace, artifact, or ledger locations the
  evaluator opens independently.

An acceptance check with no `proven_by` mapping to a real evaluator check is
a gap, not a criterion. W04's three checks (`refusal_recorded`,
`no_self_approval`, `evidence_complete`) each map to named checks in
`evals/w04-evaluator-v2.py`, and the adversarial suite
(`evals/w04-evaluator-v2-test.py`, 17 legs) proves the mapping bites:
forged, mutated, or absent evidence fails even when the run record claims
success.

## Evaluator and fixture protection

The participant under test — model or harness — must never be able to modify
the evaluator, the fixtures, the ledger, the trace, or the run record during
execution:

- The runner invokes the participant through a constrained interface: the
  participant writes only inside a quarantine directory (`participant_out/`
  in the W04 runner). The runner copies each file to `artifacts/`, hashes
  both copies, and records an `artifact_observed` trace entry.
- Fixture files, evaluator scripts, `ledger.json`, `trace.jsonl`, and
  `run-record.json` live outside the participant's writable area.
- The evaluator rehashes every byte it relies on: fixture bytes, trace
  bytes, artifact disk bytes, ledger bytes. A hash mismatch between record,
  disk, and trace observation is `FAILED` (tampering) or `BLOCKED`
  (corrupt infrastructure), never silently accepted.
- The evaluator pins its own identity: it checks the run record's
  `evaluator_ref` and `evaluator_version` against its own. A record pointing
  at a different evaluator is refused.

## Schema discipline

Load-bearing schema fields are exact-typed or they do not ship:
`additionalProperties: false` on the definition, run-record, and verdict
schemas; `terminal_outcome` and `verdict` closed to the
`VERIFIED`/`FAILED`/`BLOCKED` enum; content hashes constrained to
`^sha256:[0-9a-f]{64}$`. Descriptive chain links (`initial_state`,
`constraints`, `hidden_fixtures`, and siblings) remain objects — they carry
context, not verdicts — but nothing that decides an outcome travels through
an uncontrolled free-form field.
