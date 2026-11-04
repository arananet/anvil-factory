# Swimlane

Routing: 5 reviewers (reduced panel, 1 routed out)

**Cost**: No measured steps (10 executed steps)

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 36217.018 | runs/wo-gh-15/intake.output.md | null |
| spec-writer | executed | 69961.455 | runs/wo-gh-15/spec-writer.output.md | null |
| test-writer | executed | 143708.013 | runs/wo-gh-15/test-writer.output.md | null |
| builder | executed | 386124.427 | runs/wo-gh-15/builder.output.md | null |
| checks-gate | passed | 34433.861 | runs/wo-gh-15/checks-gate.pre-review.output.md | null |
| reviewer-spec | executed | 191514.906 | runs/wo-gh-15/reviewer-spec.output.md | null |
| reviewer-security | executed | 130178.848 | runs/wo-gh-15/reviewer-security.output.md | null |
| reviewer-tests | executed | 256322.575 | runs/wo-gh-15/reviewer-tests.output.md | null |
| reviewer-architecture | executed | 112089.764 | runs/wo-gh-15/reviewer-architecture.output.md | null |
| reviewer-design | executed | 254282.756 | runs/wo-gh-15/reviewer-design.output.md | null |
| reviewer-ux | routed_out | 1.335 | runs/wo-gh-15/reviewer-ux.packet.md | null |
| approver | completed | 0.043 | runs/wo-gh-15/report.json | null |
| approver | loopback | 0.0 | - | null |
| triage-human | completed | 0.006 | - | null |
| deployer | packet_ready | 0.314 | runs/wo-gh-15/deployer.packet.md | null |
| observer | executed | 47140.787 | runs/wo-gh-15/observer.output.md | null |

## Decision

- Approver: Reviewers reviewer-spec, reviewer-security, reviewer-design requested changes. (Expected 5 reviews after routing.)
- Human gate: Verdict is changes_requested, not approved, so a human is required.
