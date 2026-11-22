# Swimlane

Routing: 5 reviewers (reduced panel, 1 routed out)

**Exit status**: completed (run completed with verdict approved)

**Cost**: No measured steps (11 executed steps)

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 17625.274 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-47/runs/wo-gh-47/intake.output.md | null |
| spec-writer | executed | 24579.721 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-47/runs/wo-gh-47/spec-writer.output.md | null |
| test-writer | executed | 244216.3 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-47/runs/wo-gh-47/test-writer.output.md | null |
| builder | executed | 307067.176 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-47/runs/wo-gh-47/builder.output.md | null |
| checks-gate | passed | 109362.171 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-47/runs/wo-gh-47/checks-gate.pre-review.output.md | null |
| loopback | loopback | 0.0 | - | null |
| builder | executed | 406439.621 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-47/runs/wo-gh-47/builder.output.md | null |
| checks-gate | passed | 111798.672 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-47/runs/wo-gh-47/checks-gate.pre-review.output.md | null |
| reviewer-spec | executed | 70933.071 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-47/runs/wo-gh-47/reviewer-spec.output.md | null |
| reviewer-security | executed | 67417.186 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-47/runs/wo-gh-47/reviewer-security.output.md | null |
| reviewer-tests | executed | 173165.09 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-47/runs/wo-gh-47/reviewer-tests.output.md | null |
| reviewer-architecture | executed | 65232.014 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-47/runs/wo-gh-47/reviewer-architecture.output.md | null |
| reviewer-design | executed | 14474.901 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-47/runs/wo-gh-47/reviewer-design.output.md | null |
| reviewer-ux | routed_out | 1.591 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-47/runs/wo-gh-47/reviewer-ux.packet.md | null |
| approver | completed | 0.068 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-47/runs/wo-gh-47/report.json | null |
| triage-human | completed | 0.028 | - | null |
| deployer | packet_ready | 0.918 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-47/runs/wo-gh-47/deployer.packet.md | null |
| observer | executed | 292868.763 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-47/runs/wo-gh-47/observer.output.md | null |

## Decision

- Approver: All counted reviews passed. (Expected 5 reviews after routing.)
- Human gate: Verdict approved and no risk hints matched (scanned: auth, payments, data-deletion, production-deploy, secrets, publishing), so no human is required.
