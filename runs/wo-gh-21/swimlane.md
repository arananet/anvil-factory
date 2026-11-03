# Swimlane

Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | completed | 0.02 | runs/wo-gh-21/report.json | null |
| spec-writer | executed | 190044.719 | runs/wo-gh-21/spec-writer.output.md | null |
| test-writer | executed | 181795.289 | runs/wo-gh-21/test-writer.output.md | null |
| builder | executed | 327599.973 | runs/wo-gh-21/builder.output.md | null |
| reviewer-spec | executed | 270776.543 | runs/wo-gh-21/reviewer-spec.output.md | null |
| reviewer-security | executed | 118989.525 | runs/wo-gh-21/reviewer-security.output.md | null |
| reviewer-tests | executed | 80697.288 | runs/wo-gh-21/reviewer-tests.output.md | null |
| reviewer-architecture | executed | 199712.38 | runs/wo-gh-21/reviewer-architecture.output.md | null |
| reviewer-design | executed | 88498.235 | runs/wo-gh-21/reviewer-design.output.md | null |
| approver | completed | 0.044 | runs/wo-gh-21/report.json | null |
| approver | loopback | 0.0 | - | null |
| triage-human | completed | 0.007 | - | null |
| deployer | packet_ready | 0.224 | runs/wo-gh-21/deployer.packet.md | null |
| observer | executed | 36636.987 | runs/wo-gh-21/observer.output.md | null |

## Decision

- Approver: Reviewers reviewer-spec, reviewer-security requested changes. (Counted 4 reviews, expected 5.)
- Human gate: Verdict is changes_requested, not approved, so a human is required.
