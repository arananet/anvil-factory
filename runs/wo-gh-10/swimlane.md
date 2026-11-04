# Swimlane

Routing: 2 reviewers (reduced panel, 3 routed out)

**Cost**: No measured steps (5 executed steps)

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 28809.81 | runs/wo-gh-10/intake.output.md | null |
| spec-writer | executed | 116538.458 | runs/wo-gh-10/spec-writer.output.md | null |
| test-writer | executed | 392977.811 | runs/wo-gh-10/test-writer.output.md | null |
| builder | executed | 367040.704 | runs/wo-gh-10/builder.output.md | null |
| checks-gate | failed | 29700.563 | runs/wo-gh-10/checks-gate.pre-review.output.md | null |
| loopback | loopback | 0.0 | - | null |
| reviewer-spec | skipped | 0.234 | runs/wo-gh-10/reviewer-spec.packet.md | null |
| reviewer-security | skipped | 0.2 | runs/wo-gh-10/reviewer-security.packet.md | null |
| reviewer-tests | skipped | 0.258 | runs/wo-gh-10/reviewer-tests.packet.md | null |
| reviewer-architecture | skipped | 0.181 | runs/wo-gh-10/reviewer-architecture.packet.md | null |
| reviewer-design | skipped | 0.674 | runs/wo-gh-10/reviewer-design.packet.md | null |
| approver | completed | 0.032 | runs/wo-gh-10/report.json | null |
| triage-human | completed | 0.01 | - | null |
| deployer | packet_ready | 0.191 | runs/wo-gh-10/deployer.packet.md | null |
| observer | executed | 66496.542 | runs/wo-gh-10/observer.output.md | null |

## Decision

- Approver: No reviews were produced in this run, so the verdict is no_reviews; standing project reviews are never counted. (Counted 0 reviews, expected 2.)
- Human gate: Verdict is no_reviews, not approved, so a human is required.
