# Swimlane

Routing: 5 reviewers (reduced panel, 1 routed out)

**Exit status**: budget_exceeded (station builder stopped by its in-flight ceiling at efficiency.station_budgets builder 5600000: measured 441011 tokens; the undone work is not resumed in this dispatch)

**Cost**: No measured steps (5 executed steps)

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 13075.407 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-49/runs/wo-gh-49/intake.output.md | null |
| spec-writer | executed | 93984.813 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-49/runs/wo-gh-49/spec-writer.output.md | null |
| test-writer | executed | 377079.715 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-49/runs/wo-gh-49/test-writer.output.md | null |
| builder | executed | 569191.09 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-49/runs/wo-gh-49/builder.output.md | null |
| checks-gate | failed | 92237.037 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-49/runs/wo-gh-49/checks-gate.pre-review.output.md | null |
| loopback | loopback | 0.0 | - | null |
| builder | executed | 267058.201 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-49/runs/wo-gh-49/builder.output.md | null |
| checks-gate | failed | 90772.025 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-49/runs/wo-gh-49/checks-gate.pre-review.output.md | null |
| loopback | loopback | 0.0 | - | null |
| builder | budget_exceeded | 674540.239 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-49/runs/wo-gh-49/builder.packet.md | null |
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
