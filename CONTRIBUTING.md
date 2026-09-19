# Contributing

ow-workbench is a public, docs-first benchmark project. Contributions should make
workflow execution more testable, auditable, and honest without turning Phase 0
into a results repository.

## Proposing workflows

Propose a workflow by describing its tier, objective, initial state, inputs,
available capabilities and tools, environment, constraints, hidden deterministic
fixture strategy, authority boundary, acceptance contract, independent evaluator,
required evidence, and terminal outcomes. Map the proposal to the capability
matrix and explain which existing workflow it complements rather than replacing.
Include deterministic failure modes and a clear distinction between a claimed
completion and a verified state.

## Proposing fixtures

Propose fixtures with a version identifier, provenance, content-addressing plan,
initial-state description, expected invariants, injected failure conditions, and
privacy and licensing review. Keep public examples small and reproducible. Large
media belongs outside the repository behind a pointer and hash, not as a committed
blob.

## Proposing evaluators

Propose evaluators as versioned, executable checks over state and artifacts. State
the acceptance assertions, evidence inputs, failure explanations, authority-boundary
checks, and known blind spots. An evaluator must not rely on an LLM opinion as its
sole binding decision-maker. Report any human review or non-binding reader role
separately from the scripted verdict.

## Holdout protection

Never commit holdout fixtures or keys. Do not include private fixture contents,
credentials, access tokens, service accounts, or instructions that would weaken
holdout protection. Use approved access-controlled storage and publish only the
methodology, hashes, governance metadata, and release information allowed by the
holdout policy.

## No keys or secrets

Never commit keys, passwords, tokens, private URLs, credentials, personal data, or
secret configuration. Before opening a change, inspect generated files, logs,
archives, notebooks, and media metadata as well as source text. Replace sensitive
material with a documented pointer, redacted example, or synthetic fixture.

## Maturity honesty

Mark speculative content as speculative. Distinguish approved design, proposed
workflow, implemented evaluator, executed run, and published result. Do not imply
that a draft task has been validated, that an unrun evaluator has produced a score,
or that a harness-specific behavior is a model capability. Phase-0 documentation
must not present rankings or official results.

