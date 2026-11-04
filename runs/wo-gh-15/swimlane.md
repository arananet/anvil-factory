# Swimlane

Routing: 5 reviewers (reduced panel, 1 routed out)

**Cost**: No measured steps (10 executed steps)

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 29523.079 | runs/wo-gh-15/intake.output.md | null |
| spec-writer | executed | 71226.298 | runs/wo-gh-15/spec-writer.output.md | null |
| test-writer | executed | 99514.992 | runs/wo-gh-15/test-writer.output.md | null |
| builder | executed | 268591.531 | runs/wo-gh-15/builder.output.md | null |
| checks-gate | passed | 28680.477 | runs/wo-gh-15/checks-gate.pre-review.output.md | null |
| reviewer-spec | executed | 197897.211 | runs/wo-gh-15/reviewer-spec.output.md | null |
| reviewer-security | executed | 214865.83 | runs/wo-gh-15/reviewer-security.output.md | null |
| reviewer-tests | executed | 141667.25 | runs/wo-gh-15/reviewer-tests.output.md | null |
| reviewer-architecture | executed | 199790.772 | runs/wo-gh-15/reviewer-architecture.output.md | null |
| reviewer-design | executed | 289715.91 | runs/wo-gh-15/reviewer-design.output.md | null |
| reviewer-ux | routed_out | 2.548 | runs/wo-gh-15/reviewer-ux.packet.md | null |
| approver | completed | 0.041 | runs/wo-gh-15/report.json | null |
| approver | loopback | 0.0 | - | null |
| triage-human | completed | 0.007 | - | null |
| deployer | packet_ready | 0.218 | runs/wo-gh-15/deployer.packet.md | null |
| observer | executed | 70218.645 | runs/wo-gh-15/observer.output.md | null |

## Decision

- Approver: Reviewer reviewer-design requested changes. (Expected 5 reviews after routing.)
- Human gate: Verdict is changes_requested, not approved, so a human is required.
