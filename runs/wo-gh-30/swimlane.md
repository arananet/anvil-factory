# Swimlane

Routing: 4 reviewers (reduced panel, 2 routed out)

**Cost**: No measured steps (8 executed steps)

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 3116.423 | runs/wo-gh-30/intake.output.md | null |
| spec-writer | executed | 17905.249 | runs/wo-gh-30/spec-writer.output.md | null |
| test-writer | executed | 75110.3 | runs/wo-gh-30/test-writer.output.md | null |
| builder | executed | 109579.856 | runs/wo-gh-30/builder.output.md | null |
| checks-gate | passed | 104420.969 | runs/wo-gh-30/checks-gate.pre-review.output.md | null |
| reviewer-spec | executed | 18820.732 | runs/wo-gh-30/reviewer-spec.output.md | null |
| reviewer-security | routed_out | 0.291 | runs/wo-gh-30/reviewer-security.packet.md | null |
| reviewer-tests | executed | 78495.577 | runs/wo-gh-30/reviewer-tests.output.md | null |
| reviewer-architecture | routed_out | 0.319 | runs/wo-gh-30/reviewer-architecture.packet.md | null |
| reviewer-design | failed | 31147.178 | runs/wo-gh-30/reviewer-design.packet.md | null |
| reviewer-ux | executed | 25218.997 | runs/wo-gh-30/reviewer-ux.output.md | null |
| approver | completed | 0.053 | runs/wo-gh-30/report.json | null |
| approver | loopback | 0.0 | - | null |
| triage-human | completed | 0.009 | - | null |
| deployer | packet_ready | 0.284 | runs/wo-gh-30/deployer.packet.md | null |
| observer | executed | 14673.053 | runs/wo-gh-30/observer.output.md | null |

## Decision

- Approver: Reviewer reviewer-ux returned fail. (Counted 3 reviews, expected 4.)
- Human gate: Verdict is rejected, not approved, so a human is required.
