# Swimlane

Routing: 5 reviewers (reduced panel, 1 routed out)

**Cost**: No measured steps (10 executed steps)

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 42195.947 | runs/wo-gh-15/intake.output.md | null |
| spec-writer | executed | 50328.853 | runs/wo-gh-15/spec-writer.output.md | null |
| test-writer | executed | 474496.204 | runs/wo-gh-15/test-writer.output.md | null |
| builder | executed | 234340.651 | runs/wo-gh-15/builder.output.md | null |
| checks-gate | passed | 34328.901 | runs/wo-gh-15/checks-gate.pre-review.output.md | null |
| reviewer-spec | executed | 171114.681 | runs/wo-gh-15/reviewer-spec.output.md | null |
| reviewer-security | executed | 105107.84 | runs/wo-gh-15/reviewer-security.output.md | null |
| reviewer-tests | executed | 101333.88 | runs/wo-gh-15/reviewer-tests.output.md | null |
| reviewer-architecture | executed | 104457.533 | runs/wo-gh-15/reviewer-architecture.output.md | null |
| reviewer-design | executed | 80972.478 | runs/wo-gh-15/reviewer-design.output.md | null |
| reviewer-ux | routed_out | 0.92 | runs/wo-gh-15/reviewer-ux.packet.md | null |
| approver | completed | 0.041 | runs/wo-gh-15/report.json | null |
| approver | loopback | 0.0 | - | null |
| triage-human | completed | 0.006 | - | null |
| deployer | packet_ready | 0.073 | runs/wo-gh-15/deployer.packet.md | null |
| observer | executed | 51805.021 | runs/wo-gh-15/observer.output.md | null |

## Decision

- Approver: Reviewers reviewer-security, reviewer-architecture, reviewer-design requested changes. (Expected 5 reviews after routing.)
- Human gate: Verdict is changes_requested, not approved, so a human is required.
