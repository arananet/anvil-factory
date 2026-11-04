# Swimlane

Routing: 6 reviewers (full panel)

**Cost**: No measured steps (6 executed steps)

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 24157.726 | runs/wo-gh-13/intake.output.md | null |
| spec-writer | executed | 99010.233 | runs/wo-gh-13/spec-writer.output.md | null |
| test-writer | executed | 218552.408 | runs/wo-gh-13/test-writer.output.md | null |
| builder | executed | 215340.91 | runs/wo-gh-13/builder.output.md | null |
| checks-gate | passed | 30947.496 | runs/wo-gh-13/checks-gate.pre-review.output.md | null |
| reviewer-spec | executed | 118679.17 | runs/wo-gh-13/reviewer-spec.output.md | null |
| reviewer-security | executed | 160030.984 | runs/wo-gh-13/reviewer-security.output.md | null |
| reviewer-tests | failed | 50805.255 | runs/wo-gh-13/reviewer-tests.packet.md | null |
| reviewer-architecture | failed | 13228.47 | runs/wo-gh-13/reviewer-architecture.packet.md | null |
| reviewer-design | failed | 7679.806 | runs/wo-gh-13/reviewer-design.packet.md | null |
| reviewer-ux | failed | 518.853 | runs/wo-gh-13/reviewer-ux.packet.md | null |
| approver | completed | 0.058 | runs/wo-gh-13/report.json | null |
| triage-human | completed | 0.016 | - | null |
| deployer | packet_ready | 0.165 | runs/wo-gh-13/deployer.packet.md | null |
| observer | failed | 12797.071 | runs/wo-gh-13/observer.packet.md | null |

## Decision

- Approver: All counted reviews passed. (Counted 2 reviews, expected 6.)
- Human gate: Verdict approved and no risk hints matched (scanned: auth, payments, data-deletion, production-deploy, secrets, publishing), so no human is required.
