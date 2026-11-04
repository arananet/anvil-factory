# Swimlane

Routing: 5 reviewers (reduced panel, 1 routed out)

**Cost**: No measured steps (5 executed steps)

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 40882.713 | runs/wo-gh-14/intake.output.md | null |
| spec-writer | executed | 39325.521 | runs/wo-gh-14/spec-writer.output.md | null |
| test-writer | executed | 197335.288 | runs/wo-gh-14/test-writer.output.md | null |
| builder | executed | 528968.34 | runs/wo-gh-14/builder.output.md | null |
| checks-gate | failed | 34210.305 | runs/wo-gh-14/checks-gate.pre-review.output.md | null |
| loopback | loopback | 0.0 | - | null |
| reviewer-spec | skipped | 0.243 | runs/wo-gh-14/reviewer-spec.packet.md | null |
| reviewer-security | skipped | 0.204 | runs/wo-gh-14/reviewer-security.packet.md | null |
| reviewer-tests | skipped | 0.186 | runs/wo-gh-14/reviewer-tests.packet.md | null |
| reviewer-architecture | skipped | 0.205 | runs/wo-gh-14/reviewer-architecture.packet.md | null |
| reviewer-design | skipped | 1.63 | runs/wo-gh-14/reviewer-design.packet.md | null |
| reviewer-ux | skipped | 1.392 | runs/wo-gh-14/reviewer-ux.packet.md | null |
| approver | completed | 0.034 | runs/wo-gh-14/report.json | null |
| triage-human | completed | 0.01 | - | null |
| deployer | packet_ready | 0.18 | runs/wo-gh-14/deployer.packet.md | null |
| observer | executed | 61787.7 | runs/wo-gh-14/observer.output.md | null |

## Decision

- Approver: No reviews were produced in this run, so the verdict is no_reviews; standing project reviews are never counted. (Counted 0 reviews, expected 5.)
- Human gate: Verdict is no_reviews, not approved, so a human is required.
