# Swimlane

Routing: 2 reviewers (reduced panel, 4 routed out)

**Cost**: No measured steps (5 executed steps)

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 55840.216 | runs/wo-gh-23/intake.output.md | null |
| spec-writer | executed | 119770.581 | runs/wo-gh-23/spec-writer.output.md | null |
| test-writer | executed | 116644.888 | runs/wo-gh-23/test-writer.output.md | null |
| builder | executed | 470980.437 | runs/wo-gh-23/builder.output.md | null |
| checks-gate | failed | 50260.426 | runs/wo-gh-23/checks-gate.pre-review.output.md | null |
| loopback | loopback | 0.0 | - | null |
| reviewer-spec | skipped | 0.191 | runs/wo-gh-23/reviewer-spec.packet.md | null |
| reviewer-security | skipped | 0.131 | runs/wo-gh-23/reviewer-security.packet.md | null |
| reviewer-tests | skipped | 0.121 | runs/wo-gh-23/reviewer-tests.packet.md | null |
| reviewer-architecture | skipped | 0.122 | runs/wo-gh-23/reviewer-architecture.packet.md | null |
| reviewer-design | skipped | 5.657 | runs/wo-gh-23/reviewer-design.packet.md | null |
| reviewer-ux | skipped | 0.824 | runs/wo-gh-23/reviewer-ux.packet.md | null |
| approver | completed | 0.03 | runs/wo-gh-23/report.json | null |
| triage-human | completed | 0.009 | - | null |
| deployer | packet_ready | 0.133 | runs/wo-gh-23/deployer.packet.md | null |
| observer | executed | 40640.411 | runs/wo-gh-23/observer.output.md | null |

## Decision

- Approver: No reviews were produced in this run, so the verdict is no_reviews; standing project reviews are never counted. (Counted 0 reviews, expected 2.)
- Human gate: Verdict is no_reviews, not approved, so a human is required.
