# Swimlane

Routing: 5 reviewers (full panel)

Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 49236.514 | runs/wo-gh-8/intake.output.md | null |
| spec-writer | executed | 96377.201 | runs/wo-gh-8/spec-writer.output.md | null |
| test-writer | executed | 245625.753 | runs/wo-gh-8/test-writer.output.md | null |
| builder | executed | 299876.522 | runs/wo-gh-8/builder.output.md | null |
| checks-gate | failed | 16269.087 | runs/wo-gh-8/checks-gate.pre-review.output.md | null |
| loopback | loopback | 0.0 | - | null |
| reviewer-spec | skipped | 0.212 | runs/wo-gh-8/reviewer-spec.packet.md | null |
| reviewer-security | skipped | 0.189 | runs/wo-gh-8/reviewer-security.packet.md | null |
| reviewer-tests | skipped | 0.23 | runs/wo-gh-8/reviewer-tests.packet.md | null |
| reviewer-architecture | skipped | 0.24 | runs/wo-gh-8/reviewer-architecture.packet.md | null |
| reviewer-design | skipped | 0.466 | runs/wo-gh-8/reviewer-design.packet.md | null |
| approver | completed | 0.029 | runs/wo-gh-8/report.json | null |
| triage-human | completed | 0.007 | - | null |
| deployer | packet_ready | 0.21 | runs/wo-gh-8/deployer.packet.md | null |
| observer | executed | 58587.656 | runs/wo-gh-8/observer.output.md | null |

## Decision

- Approver: No reviews were produced in this run, so the verdict is no_reviews; standing project reviews are never counted. (Counted 0 reviews, expected 5.)
- Human gate: Verdict is no_reviews, not approved, so a human is required.
