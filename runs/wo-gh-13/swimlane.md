# Swimlane

Routing: 4 reviewers (reduced panel, 2 routed out)

**Cost**: No measured steps (9 executed steps)

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 27381.079 | runs/wo-gh-13/intake.output.md | null |
| spec-writer | executed | 21672.558 | runs/wo-gh-13/spec-writer.output.md | null |
| test-writer | executed | 340161.983 | runs/wo-gh-13/test-writer.output.md | null |
| builder | executed | 217136.856 | runs/wo-gh-13/builder.output.md | null |
| checks-gate | passed | 35122.175 | runs/wo-gh-13/checks-gate.pre-review.output.md | null |
| reviewer-spec | executed | 77050.346 | runs/wo-gh-13/reviewer-spec.output.md | null |
| reviewer-security | routed_out | 0.225 | runs/wo-gh-13/reviewer-security.packet.md | null |
| reviewer-tests | executed | 151198.786 | runs/wo-gh-13/reviewer-tests.output.md | null |
| reviewer-architecture | routed_out | 0.223 | runs/wo-gh-13/reviewer-architecture.packet.md | null |
| reviewer-design | executed | 90760.743 | runs/wo-gh-13/reviewer-design.output.md | null |
| reviewer-ux | executed | 203710.871 | runs/wo-gh-13/reviewer-ux.output.md | null |
| approver | completed | 0.06 | runs/wo-gh-13/report.json | null |
| triage-human | completed | 0.018 | - | null |
| deployer | packet_ready | 0.21 | runs/wo-gh-13/deployer.packet.md | null |
| observer | executed | 122553.817 | runs/wo-gh-13/observer.output.md | null |

## Decision

- Approver: All counted reviews passed. (Expected 4 reviews after routing.)
- Human gate: Verdict approved and no risk hints matched (scanned: auth, payments, data-deletion, production-deploy, secrets, publishing), so no human is required.
