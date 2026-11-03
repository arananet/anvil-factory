# Swimlane

Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | completed | 0.01 | runs/wo-gh-6/report.json | null |
| spec-writer | executed | 66240.686 | runs/wo-gh-6/spec-writer.output.md | null |
| test-writer | executed | 127757.17 | runs/wo-gh-6/test-writer.output.md | null |
| builder | executed | 167067.826 | runs/wo-gh-6/builder.output.md | null |
| checks-gate | passed | 5538.333 | runs/wo-gh-6/checks-gate.pre-review.output.md | null |
| reviewer-spec | executed | 89332.66 | runs/wo-gh-6/reviewer-spec.output.md | null |
| reviewer-security | executed | 135885.176 | runs/wo-gh-6/reviewer-security.output.md | null |
| reviewer-tests | executed | 85378.268 | runs/wo-gh-6/reviewer-tests.output.md | null |
| reviewer-architecture | executed | 142242.739 | runs/wo-gh-6/reviewer-architecture.output.md | null |
| reviewer-design | executed | 59958.646 | runs/wo-gh-6/reviewer-design.output.md | null |
| approver | completed | 0.023 | runs/wo-gh-6/report.json | null |
| triage-human | completed | 0.007 | - | null |
| deployer | packet_ready | 0.241 | runs/wo-gh-6/deployer.packet.md | null |
| observer | executed | 39917.111 | runs/wo-gh-6/observer.output.md | null |

## Decision

- Approver: No reviews were produced in this run, so the verdict is no_reviews; standing project reviews are never counted. (Counted 0 reviews, expected 5.)
- Human gate: Verdict is no_reviews, not approved, so a human is required.
