# Swimlane

Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | completed | 0.02 | runs/wo-gh-27/report.json | null |
| reviewer-design | executed | 343783.291 | runs/wo-gh-27/reviewer-design.output.md | null |
| reviewer-facts | executed | 51975.766 | runs/wo-gh-27/reviewer-facts.output.md | null |
| approver | completed | 0.04 | runs/wo-gh-27/report.json | null |
| triage-human | completed | 0.015 | - | null |
| publisher | executed | 145741.851 | runs/wo-gh-27/publisher.output.md | null |
| observer | executed | 101785.766 | runs/wo-gh-27/observer.output.md | null |

## Decision

- Approver: All counted reviews passed. (Counted 1 reviews, expected 2.)
- Human gate: Verdict approved, but the work order carries the risk hint 'publishing', so a human is required.
