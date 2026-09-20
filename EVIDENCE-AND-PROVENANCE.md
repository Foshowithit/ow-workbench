# Evidence and Provenance

## Run manifest

Every executed run retains a manifest with, at minimum, the following fields:

- Model under test
- Provider
- Harness and harness version
- Workflow and workflow version
- Tools and tool versions or service identifiers
- Environment pin
- Start-state hash
- Date and time information sufficient for audit
- Cost
- Tokens
- Latency

The manifest also records the evaluator version, relevant system configuration,
retry and routing behavior, model composition, human intervention, scaffolding,
terminal outcome, and links or hashes for retained evidence. Fields that cannot be
reported because of licensing, privacy, or provider restrictions are identified
explicitly rather than silently omitted.

## Retention layers

The evidence record has separate retention layers:

1. **Trace:** the ordered record of meaningful actions, tool calls, observations,
   decisions, retries, escalations, and state transitions.
2. **Artifacts:** files, records, messages, outputs, and other durable work products
   created or changed by the run.
3. **Evaluator evidence:** the inputs, checks, hashes, diffs, assertions, and
   failure explanations used to produce the terminal verdict.
4. **Configuration:** the model, provider, harness, workflow, tools, evaluator,
   environment, and policy configuration needed to interpret the run.

Raw evidence is retained where licensing and privacy allow. Where raw retention is
not permitted, the record uses an access-controlled pointer, a content hash, and a
description of the unavailable material so the limitation is visible and later
auditable.

## Fixtures and content addressing

Fixtures are versioned and content-addressed. A run records the fixture version and
the hashes of the start state and relevant fixture inputs, allowing evaluators to
distinguish an actual change in task state from a change in model or environment.
Hidden fixtures may remain private, but their generation, versioning, and evaluation
contracts must support reproducible governance without publishing protected keys or
contents.

## Media policy

The repository does not carry huge media blobs. Large evidence is represented by a
stable pointer plus a cryptographic hash, with access and retention handled outside
the repository when necessary. Small, license-cleared extracts may be retained
directly when they are useful for inspection.

Video is inspectable evidence, never proof alone. A video record must be paired
with the relevant manifest, trace, artifacts, and evaluator checks; visual footage
cannot substitute for an independently verifiable final state.

## Six-way separation

Every run records six distinct components: the model under test, the harness, the
workflow, the tools, the evaluator, and the environment. The entire system
configuration is retained, including routing, retries, multi-model composition,
human intervention, and scaffolding. Configurations are never claimed equivalent
when they differ in capabilities, policies, versions, permissions, or observable
execution behavior.

This separation prevents harness help, tool behavior, evaluator policy, or
environmental advantage from being silently attributed to the model. It also makes
cross-system comparisons legible without implying that different system designs
are interchangeable.


## Run record vs verdict (Phase-1 P3)

The manifest rules above apply to two distinct documents with different
authors. The run record (written by the trusted runner) captures actual
events, artifacts, observations, configuration, and the participant's
terminal claim; it never contains a terminal outcome — the schema rejects
the field. The verdict (written by the independent evaluator) is the only
document carrying `VERIFIED` / `FAILED` / `BLOCKED`, and every verdict check
rehashes the underlying evidence rather than trusting any claim. A manually
constructed reference manifest may exist as a documentation fixture, but it
is marked `execution_class: reference-fixture` and must never be represented
as an actual model execution.
