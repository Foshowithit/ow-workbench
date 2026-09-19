# Capability Coverage Matrix

The matrix maps the 14 capability surface areas to the first 12 workflows. An `x`
means that the workflow deliberately exercises that capability; a blank means the
capability is not a primary requirement of that workflow. Coverage is a design
claim for Phase 0, not an execution result.

| Capability | W01 | W02 | W03 | W04 | W05 | W06 | W07 | W08 | W09 | W10 | W11 | W12 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Intent/objective understanding | x | x |  | x | x | x | x | x |  |  | x | x |
| Routing | x |  | x | x | x | x | x | x | x |  |  | x |
| Planning |  |  |  | x | x | x | x | x | x | x | x | x |
| Research |  | x | x |  | x |  | x | x | x |  | x | x |
| Transformation | x | x | x |  | x | x | x | x |  | x | x | x |
| Creation |  |  |  |  | x | x | x | x | x | x | x | x |
| Tool use | x | x | x | x | x | x | x | x | x | x | x | x |
| Coordination/delegation |  |  |  | x | x | x | x |  | x |  | x | x |
| State/context management | x | x | x | x | x | x | x | x | x | x | x | x |
| Adaptation | x | x | x |  | x | x | x | x | x | x | x | x |
| Failure recovery | x | x | x |  | x | x | x |  | x | x | x | x |
| Verification | x | x | x | x | x | x | x | x | x | x | x | x |
| Escalation/human authority |  |  |  | x | x |  | x |  |  |  |  | x |
| Finishing/delivery | x | x | x | x | x | x | x | x | x | x | x | x |

The authority boundary is explicitly exercised in W04 approval stop, W05
discontinued component and supplier recovery, W07 RFQ to quote package, and W12
customer-ops backlog. Failure recovery and verification each appear in at least
five workflows; every capability appears in at least two workflows.

No single workflow may become a leaderboard proxy. Results must be interpreted
across the declared workflow set, tiers, evidence requirements, and metrics
fingerprint rather than elevated from one task into a claim about general ability.

