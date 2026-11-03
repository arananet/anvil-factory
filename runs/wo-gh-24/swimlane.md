# Swimlane

Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | completed | 0.02 | runs/wo-gh-24/report.json | null |
| spec-writer | executed | 90015.5 | runs/wo-gh-24/spec-writer.output.md | null |
| test-writer | executed | 173423.884 | runs/wo-gh-24/test-writer.output.md | null |
| builder | executed | 304399.049 | runs/wo-gh-24/builder.output.md | null |
| reviewer-spec | executed | 110428.774 | runs/wo-gh-24/reviewer-spec.output.md | null |
| reviewer-security | executed | 117024.204 | runs/wo-gh-24/reviewer-security.output.md | null |
| reviewer-tests | executed | 88488.967 | runs/wo-gh-24/reviewer-tests.output.md | null |
| reviewer-architecture | executed | 175976.24 | runs/wo-gh-24/reviewer-architecture.output.md | null |
| reviewer-design | executed | 84376.637 | runs/wo-gh-24/reviewer-design.output.md | null |
| approver | completed | 0.045 | runs/wo-gh-24/report.json | null |
| triage-human | completed | 0.013 | - | null |
| deployer | packet_ready | 0.233 | runs/wo-gh-24/deployer.packet.md | null |
| observer | executed | 221668.367 | runs/wo-gh-24/observer.output.md | null |

## Decision

- Approver: All counted reviews passed.
- Human gate: Verdict approved and no risk hints matched (scanned: auth, payments, data-deletion, production-deploy, secrets, publishing), so no human is required.
