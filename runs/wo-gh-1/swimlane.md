# Swimlane

Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | completed | 0.013 | runs/wo-gh-1/report.json | null |
| spec-writer | executed | 23475.336 | runs/wo-gh-1/spec-writer.output.md | null |
| test-writer | executed | 140522.921 | runs/wo-gh-1/test-writer.output.md | null |
| builder | executed | 390238.902 | runs/wo-gh-1/builder.output.md | null |
| reviewer-spec | executed | 104513.235 | runs/wo-gh-1/reviewer-spec.output.md | null |
| reviewer-security | executed | 115634.53 | runs/wo-gh-1/reviewer-security.output.md | null |
| reviewer-tests | executed | 67835.5 | runs/wo-gh-1/reviewer-tests.output.md | null |
| reviewer-architecture | executed | 154133.642 | runs/wo-gh-1/reviewer-architecture.output.md | null |
| approver | completed | 0.035 | runs/wo-gh-1/report.json | null |
| triage-human | completed | 0.012 | - | null |
| deployer | packet_ready | 0.045 | runs/wo-gh-1/deployer.packet.md | null |
| observer | executed | 162127.099 | runs/wo-gh-1/observer.output.md | null |

## Decision

- Approver: All counted reviews passed.
- Human gate: Verdict approved and no risk hints matched (scanned: auth, payments, data-deletion, production-deploy, secrets, publishing), so no human is required.
