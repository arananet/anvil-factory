# Swimlane

Routing: 2 reviewers (reduced panel, 4 routed out)

**Cost**: No measured steps (7 executed steps)

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 32618.242 | runs/wo-gh-14/intake.output.md | null |
| spec-writer | executed | 105066.699 | runs/wo-gh-14/spec-writer.output.md | null |
| test-writer | executed | 121717.484 | runs/wo-gh-14/test-writer.output.md | null |
| builder | executed | 186377.969 | runs/wo-gh-14/builder.output.md | null |
| checks-gate | passed | 33273.399 | runs/wo-gh-14/checks-gate.pre-review.output.md | null |
| reviewer-spec | executed | 229082.949 | runs/wo-gh-14/reviewer-spec.output.md | null |
| reviewer-security | routed_out | 0.286 | runs/wo-gh-14/reviewer-security.packet.md | null |
| reviewer-tests | executed | 168186.507 | runs/wo-gh-14/reviewer-tests.output.md | null |
| reviewer-architecture | routed_out | 0.287 | runs/wo-gh-14/reviewer-architecture.packet.md | null |
| reviewer-design | routed_out | 1.384 | runs/wo-gh-14/reviewer-design.packet.md | null |
| reviewer-ux | routed_out | 0.976 | runs/wo-gh-14/reviewer-ux.packet.md | null |
| approver | completed | 0.06 | runs/wo-gh-14/report.json | null |
| triage-human | completed | 0.02 | - | null |
| deployer | packet_ready | 0.246 | runs/wo-gh-14/deployer.packet.md | null |
| observer | executed | 145841.872 | runs/wo-gh-14/observer.output.md | null |

## Decision

- Approver: All counted reviews passed. (Expected 2 reviews after routing.)
- Human gate: Verdict approved, but the work order carries the risk hint 'production-deploy', so a human is required.
