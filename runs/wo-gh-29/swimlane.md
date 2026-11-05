# Swimlane

Routing: 5 reviewers (reduced panel, 1 routed out)

**Cost**: No measured steps (5 executed steps)

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 5179.985 | runs/wo-gh-29/intake.output.md | null |
| spec-writer | executed | 90722.609 | runs/wo-gh-29/spec-writer.output.md | null |
| test-writer | executed | 84982.92 | runs/wo-gh-29/test-writer.output.md | null |
| builder | executed | 68885.23 | runs/wo-gh-29/builder.output.md | null |
| checks-gate | passed | 34087.585 | runs/wo-gh-29/checks-gate.pre-review.output.md | null |
| reviewer-spec | failed | 27.442 | runs/wo-gh-29/reviewer-spec.packet.md | null |
| reviewer-security | failed | 26.728 | runs/wo-gh-29/reviewer-security.packet.md | null |
| reviewer-tests | failed | 26.029 | runs/wo-gh-29/reviewer-tests.packet.md | null |
| reviewer-architecture | failed | 26.131 | runs/wo-gh-29/reviewer-architecture.packet.md | null |
| reviewer-design | failed | 82.006 | runs/wo-gh-29/reviewer-design.packet.md | null |
| reviewer-ux | routed_out | 0.974 | runs/wo-gh-29/reviewer-ux.packet.md | null |
| approver | completed | 0.021 | runs/wo-gh-29/report.json | null |
| triage-human | completed | 0.007 | - | null |
| deployer | packet_ready | 0.218 | runs/wo-gh-29/deployer.packet.md | null |
| observer | executed | 22604.164 | runs/wo-gh-29/observer.output.md | null |

## Decision

- Approver: No reviews were produced in this run, so the verdict is no_reviews; standing project reviews are never counted. (Counted 0 reviews, expected 5.)
- Human gate: Verdict is no_reviews, not approved, so a human is required.
