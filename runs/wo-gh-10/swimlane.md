# Swimlane

Routing: 5 reviewers (full panel)

Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 48367.625 | runs/wo-gh-10/intake.output.md | null |
| spec-writer | executed | 98860.917 | runs/wo-gh-10/spec-writer.output.md | null |
| test-writer | executed | 290259.229 | runs/wo-gh-10/test-writer.output.md | null |
| builder | executed | 355101.034 | runs/wo-gh-10/builder.output.md | null |
| checks-gate | passed | 29970.463 | runs/wo-gh-10/checks-gate.pre-review.output.md | null |
| reviewer-spec | executed | 111534.93 | runs/wo-gh-10/reviewer-spec.output.md | null |
| reviewer-security | executed | 146840.555 | runs/wo-gh-10/reviewer-security.output.md | null |
| reviewer-tests | executed | 64990.427 | runs/wo-gh-10/reviewer-tests.output.md | null |
| reviewer-architecture | executed | 96393.006 | runs/wo-gh-10/reviewer-architecture.output.md | null |
| reviewer-design | executed | 90928.711 | runs/wo-gh-10/reviewer-design.output.md | null |
| approver | completed | 0.047 | runs/wo-gh-10/report.json | null |
| approver | loopback | 0.0 | - | null |
| triage-human | completed | 0.008 | - | null |
| deployer | packet_ready | 0.091 | runs/wo-gh-10/deployer.packet.md | null |
| observer | executed | 70706.452 | runs/wo-gh-10/observer.output.md | null |

## Decision

- Approver: Reviewer reviewer-architecture requested changes.
- Human gate: Verdict is changes_requested, not approved, so a human is required.
