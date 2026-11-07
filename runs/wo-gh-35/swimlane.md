# Swimlane

Routing: 4 reviewers (reduced panel, 2 routed out)

**Cost**: No measured steps (8 executed steps)

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 3805.005 | runs/wo-gh-35/intake.output.md | null |
| spec-writer | executed | 20442.196 | runs/wo-gh-35/spec-writer.output.md | null |
| test-writer | executed | 27060.445 | runs/wo-gh-35/test-writer.output.md | null |
| builder | executed | 89371.132 | runs/wo-gh-35/builder.output.md | null |
| checks-gate | passed | 105335.064 | runs/wo-gh-35/checks-gate.pre-review.output.md | null |
| reviewer-spec | executed | 23978.061 | runs/wo-gh-35/reviewer-spec.output.md | null |
| reviewer-security | routed_out | 0.446 | runs/wo-gh-35/reviewer-security.packet.md | null |
| reviewer-tests | executed | 126108.424 | runs/wo-gh-35/reviewer-tests.output.md | null |
| reviewer-architecture | routed_out | 0.543 | runs/wo-gh-35/reviewer-architecture.packet.md | null |
| reviewer-design | executed | 19568.251 | runs/wo-gh-35/reviewer-design.output.md | null |
| reviewer-ux | failed | 21983.592 | runs/wo-gh-35/reviewer-ux.packet.md | null |
| approver | completed | 0.092 | runs/wo-gh-35/report.json | null |
| triage-human | completed | 0.042 | - | null |
| deployer | packet_ready | 0.506 | runs/wo-gh-35/deployer.packet.md | null |
| observer | executed | 19407.586 | runs/wo-gh-35/observer.output.md | null |

## Decision

- Approver: All counted reviews passed. (Counted 3 reviews, expected 4.)
- Human gate: Verdict approved and no risk hints matched (scanned: auth, payments, data-deletion, production-deploy, secrets, publishing), so no human is required.
