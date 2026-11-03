# Swimlane

Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | completed | 0.01 | runs/wo-gh-22/report.json | null |
| spec-writer | executed | 126040.255 | runs/wo-gh-22/spec-writer.output.md | null |
| test-writer | executed | 100658.853 | runs/wo-gh-22/test-writer.output.md | null |
| builder | executed | 341587.664 | runs/wo-gh-22/builder.output.md | null |
| reviewer-tests | executed | 113280.921 | runs/wo-gh-22/reviewer-tests.output.md | null |
| approver | completed | 0.018 | runs/wo-gh-22/report.json | null |

## Decision

- Approver: No reviews were produced in this run, so the verdict is no_reviews; standing project reviews are never counted.
- Human gate: Verdict is no_reviews, not approved, so a human is required.
