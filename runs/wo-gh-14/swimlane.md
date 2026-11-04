# Swimlane

Routing: 2 reviewers (reduced panel, 4 routed out)

**Cost**: No measured steps (7 executed steps)

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 26643.272 | runs/wo-gh-14/intake.output.md | null |
| spec-writer | executed | 169079.292 | runs/wo-gh-14/spec-writer.output.md | null |
| test-writer | executed | 209626.026 | runs/wo-gh-14/test-writer.output.md | null |
| builder | executed | 197477.031 | runs/wo-gh-14/builder.output.md | null |
| checks-gate | passed | 30764.815 | runs/wo-gh-14/checks-gate.pre-review.output.md | null |
| reviewer-spec | executed | 221666.534 | runs/wo-gh-14/reviewer-spec.output.md | null |
| reviewer-security | routed_out | 0.3 | runs/wo-gh-14/reviewer-security.packet.md | null |
| reviewer-tests | executed | 100739.783 | runs/wo-gh-14/reviewer-tests.output.md | null |
| reviewer-architecture | routed_out | 0.256 | runs/wo-gh-14/reviewer-architecture.packet.md | null |
| reviewer-design | routed_out | 1.221 | runs/wo-gh-14/reviewer-design.packet.md | null |
| reviewer-ux | routed_out | 0.861 | runs/wo-gh-14/reviewer-ux.packet.md | null |
| approver | completed | 0.037 | runs/wo-gh-14/report.json | null |
| triage-human | completed | 0.018 | - | null |
| deployer | packet_ready | 0.208 | runs/wo-gh-14/deployer.packet.md | null |
| observer | executed | 121374.065 | runs/wo-gh-14/observer.output.md | null |

## Decision

- Approver: All counted reviews passed. (Expected 2 reviews after routing.)
- Human gate: Verdict approved, but the work order carries the risk hint 'production-deploy', so a human is required.
