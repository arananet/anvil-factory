# Swimlane

Routing: 5 reviewers (full panel)

**Cost**: No measured steps (5 executed steps)

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 91219.454 | runs/wo-gh-12/intake.output.md | null |
| spec-writer | executed | 124671.471 | runs/wo-gh-12/spec-writer.output.md | null |
| test-writer | executed | 215339.052 | runs/wo-gh-12/test-writer.output.md | null |
| builder | executed | 734449.664 | runs/wo-gh-12/builder.output.md | null |
| checks-gate | failed | 28898.849 | runs/wo-gh-12/checks-gate.pre-review.output.md | null |
| loopback | loopback | 0.0 | - | null |
| reviewer-spec | skipped | 0.089 | runs/wo-gh-12/reviewer-spec.packet.md | null |
| reviewer-security | skipped | 0.055 | runs/wo-gh-12/reviewer-security.packet.md | null |
| reviewer-tests | skipped | 0.052 | runs/wo-gh-12/reviewer-tests.packet.md | null |
| reviewer-architecture | skipped | 0.058 | runs/wo-gh-12/reviewer-architecture.packet.md | null |
| reviewer-design | skipped | 1.025 | runs/wo-gh-12/reviewer-design.packet.md | null |
| approver | completed | 0.017 | runs/wo-gh-12/report.json | null |
| triage-human | completed | 0.006 | - | null |
| deployer | packet_ready | 0.055 | runs/wo-gh-12/deployer.packet.md | null |
| observer | executed | 106980.481 | runs/wo-gh-12/observer.output.md | null |

## Decision

- Approver: No reviews were produced in this run, so the verdict is no_reviews; standing project reviews are never counted. (Counted 0 reviews, expected 5.)
- Human gate: Verdict is no_reviews, not approved, so a human is required.
