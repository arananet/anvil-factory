# Swimlane

Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | completed | 0.023 | runs/wo-gh-16/report.json | null |
| spec-writer | executed | 66198.453 | runs/wo-gh-16/spec-writer.output.md | null |
| test-writer | executed | 222151.938 | runs/wo-gh-16/test-writer.output.md | null |
| builder | executed | 251332.159 | runs/wo-gh-16/builder.output.md | null |
| reviewer-spec | executed | 169009.604 | runs/wo-gh-16/reviewer-spec.output.md | null |
| reviewer-security | executed | 214645.94 | runs/wo-gh-16/reviewer-security.output.md | null |
| reviewer-tests | executed | 89140.793 | runs/wo-gh-16/reviewer-tests.output.md | null |
| reviewer-architecture | executed | 90109.723 | runs/wo-gh-16/reviewer-architecture.output.md | null |
| reviewer-design | executed | 40794.117 | runs/wo-gh-16/reviewer-design.output.md | null |
| approver | completed | 0.042 | runs/wo-gh-16/report.json | null |
| triage-human | completed | 0.013 | - | null |
| deployer | packet_ready | 0.194 | runs/wo-gh-16/deployer.packet.md | null |
| observer | executed | 194024.984 | runs/wo-gh-16/observer.output.md | null |

## Decision

- Approver: All counted reviews passed. (Counted 2 reviews, expected 5.)
- Human gate: Verdict approved and no risk hints matched (scanned: auth, payments, data-deletion, production-deploy, secrets, publishing), so no human is required.
