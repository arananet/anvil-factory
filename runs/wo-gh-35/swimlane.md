# Swimlane

Routing: 4 reviewers (reduced panel, 2 routed out)

**Cost**: No measured steps (5 executed steps)

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 4797.738 | runs/wo-gh-35/intake.output.md | null |
| spec-writer | executed | 10905.657 | runs/wo-gh-35/spec-writer.output.md | null |
| test-writer | executed | 43288.67 | runs/wo-gh-35/test-writer.output.md | null |
| builder | executed | 245088.91 | runs/wo-gh-35/builder.output.md | null |
| checks-gate | failed | 105322.98 | runs/wo-gh-35/checks-gate.pre-review.output.md | null |
| loopback | loopback | 0.0 | - | null |
| reviewer-spec | skipped | 0.168 | runs/wo-gh-35/reviewer-spec.packet.md | null |
| reviewer-security | skipped | 0.124 | runs/wo-gh-35/reviewer-security.packet.md | null |
| reviewer-tests | skipped | 0.117 | runs/wo-gh-35/reviewer-tests.packet.md | null |
| reviewer-architecture | skipped | 0.125 | runs/wo-gh-35/reviewer-architecture.packet.md | null |
| reviewer-design | skipped | 6.094 | runs/wo-gh-35/reviewer-design.packet.md | null |
| reviewer-ux | skipped | 1.039 | runs/wo-gh-35/reviewer-ux.packet.md | null |
| approver | completed | 0.031 | runs/wo-gh-35/report.json | null |
| triage-human | completed | 0.008 | - | null |
| deployer | packet_ready | 0.126 | runs/wo-gh-35/deployer.packet.md | null |
| observer | executed | 26462.739 | runs/wo-gh-35/observer.output.md | null |

## Decision

- Approver: No reviews were produced in this run, so the verdict is no_reviews; standing project reviews are never counted. (Counted 0 reviews, expected 4.)
- Human gate: Verdict is no_reviews, not approved, so a human is required.
