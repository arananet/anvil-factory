# Swimlane

Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 103914.965 | runs/wo-gh-7/intake.output.md | null |
| spec-writer | executed | 110486.031 | runs/wo-gh-7/spec-writer.output.md | null |
| test-writer | executed | 90027.826 | runs/wo-gh-7/test-writer.output.md | null |
| builder | executed | 99415.889 | runs/wo-gh-7/builder.output.md | null |
| checks-gate | passed | 13332.799 | runs/wo-gh-7/checks-gate.pre-review.output.md | null |
| reviewer-spec | executed | 126281.658 | runs/wo-gh-7/reviewer-spec.output.md | null |
| reviewer-security | executed | 75145.332 | runs/wo-gh-7/reviewer-security.output.md | null |
| reviewer-tests | executed | 73181.308 | runs/wo-gh-7/reviewer-tests.output.md | null |
| reviewer-architecture | executed | 135442.202 | runs/wo-gh-7/reviewer-architecture.output.md | null |
| reviewer-design | executed | 105313.022 | runs/wo-gh-7/reviewer-design.output.md | null |
| approver | completed | 0.046 | runs/wo-gh-7/report.json | null |
| triage-human | completed | 0.014 | - | null |
| deployer | packet_ready | 0.178 | runs/wo-gh-7/deployer.packet.md | null |
| observer | executed | 53974.747 | runs/wo-gh-7/observer.output.md | null |

## Decision

- Approver: All counted reviews passed.
- Human gate: Verdict approved and no risk hints matched (scanned: auth, payments, data-deletion, production-deploy, secrets, publishing), so no human is required.
