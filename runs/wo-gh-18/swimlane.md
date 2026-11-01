# Swimlane

Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | completed | 0.021 | runs/wo-gh-18/report.json | null |
| brief-writer | executed | 26368.492 | runs/wo-gh-18/brief-writer.output.md | null |
| researcher | executed | 17393.207 | runs/wo-gh-18/researcher.output.md | null |
| writer | executed | 45062.468 | runs/wo-gh-18/writer.output.md | null |
| media-producer | executed | 24732.257 | runs/wo-gh-18/media-producer.output.md | null |
| reviewer-facts | executed | 20366.743 | runs/wo-gh-18/reviewer-facts.output.md | null |
| reviewer-voice | executed | 21442.117 | runs/wo-gh-18/reviewer-voice.output.md | null |
| reviewer-brand | executed | 11362.873 | runs/wo-gh-18/reviewer-brand.output.md | null |
| reviewer-design | executed | 18547.429 | runs/wo-gh-18/reviewer-design.output.md | null |
| approver | completed | 0.046 | runs/wo-gh-18/report.json | null |
| triage-human | completed | 0.017 | - | null |
| publisher | executed | 21560.25 | runs/wo-gh-18/publisher.output.md | null |
| observer | executed | 138104.576 | runs/wo-gh-18/observer.output.md | null |

## Decision

- Approver: All counted reviews passed.
- Human gate: Verdict approved, but the work order carries the risk hint 'publishing', so a human is required.
