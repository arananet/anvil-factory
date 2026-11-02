# Swimlane

Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | completed | 0.019 | runs/wo-gh-16/report.json | null |
| spec-writer | executed | 75864.217 | runs/wo-gh-16/spec-writer.output.md | null |
| test-writer | executed | 155787.284 | runs/wo-gh-16/test-writer.output.md | null |
| builder | failed | 115690.306 | runs/wo-gh-16/builder.packet.md | null |
| reviewer-spec | failed | 90354.402 | runs/wo-gh-16/reviewer-spec.packet.md | null |
| reviewer-security | failed | 10225.338 | runs/wo-gh-16/reviewer-security.packet.md | null |
| reviewer-tests | failed | 629.334 | runs/wo-gh-16/reviewer-tests.packet.md | null |
| reviewer-architecture | failed | 49889.005 | runs/wo-gh-16/reviewer-architecture.packet.md | null |
| reviewer-design | failed | 27995.673 | runs/wo-gh-16/reviewer-design.packet.md | null |
| approver | completed | 0.034 | runs/wo-gh-16/report.json | null |
| triage-human | completed | 0.007 | - | null |
| deployer | packet_ready | 0.19 | runs/wo-gh-16/deployer.packet.md | null |
| observer | failed | 626.402 | runs/wo-gh-16/observer.packet.md | null |

## Decision

- Approver: No reviews were produced in this run, so the verdict is no_reviews; standing project reviews are never counted. (Counted 0 reviews, expected 5.)
- Human gate: Verdict is no_reviews, not approved, so a human is required.
