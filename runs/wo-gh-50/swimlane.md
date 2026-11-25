# Swimlane

Routing: 5 reviewers (reduced panel, 1 routed out)

**Exit status**: runtime_refused (the model runtime refused station test-writer: insufficient billing balance (HTTP 402); no later station was called)

**Cost**: No measured steps (2 executed steps)

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 11628.054 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-50/runs/wo-gh-50/intake.output.md | null |
| spec-writer | executed | 158497.852 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-50/runs/wo-gh-50/spec-writer.output.md | null |
| test-writer | failed | 475811.269 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-50/runs/wo-gh-50/test-writer.packet.md | null |
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

- Approver: The run ended (runtime_refused) before the approver step, so no reviews were aggregated into a verdict.
- Human gate: No approver verdict was produced by this pipeline and no risk hints matched (scanned: auth, payments, data-deletion, production-deploy, secrets, publishing), so no human is required.
