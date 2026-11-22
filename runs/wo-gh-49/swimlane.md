# Swimlane

**Exit status**: budget_exceeded (station intake stopped by its in-flight ceiling at efficiency.station_budgets intake 200000: measured 212779 tokens; the undone work is not resumed in this dispatch)

**Cost**: No measured steps (0 executed steps)

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | budget_exceeded | 39382.219 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-49/runs/wo-gh-49/intake.packet.md | null |
| spec-writer | not_run | 0 | - | null |
| test-writer | not_run | 0 | - | null |
| builder | not_run | 0 | - | null |
| checks-gate | not_run | 0 | - | null |
| reviewer-spec | not_run | 0 | - | null |
| reviewer-security | not_run | 0 | - | null |
| reviewer-tests | not_run | 0 | - | null |
| reviewer-architecture | not_run | 0 | - | null |
| reviewer-design | not_run | 0 | - | null |
| reviewer-ux | not_run | 0 | - | null |
| approver | not_run | 0 | - | null |
| triage-human | not_run | 0 | - | null |
| deployer | not_run | 0 | - | null |
| observer | not_run | 0 | - | null |

## Decision

- Approver: The run ended (budget_exceeded) before the approver step, so no reviews were aggregated into a verdict.
- Human gate: No approver verdict was produced by this pipeline and no risk hints matched (scanned: auth, payments, data-deletion, production-deploy, secrets, publishing), so no human is required.
