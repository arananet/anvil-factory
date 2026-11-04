# Swimlane

Routing: 6 reviewers (full panel)

**Cost**: No measured steps (11 executed steps)

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 37398.724 | runs/wo-gh-13/intake.output.md | null |
| spec-writer | executed | 53720.913 | runs/wo-gh-13/spec-writer.output.md | null |
| test-writer | executed | 222149.392 | runs/wo-gh-13/test-writer.output.md | null |
| builder | executed | 245103.065 | runs/wo-gh-13/builder.output.md | null |
| checks-gate | passed | 30740.506 | runs/wo-gh-13/checks-gate.pre-review.output.md | null |
| reviewer-spec | executed | 187726.239 | runs/wo-gh-13/reviewer-spec.output.md | null |
| reviewer-security | executed | 109630.719 | runs/wo-gh-13/reviewer-security.output.md | null |
| reviewer-tests | executed | 69805.219 | runs/wo-gh-13/reviewer-tests.output.md | null |
| reviewer-architecture | executed | 106280.775 | runs/wo-gh-13/reviewer-architecture.output.md | null |
| reviewer-design | executed | 93357.168 | runs/wo-gh-13/reviewer-design.output.md | null |
| reviewer-ux | executed | 112635.457 | runs/wo-gh-13/reviewer-ux.output.md | null |
| approver | completed | 0.039 | runs/wo-gh-13/report.json | null |
| approver | loopback | 0.0 | - | null |
| triage-human | completed | 0.008 | - | null |
| deployer | packet_ready | 0.066 | runs/wo-gh-13/deployer.packet.md | null |
| observer | executed | 78227.99 | runs/wo-gh-13/observer.output.md | null |

## Decision

- Approver: Reviewers reviewer-spec, reviewer-design, reviewer-ux requested changes.
- Human gate: Verdict is changes_requested, not approved, so a human is required.
