# Swimlane

Routing: 5 reviewers (reduced panel, 1 routed out)

**Cost**: No measured steps (9 executed steps)

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 6582.006 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-43/runs/wo-gh-43/intake.output.md | null |
| spec-writer | executed | 28159.452 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-43/runs/wo-gh-43/spec-writer.output.md | null |
| test-writer | executed | 226413.734 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-43/runs/wo-gh-43/test-writer.output.md | null |
| builder | failed | 65298.157 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-43/runs/wo-gh-43/builder.packet.md | null |
| checks-gate | failed | 84839.508 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-43/runs/wo-gh-43/checks-gate.pre-review.output.md | null |
| loopback | loopback | 0.0 | - | null |
| builder | executed | 432778.855 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-43/runs/wo-gh-43/builder.output.md | null |
| checks-gate | passed | 75047.487 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-43/runs/wo-gh-43/checks-gate.pre-review.output.md | null |
| reviewer-spec | executed | 105390.801 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-43/runs/wo-gh-43/reviewer-spec.output.md | null |
| reviewer-security | executed | 13713.861 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-43/runs/wo-gh-43/reviewer-security.output.md | null |
| reviewer-tests | executed | 120991.048 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-43/runs/wo-gh-43/reviewer-tests.output.md | null |
| reviewer-architecture | executed | 183277.471 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-43/runs/wo-gh-43/reviewer-architecture.output.md | null |
| reviewer-design | executed | 29469.348 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-43/runs/wo-gh-43/reviewer-design.output.md | null |
| reviewer-ux | routed_out | 1.842 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-43/runs/wo-gh-43/reviewer-ux.packet.md | null |
| approver | completed | 0.054 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-43/runs/wo-gh-43/report.json | null |
| triage-human | completed | 0.018 | - | null |
| deployer | packet_ready | 0.895 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-43/runs/wo-gh-43/deployer.packet.md | null |
| observer | failed | 175450.431 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-43/runs/wo-gh-43/observer.packet.md | null |

## Decision

- Approver: All counted reviews passed. (Expected 5 reviews after routing.)
- Human gate: Verdict approved and no risk hints matched (scanned: auth, payments, data-deletion, production-deploy, secrets, publishing), so no human is required.
