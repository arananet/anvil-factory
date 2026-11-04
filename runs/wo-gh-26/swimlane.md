# Swimlane

Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | completed | 0.012 | runs/wo-gh-26/report.json | null |
| spec-writer | executed | 81704.655 | runs/wo-gh-26/spec-writer.output.md | null |
| test-writer | executed | 132036.867 | runs/wo-gh-26/test-writer.output.md | null |
| builder | executed | 272919.253 | runs/wo-gh-26/builder.output.md | null |
| reviewer-spec | executed | 105386.04 | runs/wo-gh-26/reviewer-spec.output.md | null |
| reviewer-security | executed | 107732.794 | runs/wo-gh-26/reviewer-security.output.md | null |
| reviewer-tests | executed | 200448.897 | runs/wo-gh-26/reviewer-tests.output.md | null |
| reviewer-architecture | executed | 100618.184 | runs/wo-gh-26/reviewer-architecture.output.md | null |
| reviewer-design | executed | 64620.669 | runs/wo-gh-26/reviewer-design.output.md | null |
| approver | completed | 0.035 | runs/wo-gh-26/report.json | null |
| approver | loopback | 0.0 | - | null |
| triage-human | completed | 0.006 | - | null |
| deployer | packet_ready | 0.069 | runs/wo-gh-26/deployer.packet.md | null |
| observer | executed | 159509.181 | runs/wo-gh-26/observer.output.md | null |

## Decision

- Approver: Reviewers reviewer-spec, reviewer-tests requested changes. (Counted 4 reviews, expected 5.)
- Human gate: Verdict is changes_requested, not approved, so a human is required.
