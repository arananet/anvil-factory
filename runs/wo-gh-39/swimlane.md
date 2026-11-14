# Swimlane

Routing: 5 reviewers (reduced panel, 1 routed out)

**Cost**: No measured steps (10 executed steps)

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 10362.356 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-39/runs/wo-gh-39/intake.output.md | null |
| spec-writer | executed | 16938.64 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-39/runs/wo-gh-39/spec-writer.output.md | null |
| test-writer | executed | 216854.422 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-39/runs/wo-gh-39/test-writer.output.md | null |
| builder | executed | 223357.001 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-39/runs/wo-gh-39/builder.output.md | null |
| checks-gate | passed | 79398.932 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-39/runs/wo-gh-39/checks-gate.pre-review.output.md | null |
| reviewer-spec | executed | 23575.687 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-39/runs/wo-gh-39/reviewer-spec.output.md | null |
| reviewer-security | executed | 13085.15 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-39/runs/wo-gh-39/reviewer-security.output.md | null |
| reviewer-tests | executed | 179102.29 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-39/runs/wo-gh-39/reviewer-tests.output.md | null |
| reviewer-architecture | executed | 15403.652 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-39/runs/wo-gh-39/reviewer-architecture.output.md | null |
| reviewer-design | executed | 27194.759 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-39/runs/wo-gh-39/reviewer-design.output.md | null |
| reviewer-ux | routed_out | 1.509 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-39/runs/wo-gh-39/reviewer-ux.packet.md | null |
| approver | completed | 0.05 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-39/runs/wo-gh-39/report.json | null |
| triage-human | completed | 0.014 | - | null |
| deployer | packet_ready | 0.712 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-39/runs/wo-gh-39/deployer.packet.md | null |
| observer | executed | 12031.241 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-39/runs/wo-gh-39/observer.output.md | null |

## Decision

- Approver: All counted reviews passed. (Expected 5 reviews after routing.)
- Human gate: Verdict approved and no risk hints matched (scanned: auth, payments, data-deletion, production-deploy, secrets, publishing), so no human is required.
