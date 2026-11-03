# Swimlane

Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | completed | 0.009 | runs/wo-gh-20/report.json | null |
| spec-writer | executed | 218806.987 | runs/wo-gh-20/spec-writer.output.md | null |
| test-writer | executed | 112461.873 | runs/wo-gh-20/test-writer.output.md | null |
| builder | executed | 123756.852 | runs/wo-gh-20/builder.output.md | null |
| reviewer-spec | executed | 169762.386 | runs/wo-gh-20/reviewer-spec.output.md | null |
| reviewer-security | executed | 143818.533 | runs/wo-gh-20/reviewer-security.output.md | null |
| reviewer-tests | executed | 84601.088 | runs/wo-gh-20/reviewer-tests.output.md | null |
| reviewer-architecture | executed | 152497.216 | runs/wo-gh-20/reviewer-architecture.output.md | null |
| reviewer-design | executed | 72924.375 | runs/wo-gh-20/reviewer-design.output.md | null |
| approver | completed | 0.027 | runs/wo-gh-20/report.json | null |
| triage-human | completed | 0.011 | - | null |
| deployer | packet_ready | 0.204 | runs/wo-gh-20/deployer.packet.md | null |
| observer | executed | 40420.084 | runs/wo-gh-20/observer.output.md | null |

## Decision

- Approver: All counted reviews passed.
- Human gate: Verdict approved and no risk hints matched (scanned: auth, payments, data-deletion, production-deploy, secrets, publishing), so no human is required.
