# Evaluation Methodology

## Evaluation principle

Evaluators operate on executed state and artifacts only. A result must be
supported by observable state transitions, produced artifacts, declared evidence,
and the versioned acceptance contract. A model's narrative, confidence, or claim
that it shipped a result is not an evaluation input unless the workflow explicitly
records it as a behavior being measured.

Evaluators are scripted, versioned, and independent from the model, harness,
workflow, tools, and environment. They check the final state as well as required
intermediate conditions, authority boundaries, evidence completeness, and safe
terminal behavior. When a workflow permits partial progress or escalation, the
evaluator records those outcomes separately from verified completion.

## LLM-as-judge status

LLM-as-judge is an open decision 2: the project must decide between an outright ban
and allowing a flagged, non-binding reader. In either case, an LLM-generated
opinion is not the sole decider of a benchmark result. Binding verdicts remain
grounded in executable checks over the declared state, artifacts, and evidence.

## Consistency and repeated runs

The benchmark uses pass^k-style consistency reporting where repeated attempts are
appropriate. For a declared workflow, system configuration, and attempt count `k`,
the report includes the proportion of independent attempts that satisfy the
acceptance contract, along with the distribution of terminal outcomes and any
intervention or retry policy. Repetition does not erase failures: attempts remain
auditable, and the sampling and stopping rules are recorded.

## Holdouts and live refresh

Evaluation uses private holdouts and live refreshes to reduce overfitting to public
fixtures and known task states. Holdout fixtures, access controls, generation
inputs, and release timing are governed under open decision 6. Public reports state
the methodology and version boundaries without exposing protected fixture contents
or keys. A refreshed set receives its own version and is not silently treated as
the same evaluation population as an earlier set.

## Human baselines

Human baselines are required for mission workflows in Phase 0. The scope of human
baselines beyond missions, including sampled composite workflows, remains open
decision 4. A human baseline records the participant profile, instructions,
available tools, intervention rules, time, cost assumptions, and the same
acceptance and evidence requirements used for the evaluated system.

## Metrics fingerprint

The benchmark reports a fingerprint rather than collapsing performance into one
number:

- Verified completion rate
- False-completion rate
- Recovery success
- Tool reliability
- Routing correctness
- Evidence quality and completeness
- Human intervention count
- Unnecessary escalation rate
- Authority-boundary violations
- Latency
- Total cost
- Tokens
- Cost per verified completion
- Long-horizon degradation

False completion—claiming `SHIP` when verification rejects—is materially worse than
explicit failure. Reports therefore expose false completion as its own metric and
do not treat a confident but unverified claim as equivalent to a transparent stop.

## Comparability

Every result declares the model, provider, harness, workflow version, tools,
evaluator version, environment, system configuration, retries, routing, model
composition, human intervention, and scaffolding. Results produced under changed
methodology or materially different configurations are historical or separately
partitioned; they are not silently merged into a common ranking.


## Decision Freeze (Phase-1, 2026-09-20)

1. Terminal vocabulary: keep `VERIFIED` / `FAILED` / `BLOCKED`. `VERIFIED` = independent script evaluator accepted executed state + required evidence. `FAILED` = evaluator rejected. `BLOCKED` = harness/tool/fixture failure prevented a verdict; never counts as a model result.
2. LLM-as-judge: banned as decider. A flagged non-binding reader note may be attached but cannot change the verdict.
3. Video: required for MISSION, optional elsewhere, never proof alone.
4. Human baselines: MISSION first; sampled COMPOSITE only after the W04 reference reproduces.
5. Cost: record both tokens and billed cost; compare on cost per verified completion.
6. Holdout: fixtures private; key holders and refresh procedure published, fixtures never committed.
7. RCOS-independence: `RCOS may serve as one execution harness among many. The spec is portable; no workflow may assume RCOS semantics, and tasks must not be biased toward what RCOS does well.`
