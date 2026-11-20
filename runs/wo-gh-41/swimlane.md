# Swimlane

Routing: 5 reviewers (reduced panel, 1 routed out)

**Cost**: No measured steps (10 executed steps)

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 19409.252 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-41/runs/wo-gh-41/intake.output.md | null |
| spec-writer | executed | 40696.267 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-41/runs/wo-gh-41/spec-writer.output.md | null |
| test-writer | executed | 280895.917 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-41/runs/wo-gh-41/test-writer.output.md | null |
| builder | executed | 205770.139 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-41/runs/wo-gh-41/builder.output.md | null |
| checks-gate | passed | 73814.805 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-41/runs/wo-gh-41/checks-gate.pre-review.output.md | null |
| reviewer-spec | executed | 124180.042 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-41/runs/wo-gh-41/reviewer-spec.output.md | null |
| reviewer-security | executed | 36394.575 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-41/runs/wo-gh-41/reviewer-security.output.md | null |
| reviewer-tests | executed | 187976.86 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-41/runs/wo-gh-41/reviewer-tests.output.md | null |
| reviewer-architecture | executed | 52877.965 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-41/runs/wo-gh-41/reviewer-architecture.output.md | null |
| reviewer-design | executed | 18754.22 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-41/runs/wo-gh-41/reviewer-design.output.md | null |
| reviewer-ux | routed_out | 1.195 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-41/runs/wo-gh-41/reviewer-ux.packet.md | null |
| approver | completed | 0.059 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-41/runs/wo-gh-41/report.json | null |
| triage-human | completed | 0.013 | - | null |
| deployer | packet_ready | 0.561 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-41/runs/wo-gh-41/deployer.packet.md | null |
| observer | executed | 48916.921 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-41/runs/wo-gh-41/observer.output.md | null |

## Decision

- Approver: All counted reviews passed. (Expected 5 reviews after routing.)
- Human gate: Verdict approved and no risk hints matched (scanned: auth, payments, data-deletion, production-deploy, secrets, publishing), so no human is required.
