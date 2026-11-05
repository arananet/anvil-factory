# Swimlane

Routing: 2 reviewers (reduced panel, 4 routed out)

**Cost**: No measured steps (5 executed steps)

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 4068.249 | runs/wo-gh-31/intake.output.md | null |
| spec-writer | executed | 8491.968 | runs/wo-gh-31/spec-writer.output.md | null |
| test-writer | executed | 142630.379 | runs/wo-gh-31/test-writer.output.md | null |
| builder | executed | 138092.773 | runs/wo-gh-31/builder.output.md | null |
| checks-gate | passed | 122112.75 | runs/wo-gh-31/checks-gate.pre-review.output.md | null |
| reviewer-spec | failed | 55.907 | runs/wo-gh-31/reviewer-spec.packet.md | null |
| reviewer-security | routed_out | 0.198 | runs/wo-gh-31/reviewer-security.packet.md | null |
| reviewer-tests | failed | 53.637 | runs/wo-gh-31/reviewer-tests.packet.md | null |
| reviewer-architecture | routed_out | 0.204 | runs/wo-gh-31/reviewer-architecture.packet.md | null |
| reviewer-design | routed_out | 9.244 | runs/wo-gh-31/reviewer-design.packet.md | null |
| reviewer-ux | routed_out | 1.63 | runs/wo-gh-31/reviewer-ux.packet.md | null |
| approver | completed | 0.046 | runs/wo-gh-31/report.json | null |
| triage-human | completed | 0.01 | - | null |
| deployer | packet_ready | 0.152 | runs/wo-gh-31/deployer.packet.md | null |
| observer | executed | 23988.796 | runs/wo-gh-31/observer.output.md | null |

## Decision

- Approver: No reviews were produced in this run, so the verdict is no_reviews; standing project reviews are never counted. (Counted 0 reviews, expected 2.)
- Human gate: Verdict is no_reviews, not approved, so a human is required.
