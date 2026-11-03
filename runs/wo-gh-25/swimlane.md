# Swimlane

Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | completed | 0.014 | runs/wo-gh-25/report.json | null |
| spec-writer | executed | 343143.259 | runs/wo-gh-25/spec-writer.output.md | null |
| test-writer | executed | 501608.961 | runs/wo-gh-25/test-writer.output.md | null |
| builder | executed | 378053.87 | runs/wo-gh-25/builder.output.md | null |
| reviewer-spec | executed | 147070.308 | runs/wo-gh-25/reviewer-spec.output.md | null |
| reviewer-security | executed | 129792.756 | runs/wo-gh-25/reviewer-security.output.md | null |
| reviewer-tests | executed | 159121.752 | runs/wo-gh-25/reviewer-tests.output.md | null |
| reviewer-architecture | executed | 100262.605 | runs/wo-gh-25/reviewer-architecture.output.md | null |
| reviewer-design | executed | 49060.298 | runs/wo-gh-25/reviewer-design.output.md | null |
| approver | completed | 0.038 | runs/wo-gh-25/report.json | null |
| triage-human | completed | 0.011 | - | null |
| deployer | packet_ready | 0.243 | runs/wo-gh-25/deployer.packet.md | null |
| observer | failed | 25308.734 | runs/wo-gh-25/observer.packet.md | null |

## Decision

- Approver: All counted reviews passed.
- Human gate: Verdict approved and no risk hints matched (scanned: auth, payments, data-deletion, production-deploy, secrets, publishing), so no human is required.
