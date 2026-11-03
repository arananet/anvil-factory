# Swimlane

Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 630987.241 | runs/wo-gh-7/intake.output.md | null |
| spec-writer | executed | 225020.782 | runs/wo-gh-7/spec-writer.output.md | null |
| test-writer | executed | 169436.273 | runs/wo-gh-7/test-writer.output.md | null |
| builder | executed | 125258.596 | runs/wo-gh-7/builder.output.md | null |
| checks-gate | failed | 12384.807 | runs/wo-gh-7/checks-gate.pre-review.output.md | null |
| loopback | loopback | 0.0 | - | null |
| reviewer-spec | skipped | 0.239 | runs/wo-gh-7/reviewer-spec.packet.md | null |
| reviewer-security | skipped | 0.227 | runs/wo-gh-7/reviewer-security.packet.md | null |
| reviewer-tests | skipped | 0.186 | runs/wo-gh-7/reviewer-tests.packet.md | null |
| reviewer-architecture | skipped | 0.19 | runs/wo-gh-7/reviewer-architecture.packet.md | null |
| reviewer-design | skipped | 0.405 | runs/wo-gh-7/reviewer-design.packet.md | null |
| approver | completed | 0.028 | runs/wo-gh-7/report.json | null |
| triage-human | completed | 0.007 | - | null |
| deployer | packet_ready | 0.214 | runs/wo-gh-7/deployer.packet.md | null |
| observer | executed | 119693.765 | runs/wo-gh-7/observer.output.md | null |

## Decision

- Approver: No reviews were produced in this run, so the verdict is no_reviews; standing project reviews are never counted. (Counted 0 reviews, expected 5.)
- Human gate: Verdict is no_reviews, not approved, so a human is required.
