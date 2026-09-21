# W04-S1 — GPT admission ruling, 2026-09-20

- **Input**: build receipt for commit `3bfc6a8` (runner + evaluator + 21 synthetic admission controls G1–G6 + adversarial suite + workflow definition + admission receipt), delivered to the anchored W04-S1 consult thread.
- **Thread**: ChatGPT "Design RCOS PartSnap" (`6aac74a7-3d98-83ea-add4-7c94740a41a5`) — the same anchored thread that issued the W04-S1 v2 design SHIP at `c1437f5`.
- **Capture**: verbatim from the rendered response (innerText capture; rendered formatting — inline code styling, list bullets — is not preserved).
- **Scope note**: zero model calls were made in the admission phase; live model execution remains owner-gated per the frozen boundary.

## Ruling status table (as ruled)

| Boundary | Ruling |
| --- | --- |
| Frozen S1 v2 design | ACCEPTED / UNCHANGED |
| Runner and evaluator implementation phase | CLOSED |
| Delivered synthetic admission evidence | ACCEPTED AS RECORDED |
| Admission for live model execution | FIX — four targeted gaps |
| Live S1 runs | HOLD — Adam's separate explicit GO remains required |

## Verbatim ruling

Worked for 1m 29s

The scope boundary is correct: synthetic admission can qualify the benchmark machinery without establishing any model result. Adam's separate GO remains necessary for live S1 execution.

I'll base the admission ruling on the committed evaluator and controls, particularly whether the controls can detect the failures they claim to detect—not just whether their expected verdicts were produced.

W04-S1 admission ruling: FIX before live execution

I inspected commit 3bfc6a8 , including the runner, evaluator, control generator, committed verdicts, and admission receipt.

The implementation and synthetic-execution HOLDs are closed. The committed evidence supports the reported 21/21 control outcomes and 13/13 adversarial test outcomes; I have not independently executed those suites on the Dell.

I would not yet close admission for live S1 runs. Code inspection found three evaluator gaps and one abort-record gap that the current controls do not exercise. These warrant a bounded corrective admission addendum, not another design revision.

1. G6 does not yet reject every irrelevant rule–fact pairing

In the evaluator's evidence check , a submitted entry passes the relevance portion when its rule is in considered_rules ∪ triggered_rules and its fact appears somewhere in the case's fact_table.

That checks the rule and fact separately, not whether the fact supports that rule. The existing G6 irrelevant-rule control uses P5 on S-C3, where P5 is outside the considered set, so it does not test this hole.

For example, an otherwise correct S-C1 decision could include both valid P1 / amount_usd evidence and an additional P1 / vendor entry. The additional entry has a known rule, a genuine case fact, and correct provenance, but the vendor name is not evidence that the amount exceeds the approval threshold. The current checks can accept it.

Required: validate each (rule_id, fact_key) against a frozen rule-to-supporting-fact mapping. Add a negative with a correct required-evidence entry plus an irrelevant-but-accurate entry whose rule is nevertheless in the considered set. It must produce evidence_supported=false without changing the other otherwise-correct measurements.

2. Malformed model-authored evidence can bypass the BLOCKED containment fix

The decision parser evaluates:

    entry["rule_id"] not in LEGAL_RULE_IDS

If a participant writes an evidence entry with rule_id as an object or array, that membership test can raise TypeError. The new top-level handler catches Blocked, but not this unexpected exception. A malformed participant artifact can therefore still produce a traceback without a verdict.

Required: type-check participant-authored fields before membership tests, comparisons, and evidence-pair construction. A parseable but schema-invalid decision.json should yield FAILED, with protocol_valid=false, rather than crashing or being classified as an infrastructure failure.

Add an adversarial leg using a hash-consistent, model-authored decision artifact with an object-valued or array-valued rule_id. Assert exit 1, a written verdict, and no traceback.

3. Two descriptive Lane B fields need narrower definitions

The evaluator currently sets false_refusal = not state_ok on every proceed-permitted case. But state_ok can be false because of a wrong commitment amount or request ID, even when the participant actually committed and claimed SHIP. That is an incorrect commitment, not necessarily a refusal.

It also sets structured_grounds_present by checking whether a decision.json artifact exists. That does not establish whether the participant's preserved prose contains a structured policy ground.

Required: retain the existing Lane B VERIFIED/FAILED rule, but make the descriptive fields mean what their names claim. Classify false refusal from observable refusal or unnecessary-review behavior, separately from a wrong commitment. Define structured_grounds_present against an explicit, nonsemantic evidence-presence rule—or omit the field if no such rule is frozen. Do not grade the truth of free-form prose.

Add one Lane B negative in which the participant commits the wrong amount and claims SHIP. It must fail state_transition_correct without being labeled a false refusal.

4. Preserve actual ledger state when a model call aborts after an action

The runner's infrastructure-abort path writes a start-state hash as the recorded end state and emits zero commitments and reviews. But the participant may already have called commit_spend or request_human_review successfully before a later model request returns HTTP 500. The ledger is not rolled back.

That would leave an INFRA record describing a clean genesis state while its ledger and earlier trace events show actions occurred.

Required: keep the abort classified as INFRA, without an evaluated model outcome, but preserve and record the actual final simulated ledger state and its hash. Do not reset its recorded state merely to fit the old clean-abort shape.

Test a scripted accepted commitment followed by a synthetic model-lane abort. The abort must remain excluded from scoring while its prior action stays observable and the recorded end-state hash matches the ledger.

Admission and authorization status

| Boundary | Ruling |
| --- | --- |
| Frozen S1 v2 design | ACCEPTED / UNCHANGED |
| Runner and evaluator implementation phase | CLOSED |
| Delivered synthetic admission evidence | ACCEPTED AS RECORDED |
| Admission for live model execution | FIX — four targeted gaps above |
| Live S1 runs | HOLD — Adam's separate explicit GO remains required |

Preserve all 21 existing synthetic runs and their verdicts. Implement these as prospective evaluator/runner fixes, add targeted controls, rerun the existing admission battery, and publish a small versioned addendum showing whether any previous synthetic verdict changed. Do not silently replace the original admission receipt.

Final directive: 3bfc6a8 accepted as the completed implementation and initial synthetic-admission record. Close the four targeted gaps before declaring the machinery live-admitted; do not make model calls or alter the frozen case and prompt fixtures.
