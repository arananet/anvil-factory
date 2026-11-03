# Swimlane

Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 28748.249 | runs/wo-gh-8/intake.output.md | null |
| spec-writer | executed | 251223.487 | runs/wo-gh-8/spec-writer.output.md | null |
| test-writer | executed | 225623.143 | runs/wo-gh-8/test-writer.output.md | null |
| builder | failed | 297015.699 | runs/wo-gh-8/builder.packet.md | null |
| checks-gate | passed | 12783.567 | runs/wo-gh-8/checks-gate.pre-review.output.md | null |
| reviewer-spec | failed | 17876.023 | runs/wo-gh-8/reviewer-spec.packet.md | null |
| reviewer-security | failed | 20558.076 | runs/wo-gh-8/reviewer-security.packet.md | null |
| reviewer-tests | failed | 9744.013 | runs/wo-gh-8/reviewer-tests.packet.md | null |
| reviewer-architecture | failed | 9490.319 | runs/wo-gh-8/reviewer-architecture.packet.md | null |
| reviewer-design | failed | 19495.592 | runs/wo-gh-8/reviewer-design.packet.md | null |
| approver | completed | 0.024 | runs/wo-gh-8/report.json | null |
| triage-human | completed | 0.006 | - | null |
| deployer | packet_ready | 0.091 | runs/wo-gh-8/deployer.packet.md | null |
| observer | failed | 9582.207 | runs/wo-gh-8/observer.packet.md | null |

## Decision

- Approver: No reviews were produced in this run, so the verdict is no_reviews; standing project reviews are never counted. (Counted 0 reviews, expected 5.)
- Human gate: Verdict is no_reviews, not approved, so a human is required.
