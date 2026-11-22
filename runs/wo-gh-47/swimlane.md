# Swimlane

Routing: 5 reviewers (reduced panel, 1 routed out)

**Exit status**: checks_stopped (pre-review checks gate failed with 2 of 2 loopbacks used: Gate failed: 1 checks, protected paths: pass; completeness precondition failed: checks gate verdict for attempt 3 is fail, not pass)

**Cost**: No measured steps (6 executed steps)

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 17022.938 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-47/runs/wo-gh-47/intake.output.md | null |
| spec-writer | executed | 251101.057 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-47/runs/wo-gh-47/spec-writer.output.md | null |
| test-writer | executed | 555419.47 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-47/runs/wo-gh-47/test-writer.output.md | null |
| builder | executed | 619190.362 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-47/runs/wo-gh-47/builder.output.md | null |
| checks-gate | failed | 105404.062 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-47/runs/wo-gh-47/checks-gate.pre-review.output.md | null |
| loopback | loopback | 0.0 | - | null |
| builder | executed | 589359.063 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-47/runs/wo-gh-47/builder.output.md | null |
| checks-gate | failed | 113452.282 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-47/runs/wo-gh-47/checks-gate.pre-review.output.md | null |
| loopback | loopback | 0.0 | - | null |
| builder | executed | 349891.309 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-47/runs/wo-gh-47/builder.output.md | null |
| checks-gate | failed | 101012.422 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-47/runs/wo-gh-47/checks-gate.pre-review.output.md | null |
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

- Approver: The run ended (checks_stopped) before the approver step, so no reviews were aggregated into a verdict.
- Human gate: No approver verdict was produced by this pipeline and no risk hints matched (scanned: auth, payments, data-deletion, production-deploy, secrets, publishing), so no human is required.
