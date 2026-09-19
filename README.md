# ow-workbench

**Status: DESIGN / PRE-RELEASE — no official results yet.**

`ow-workbench` is a provisional name; branding is not locked.

## Thesis

Can this model reliably participate in real workflows that produce verified outcomes?

## Tiers

- **MICRO** — Isolated primitives for diagnosis, typically minutes-long and focused on one or two capabilities.
- **COMPOSITE** — Realistic 5–20 minute workflows that combine capabilities with deterministic failure injection.
- **MISSION** — Long-horizon, messy end-to-end deliverables with persistent, degrading state.

## Specification

- [Benchmark Constitution](BENCHMARK-CONSTITUTION.md)
- [Capability Coverage Matrix](CAPABILITY-COVERAGE-MATRIX.md)
- [Workflow Specification](WORKFLOW-SPEC.md)
- [Evaluation Methodology](EVALUATION-METHODOLOGY.md)
- [Evidence and Provenance](EVIDENCE-AND-PROVENANCE.md)
- [Contributing](CONTRIBUTING.md)

The benchmark records verified outcomes, failure recovery, evidence quality,
authority boundaries, intervention, latency, cost, and long-horizon degradation.
RCOS may be used as one harness among many, but it is not a dependency of the
portable workflow specification.

No model rankings are published in Phase 0.

