# Swimlane

Routing: 3 reviewers (reduced panel, 2 routed out)

Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 23207.514 | runs/wo-gh-9/intake.output.md | null |
| spec-writer | executed | 164992.219 | runs/wo-gh-9/spec-writer.output.md | null |
| test-writer | executed | 108797.038 | runs/wo-gh-9/test-writer.output.md | null |
| builder | executed | 107757.897 | runs/wo-gh-9/builder.output.md | null |
| checks-gate | passed | 29912.239 | runs/wo-gh-9/checks-gate.pre-review.output.md | null |
| reviewer-spec | executed | 103036.086 | runs/wo-gh-9/reviewer-spec.output.md | null |
| reviewer-security | executed | 100858.999 | runs/wo-gh-9/reviewer-security.output.md | null |
| reviewer-tests | executed | 64662.531 | runs/wo-gh-9/reviewer-tests.output.md | null |
| reviewer-architecture | routed_out | 0.227 | runs/wo-gh-9/reviewer-architecture.packet.md | null |
| reviewer-design | routed_out | 0.991 | runs/wo-gh-9/reviewer-design.packet.md | null |
| approver | completed | 0.044 | runs/wo-gh-9/report.json | null |
| triage-human | completed | 0.016 | - | null |
| deployer | packet_ready | 0.206 | runs/wo-gh-9/deployer.packet.md | null |
| observer | executed | 196019.243 | runs/wo-gh-9/observer.output.md | null |

## Decision

- Approver: All counted reviews passed. (Expected 3 reviews after routing.)
- Human gate: Verdict approved and no risk hints matched (scanned: auth, payments, data-deletion, production-deploy, secrets, publishing), so no human is required.
