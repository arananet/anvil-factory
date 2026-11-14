# Swimlane

Routing: 5 reviewers (reduced panel, 1 routed out)

**Cost**: No measured steps (3 executed steps)

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 4203.322 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-39/runs/wo-gh-39/intake.output.md | null |
| spec-writer | executed | 34884.972 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-39/runs/wo-gh-39/spec-writer.output.md | null |
| test-writer | executed | 284343.037 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-39/runs/wo-gh-39/test-writer.output.md | null |
| builder | budget_exceeded | 0 | - | null |

## Decision

- Approver: The pipeline has no approver step, so no reviews were aggregated into a verdict.
- Human gate: No approver verdict was produced by this pipeline and no risk hints matched (scanned: auth, payments, data-deletion, production-deploy, secrets, publishing), so no human is required.
