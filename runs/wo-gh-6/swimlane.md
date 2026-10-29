# Swimlane

Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | completed | 0.02 | runs/wo-gh-6/report.json | null |
| spec-writer | executed | 47158.482 | runs/wo-gh-6/spec-writer.output.md | null |
| test-writer | executed | 156523.125 | runs/wo-gh-6/test-writer.output.md | null |
| builder | executed | 787250.187 | runs/wo-gh-6/builder.output.md | null |
| reviewer-spec | executed | 130148.338 | runs/wo-gh-6/reviewer-spec.output.md | null |
| reviewer-security | executed | 113945.147 | runs/wo-gh-6/reviewer-security.output.md | null |
| reviewer-tests | executed | 49260.345 | runs/wo-gh-6/reviewer-tests.output.md | null |
| reviewer-architecture | executed | 153562.588 | runs/wo-gh-6/reviewer-architecture.output.md | null |
| reviewer-design | executed | 40700.913 | runs/wo-gh-6/reviewer-design.output.md | null |
| approver | completed | 0.04 | runs/wo-gh-6/report.json | null |
| approver | loopback | 0.0 | - | null |
| triage-human | completed | 0.006 | - | null |
| deployer | packet_ready | 0.089 | runs/wo-gh-6/deployer.packet.md | null |
| observer | executed | 171616.937 | runs/wo-gh-6/observer.output.md | null |

## Decision

- Approver: Reviewers reviewer-spec, reviewer-architecture requested changes.
- Human gate: Verdict is changes_requested, not approved, so a human is required.
