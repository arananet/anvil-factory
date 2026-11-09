# Swimlane

Routing: 5 reviewers (reduced panel, 1 routed out)

**Cost**: No measured steps (5 executed steps)

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 4650.477 | runs/wo-gh-36/intake.output.md | null |
| spec-writer | executed | 12653.924 | runs/wo-gh-36/spec-writer.output.md | null |
| test-writer | executed | 85955.064 | runs/wo-gh-36/test-writer.output.md | null |
| builder | executed | 534317.15 | runs/wo-gh-36/builder.output.md | null |
| checks-gate | failed | 125870.156 | runs/wo-gh-36/checks-gate.pre-review.output.md | null |
| loopback | loopback | 0.0 | - | null |
| reviewer-spec | skipped | 0.173 | runs/wo-gh-36/reviewer-spec.packet.md | null |
| reviewer-security | skipped | 0.132 | runs/wo-gh-36/reviewer-security.packet.md | null |
| reviewer-tests | skipped | 0.138 | runs/wo-gh-36/reviewer-tests.packet.md | null |
| reviewer-architecture | skipped | 0.106 | runs/wo-gh-36/reviewer-architecture.packet.md | null |
| reviewer-design | skipped | 11.574 | runs/wo-gh-36/reviewer-design.packet.md | null |
| reviewer-ux | skipped | 1.155 | runs/wo-gh-36/reviewer-ux.packet.md | null |
| approver | completed | 0.035 | runs/wo-gh-36/report.json | null |
| triage-human | completed | 0.008 | - | null |
| deployer | packet_ready | 0.109 | runs/wo-gh-36/deployer.packet.md | null |
| observer | executed | 18055.181 | runs/wo-gh-36/observer.output.md | null |

## Decision

- Approver: No reviews were produced in this run, so the verdict is no_reviews; standing project reviews are never counted. (Counted 0 reviews, expected 5.)
- Human gate: Verdict is no_reviews, not approved, so a human is required.
