# Swimlane

Routing: 5 reviewers (reduced panel, 1 routed out)

**Cost**: No measured steps (5 executed steps)

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 2268.358 | runs/wo-gh-29/intake.output.md | null |
| spec-writer | executed | 19447.902 | runs/wo-gh-29/spec-writer.output.md | null |
| test-writer | executed | 54921.638 | runs/wo-gh-29/test-writer.output.md | null |
| builder | executed | 426762.438 | runs/wo-gh-29/builder.output.md | null |
| checks-gate | failed | 55711.712 | runs/wo-gh-29/checks-gate.pre-review.output.md | null |
| loopback | loopback | 0.0 | - | null |
| reviewer-spec | skipped | 0.437 | runs/wo-gh-29/reviewer-spec.packet.md | null |
| reviewer-security | skipped | 0.376 | runs/wo-gh-29/reviewer-security.packet.md | null |
| reviewer-tests | skipped | 0.39 | runs/wo-gh-29/reviewer-tests.packet.md | null |
| reviewer-architecture | skipped | 0.353 | runs/wo-gh-29/reviewer-architecture.packet.md | null |
| reviewer-design | skipped | 17.939 | runs/wo-gh-29/reviewer-design.packet.md | null |
| reviewer-ux | skipped | 1.465 | runs/wo-gh-29/reviewer-ux.packet.md | null |
| approver | completed | 0.042 | runs/wo-gh-29/report.json | null |
| triage-human | completed | 0.017 | - | null |
| deployer | packet_ready | 0.577 | runs/wo-gh-29/deployer.packet.md | null |
| observer | executed | 19658.966 | runs/wo-gh-29/observer.output.md | null |

## Decision

- Approver: No reviews were produced in this run, so the verdict is no_reviews; standing project reviews are never counted. (Counted 0 reviews, expected 5.)
- Human gate: Verdict is no_reviews, not approved, so a human is required.
