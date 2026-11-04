# Swimlane

Routing: 5 reviewers (full panel)

**Cost**: No measured steps (10 executed steps)

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 72195.052 | runs/wo-gh-11/intake.output.md | null |
| spec-writer | executed | 158383.651 | runs/wo-gh-11/spec-writer.output.md | null |
| test-writer | executed | 168323.085 | runs/wo-gh-11/test-writer.output.md | null |
| builder | executed | 427110.766 | runs/wo-gh-11/builder.output.md | null |
| checks-gate | passed | 27024.065 | runs/wo-gh-11/checks-gate.pre-review.output.md | null |
| reviewer-spec | executed | 280973.739 | runs/wo-gh-11/reviewer-spec.output.md | null |
| reviewer-security | executed | 148860.86 | runs/wo-gh-11/reviewer-security.output.md | null |
| reviewer-tests | executed | 170831.552 | runs/wo-gh-11/reviewer-tests.output.md | null |
| reviewer-architecture | executed | 141489.932 | runs/wo-gh-11/reviewer-architecture.output.md | null |
| reviewer-design | executed | 30711.884 | runs/wo-gh-11/reviewer-design.output.md | null |
| approver | completed | 0.044 | runs/wo-gh-11/report.json | null |
| approver | loopback | 0.0 | - | null |
| triage-human | completed | 0.008 | - | null |
| deployer | packet_ready | 0.226 | runs/wo-gh-11/deployer.packet.md | null |
| observer | executed | 14432.934 | runs/wo-gh-11/observer.output.md | null |

## Decision

- Approver: Reviewers reviewer-tests, reviewer-architecture requested changes.
- Human gate: Verdict is changes_requested, not approved, so a human is required.
