# Swimlane

Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | completed | 0.022 | runs/wo-gh-6/report.json | null |
| spec-writer | executed | 83585.241 | runs/wo-gh-6/spec-writer.output.md | null |
| test-writer | executed | 272355.699 | runs/wo-gh-6/test-writer.output.md | null |
| builder | executed | 316963.479 | runs/wo-gh-6/builder.output.md | null |
| checks-gate | passed | 7092.772 | runs/wo-gh-6/checks-gate.pre-review.output.md | null |
| reviewer-spec | executed | 135796.01 | runs/wo-gh-6/reviewer-spec.output.md | null |
| reviewer-security | executed | 151181.667 | runs/wo-gh-6/reviewer-security.output.md | null |
| reviewer-tests | executed | 126071.896 | runs/wo-gh-6/reviewer-tests.output.md | null |
| reviewer-architecture | executed | 136832.049 | runs/wo-gh-6/reviewer-architecture.output.md | null |
| reviewer-design | executed | 50455.445 | runs/wo-gh-6/reviewer-design.output.md | null |
| approver | completed | 0.034 | runs/wo-gh-6/report.json | null |
| triage-human | completed | 0.008 | - | null |
| deployer | packet_ready | 0.21 | runs/wo-gh-6/deployer.packet.md | null |
| observer | executed | 38670.353 | runs/wo-gh-6/observer.output.md | null |

## Decision

- Approver: No reviews were produced in this run, so the verdict is no_reviews; standing project reviews are never counted. (Counted 0 reviews, expected 5.)
- Human gate: Verdict is no_reviews, not approved, so a human is required.
