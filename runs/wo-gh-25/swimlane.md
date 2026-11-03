# Swimlane

Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | completed | 0.027 | runs/wo-gh-25/report.json | null |
| spec-writer | executed | 44982.383 | runs/wo-gh-25/spec-writer.output.md | null |
| test-writer | executed | 211741.943 | runs/wo-gh-25/test-writer.output.md | null |
| builder | executed | 530429.857 | runs/wo-gh-25/builder.output.md | null |
| reviewer-spec | executed | 281684.422 | runs/wo-gh-25/reviewer-spec.output.md | null |
| reviewer-security | executed | 134211.668 | runs/wo-gh-25/reviewer-security.output.md | null |
| reviewer-tests | executed | 255924.669 | runs/wo-gh-25/reviewer-tests.output.md | null |
| reviewer-architecture | executed | 153672.954 | runs/wo-gh-25/reviewer-architecture.output.md | null |
| reviewer-design | executed | 62186.1 | runs/wo-gh-25/reviewer-design.output.md | null |
| approver | completed | 0.035 | runs/wo-gh-25/report.json | null |
| approver | loopback | 0.0 | - | null |
| triage-human | completed | 0.006 | - | null |
| deployer | packet_ready | 0.073 | runs/wo-gh-25/deployer.packet.md | null |
| observer | executed | 47692.88 | runs/wo-gh-25/observer.output.md | null |

## Decision

- Approver: Reviewer reviewer-spec returned fail.
- Human gate: Verdict is rejected, not approved, so a human is required.
