# Swimlane

Routing: 5 reviewers (full panel)

Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 58122.054 | runs/wo-gh-8/intake.output.md | null |
| spec-writer | executed | 41732.765 | runs/wo-gh-8/spec-writer.output.md | null |
| test-writer | executed | 57920.584 | runs/wo-gh-8/test-writer.output.md | null |
| builder | executed | 122546.205 | runs/wo-gh-8/builder.output.md | null |
| checks-gate | passed | 16050.852 | runs/wo-gh-8/checks-gate.pre-review.output.md | null |
| reviewer-spec | executed | 86496.514 | runs/wo-gh-8/reviewer-spec.output.md | null |
| reviewer-security | executed | 79090.264 | runs/wo-gh-8/reviewer-security.output.md | null |
| reviewer-tests | executed | 68396.702 | runs/wo-gh-8/reviewer-tests.output.md | null |
| reviewer-architecture | executed | 94995.096 | runs/wo-gh-8/reviewer-architecture.output.md | null |
| reviewer-design | executed | 66899.006 | runs/wo-gh-8/reviewer-design.output.md | null |
| approver | completed | 0.047 | runs/wo-gh-8/report.json | null |
| triage-human | completed | 0.013 | - | null |
| deployer | packet_ready | 0.238 | runs/wo-gh-8/deployer.packet.md | null |
| observer | executed | 209924.054 | runs/wo-gh-8/observer.output.md | null |

## Decision

- Approver: All counted reviews passed.
- Human gate: Verdict approved and no risk hints matched (scanned: auth, payments, data-deletion, production-deploy, secrets, publishing), so no human is required.
