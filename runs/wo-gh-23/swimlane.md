# Swimlane

Routing: 5 reviewers (reduced panel, 1 routed out)

**Cost**: No measured steps (5 executed steps)

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 42197.382 | runs/wo-gh-23/intake.output.md | null |
| spec-writer | executed | 160353.279 | runs/wo-gh-23/spec-writer.output.md | null |
| test-writer | executed | 327785.066 | runs/wo-gh-23/test-writer.output.md | null |
| builder | executed | 321711.977 | runs/wo-gh-23/builder.output.md | null |
| checks-gate | failed | 122308.875 | runs/wo-gh-23/checks-gate.pre-review.output.md | null |
| loopback | loopback | 0.0 | - | null |
| reviewer-spec | skipped | 0.39 | runs/wo-gh-23/reviewer-spec.packet.md | null |
| reviewer-security | skipped | 0.351 | runs/wo-gh-23/reviewer-security.packet.md | null |
| reviewer-tests | skipped | 0.358 | runs/wo-gh-23/reviewer-tests.packet.md | null |
| reviewer-architecture | skipped | 0.327 | runs/wo-gh-23/reviewer-architecture.packet.md | null |
| reviewer-design | skipped | 22.309 | runs/wo-gh-23/reviewer-design.packet.md | null |
| reviewer-ux | skipped | 2.592 | runs/wo-gh-23/reviewer-ux.packet.md | null |
| approver | completed | 0.045 | runs/wo-gh-23/report.json | null |
| triage-human | completed | 0.009 | - | null |
| deployer | packet_ready | 0.34 | runs/wo-gh-23/deployer.packet.md | null |
| observer | executed | 74742.166 | runs/wo-gh-23/observer.output.md | null |

## Decision

- Approver: No reviews were produced in this run, so the verdict is no_reviews; standing project reviews are never counted. (Counted 0 reviews, expected 5.)
- Human gate: Verdict is no_reviews, not approved, so a human is required.
