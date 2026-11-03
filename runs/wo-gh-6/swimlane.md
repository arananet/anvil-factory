# Swimlane

Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | completed | 0.028 | runs/wo-gh-6/report.json | null |
| spec-writer | executed | 175354.936 | runs/wo-gh-6/spec-writer.output.md | null |
| test-writer | executed | 126871.694 | runs/wo-gh-6/test-writer.output.md | null |
| builder | executed | 342439.127 | runs/wo-gh-6/builder.output.md | null |
| checks-gate | failed | 6828.054 | runs/wo-gh-6/checks-gate.pre-review.output.md | null |
| loopback | loopback | 0.0 | - | null |
| reviewer-spec | skipped | 0.278 | runs/wo-gh-6/reviewer-spec.packet.md | null |
| reviewer-security | skipped | 0.224 | runs/wo-gh-6/reviewer-security.packet.md | null |
| reviewer-tests | skipped | 0.659 | runs/wo-gh-6/reviewer-tests.packet.md | null |
| reviewer-architecture | skipped | 0.226 | runs/wo-gh-6/reviewer-architecture.packet.md | null |
| reviewer-design | skipped | 0.419 | runs/wo-gh-6/reviewer-design.packet.md | null |
| approver | completed | 0.03 | runs/wo-gh-6/report.json | null |
| triage-human | completed | 0.008 | - | null |
| deployer | packet_ready | 0.294 | runs/wo-gh-6/deployer.packet.md | null |
| observer | executed | 51078.376 | runs/wo-gh-6/observer.output.md | null |

## Decision

- Approver: No reviews were produced in this run, so the verdict is no_reviews; standing project reviews are never counted. (Counted 0 reviews, expected 5.)
- Human gate: Verdict is no_reviews, not approved, so a human is required.
