# Swimlane

Routing: 4 reviewers (reduced panel, 2 routed out)

**Cost**: No measured steps (5 executed steps)

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 59822.586 | runs/wo-gh-12/intake.output.md | null |
| spec-writer | executed | 98398.929 | runs/wo-gh-12/spec-writer.output.md | null |
| test-writer | executed | 369970.547 | runs/wo-gh-12/test-writer.output.md | null |
| builder | executed | 423072.62 | runs/wo-gh-12/builder.output.md | null |
| checks-gate | failed | 30782.998 | runs/wo-gh-12/checks-gate.pre-review.output.md | null |
| loopback | loopback | 0.0 | - | null |
| reviewer-spec | skipped | 0.176 | runs/wo-gh-12/reviewer-spec.packet.md | null |
| reviewer-security | skipped | 0.171 | runs/wo-gh-12/reviewer-security.packet.md | null |
| reviewer-tests | skipped | 0.132 | runs/wo-gh-12/reviewer-tests.packet.md | null |
| reviewer-architecture | skipped | 0.131 | runs/wo-gh-12/reviewer-architecture.packet.md | null |
| reviewer-design | skipped | 1.234 | runs/wo-gh-12/reviewer-design.packet.md | null |
| reviewer-ux | skipped | 1.197 | runs/wo-gh-12/reviewer-ux.packet.md | null |
| approver | completed | 0.021 | runs/wo-gh-12/report.json | null |
| triage-human | completed | 0.007 | - | null |
| deployer | packet_ready | 0.133 | runs/wo-gh-12/deployer.packet.md | null |
| observer | executed | 97114.141 | runs/wo-gh-12/observer.output.md | null |

## Decision

- Approver: No reviews were produced in this run, so the verdict is no_reviews; standing project reviews are never counted. (Counted 0 reviews, expected 4.)
- Human gate: Verdict is no_reviews, not approved, so a human is required.
