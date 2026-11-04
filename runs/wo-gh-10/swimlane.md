# Swimlane

Routing: 5 reviewers (full panel)

**Cost**: No measured steps (5 executed steps)

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 21470.899 | runs/wo-gh-10/intake.output.md | null |
| spec-writer | executed | 124324.968 | runs/wo-gh-10/spec-writer.output.md | null |
| test-writer | executed | 236127.388 | runs/wo-gh-10/test-writer.output.md | null |
| builder | executed | 307698.169 | runs/wo-gh-10/builder.output.md | null |
| checks-gate | failed | 27830.469 | runs/wo-gh-10/checks-gate.pre-review.output.md | null |
| loopback | loopback | 0.0 | - | null |
| reviewer-spec | skipped | 0.353 | runs/wo-gh-10/reviewer-spec.packet.md | null |
| reviewer-security | skipped | 0.281 | runs/wo-gh-10/reviewer-security.packet.md | null |
| reviewer-tests | skipped | 0.362 | runs/wo-gh-10/reviewer-tests.packet.md | null |
| reviewer-architecture | skipped | 0.478 | runs/wo-gh-10/reviewer-architecture.packet.md | null |
| reviewer-design | skipped | 0.743 | runs/wo-gh-10/reviewer-design.packet.md | null |
| approver | completed | 0.026 | runs/wo-gh-10/report.json | null |
| triage-human | completed | 0.011 | - | null |
| deployer | packet_ready | 0.343 | runs/wo-gh-10/deployer.packet.md | null |
| observer | executed | 53214.593 | runs/wo-gh-10/observer.output.md | null |

## Decision

- Approver: No reviews were produced in this run, so the verdict is no_reviews; standing project reviews are never counted. (Counted 0 reviews, expected 5.)
- Human gate: Verdict is no_reviews, not approved, so a human is required.
