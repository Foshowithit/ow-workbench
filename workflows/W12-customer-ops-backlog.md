# W12 customer-ops backlog (MISSION)

Objective: clear a messy multi-customer backlog to verified resolutions without violating authority.

Mission-depth requirements (all five, else demoted to COMPOSITE):

1. Persistent queue state across sessions (tickets, SLAs, partial resolutions survive restart).
2. At least one mid-run interruption (shift handoff, tool outage, reprioritization event).
3. At least one dependency change after work started (policy update, supplier status change, refund-rule revision).
4. At least two parallel workers or tracks coordinated (triage + resolution, or two agents with handoff log).
5. Extended execution where unmanaged state degrades (SLA breaches accrue, duplicate replies, lost context).

Evidence: per-ticket resolution records + handoff log + evaluator checks. Video required (inspectable, never proof alone).
