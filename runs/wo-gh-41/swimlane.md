# Swimlane

Routing: 5 reviewers (reduced panel, 1 routed out)

**Cost**: No measured steps (3 executed steps)

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 16960.422 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-41/runs/wo-gh-41/intake.output.md | null |
| spec-writer | executed | 78845.729 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-41/runs/wo-gh-41/spec-writer.output.md | null |
| test-writer | executed | 569417.002 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-41/runs/wo-gh-41/test-writer.output.md | null |
| builder | failed | 663818.073 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-41/runs/wo-gh-41/builder.packet.md | null |
| checks-gate | failed | 66167.095 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-41/runs/wo-gh-41/checks-gate.pre-review.output.md | null |
| loopback | loopback | 0.0 | - | null |
| reviewer-spec | skipped | 0.316 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-41/runs/wo-gh-41/reviewer-spec.packet.md | null |
| reviewer-security | skipped | 0.256 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-41/runs/wo-gh-41/reviewer-security.packet.md | null |
| reviewer-tests | skipped | 0.255 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-41/runs/wo-gh-41/reviewer-tests.packet.md | null |
| reviewer-architecture | skipped | 0.254 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-41/runs/wo-gh-41/reviewer-architecture.packet.md | null |
| reviewer-design | skipped | 8.236 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-41/runs/wo-gh-41/reviewer-design.packet.md | null |
| reviewer-ux | skipped | 0.838 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-41/runs/wo-gh-41/reviewer-ux.packet.md | null |
| approver | completed | 0.022 | /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-41/runs/wo-gh-41/report.json | null |
| triage-human | completed | 0.008 | - | null |
| deployer | budget_exceeded | 0 | - | null |

## Decision

- Approver: No reviews were produced in this run, so the verdict is no_reviews; standing project reviews are never counted. (Counted 0 reviews, expected 5.)
- Human gate: No approver verdict was produced by this pipeline and no risk hints matched (scanned: auth, payments, data-deletion, production-deploy, secrets, publishing), so no human is required.
