# Swimlane

Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | completed | 0.021 | runs/wo-gh-6/report.json | null |
| spec-writer | executed | 55185.595 | runs/wo-gh-6/spec-writer.output.md | null |
| test-writer | executed | 186325.293 | runs/wo-gh-6/test-writer.output.md | null |
| builder | executed | 379357.092 | runs/wo-gh-6/builder.output.md | null |
| checks-gate | failed | 7131.733 | runs/wo-gh-6/checks-gate.pre-review.output.md | null |
| loopback | loopback | 0.0 | - | null |
| reviewer-spec | skipped | 0.233 | runs/wo-gh-6/reviewer-spec.packet.md | null |
| reviewer-security | skipped | 0.18 | runs/wo-gh-6/reviewer-security.packet.md | null |
| reviewer-tests | skipped | 0.196 | runs/wo-gh-6/reviewer-tests.packet.md | null |
| reviewer-architecture | skipped | 0.21 | runs/wo-gh-6/reviewer-architecture.packet.md | null |
| reviewer-design | skipped | 0.384 | runs/wo-gh-6/reviewer-design.packet.md | null |
| approver | completed | 0.029 | runs/wo-gh-6/report.json | null |
| triage-human | completed | 0.007 | - | null |
| deployer | packet_ready | 0.182 | runs/wo-gh-6/deployer.packet.md | null |
| observer | executed | 33616.399 | runs/wo-gh-6/observer.output.md | null |

## Decision

- Approver: No reviews were produced in this run, so the verdict is no_reviews; standing project reviews are never counted. (Counted 0 reviews, expected 5.)
- Human gate: Verdict is no_reviews, not approved, so a human is required.
