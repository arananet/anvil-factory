# Swimlane

Routing: 5 reviewers (reduced panel, 1 routed out)

**Cost**: No measured steps (4 executed steps)

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 38752.224 | runs/wo-gh-29/intake.output.md | null |
| spec-writer | executed | 25821.21 | runs/wo-gh-29/spec-writer.output.md | null |
| test-writer | executed | 360272.001 | runs/wo-gh-29/test-writer.output.md | null |
| builder | executed | 407793.019 | runs/wo-gh-29/builder.output.md | null |
| checks-gate | failed | 48667.945 | runs/wo-gh-29/checks-gate.pre-review.output.md | null |
| loopback | loopback | 0.0 | - | null |
| reviewer-spec | skipped | 0.111 | runs/wo-gh-29/reviewer-spec.packet.md | null |
| reviewer-security | skipped | 0.066 | runs/wo-gh-29/reviewer-security.packet.md | null |
| reviewer-tests | skipped | 0.061 | runs/wo-gh-29/reviewer-tests.packet.md | null |
| reviewer-architecture | skipped | 0.052 | runs/wo-gh-29/reviewer-architecture.packet.md | null |
| reviewer-design | skipped | 27.903 | runs/wo-gh-29/reviewer-design.packet.md | null |
| reviewer-ux | skipped | 0.511 | runs/wo-gh-29/reviewer-ux.packet.md | null |
| approver | completed | 0.014 | runs/wo-gh-29/report.json | null |
| triage-human | completed | 0.005 | - | null |
| deployer | packet_ready | 0.06 | runs/wo-gh-29/deployer.packet.md | null |
| observer | failed | 23.665 | runs/wo-gh-29/observer.packet.md | null |

## Decision

- Approver: No reviews were produced in this run, so the verdict is no_reviews; standing project reviews are never counted. (Counted 0 reviews, expected 5.)
- Human gate: Verdict is no_reviews, not approved, so a human is required.
