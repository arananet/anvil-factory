# Swimlane

Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | completed | 0.02 | runs/wo-gh-20/report.json | null |
| spec-writer | executed | 47336.937 | runs/wo-gh-20/spec-writer.output.md | null |
| test-writer | executed | 126194.814 | runs/wo-gh-20/test-writer.output.md | null |
| builder | executed | 203995.325 | runs/wo-gh-20/builder.output.md | null |
| reviewer-spec | executed | 104713.103 | runs/wo-gh-20/reviewer-spec.output.md | null |
| reviewer-security | executed | 137241.6 | runs/wo-gh-20/reviewer-security.output.md | null |
| reviewer-tests | executed | 82600.499 | runs/wo-gh-20/reviewer-tests.output.md | null |
| reviewer-architecture | executed | 164912.556 | runs/wo-gh-20/reviewer-architecture.output.md | null |
| reviewer-design | executed | 40164.714 | runs/wo-gh-20/reviewer-design.output.md | null |
| approver | completed | 0.039 | runs/wo-gh-20/report.json | null |
| approver | loopback | 0.0 | - | null |
| triage-human | completed | 0.006 | - | null |
| deployer | packet_ready | 0.093 | runs/wo-gh-20/deployer.packet.md | null |
| observer | executed | 58918.63 | runs/wo-gh-20/observer.output.md | null |

## Decision

- Approver: Reviewer reviewer-spec returned fail.
- Human gate: Verdict is rejected, not approved, so a human is required.
