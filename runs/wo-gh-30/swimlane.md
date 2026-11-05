# Swimlane

Routing: 4 reviewers (reduced panel, 2 routed out)

**Cost**: No measured steps (8 executed steps)

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 4777.848 | runs/wo-gh-30/intake.output.md | null |
| spec-writer | executed | 31127.646 | runs/wo-gh-30/spec-writer.output.md | null |
| test-writer | executed | 162100.185 | runs/wo-gh-30/test-writer.output.md | null |
| builder | executed | 121158.741 | runs/wo-gh-30/builder.output.md | null |
| checks-gate | passed | 100484.574 | runs/wo-gh-30/checks-gate.pre-review.output.md | null |
| reviewer-spec | executed | 19275.38 | runs/wo-gh-30/reviewer-spec.output.md | null |
| reviewer-security | routed_out | 0.142 | runs/wo-gh-30/reviewer-security.packet.md | null |
| reviewer-tests | executed | 19669.364 | runs/wo-gh-30/reviewer-tests.output.md | null |
| reviewer-architecture | routed_out | 0.146 | runs/wo-gh-30/reviewer-architecture.packet.md | null |
| reviewer-design | executed | 25140.257 | runs/wo-gh-30/reviewer-design.output.md | null |
| reviewer-ux | failed | 28295.7 | runs/wo-gh-30/reviewer-ux.packet.md | null |
| approver | completed | 0.055 | runs/wo-gh-30/report.json | null |
| approver | loopback | 0.0 | - | null |
| triage-human | completed | 0.008 | - | null |
| deployer | packet_ready | 0.106 | runs/wo-gh-30/deployer.packet.md | null |
| observer | executed | 28091.748 | runs/wo-gh-30/observer.output.md | null |

## Decision

- Approver: Reviewer reviewer-design requested changes. (Counted 3 reviews, expected 4.)
- Human gate: Verdict is changes_requested, not approved, so a human is required.
