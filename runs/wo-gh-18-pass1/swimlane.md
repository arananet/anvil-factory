# Swimlane

Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | completed | 0.02 | runs/wo-gh-18/report.json | null |
| brief-writer | executed | 17974.281 | runs/wo-gh-18/brief-writer.output.md | null |
| researcher | executed | 19219.807 | runs/wo-gh-18/researcher.output.md | null |
| writer | executed | 24895.685 | runs/wo-gh-18/writer.output.md | null |
| media-producer | executed | 104539.607 | runs/wo-gh-18/media-producer.output.md | null |
| reviewer-facts | executed | 14407.075 | runs/wo-gh-18/reviewer-facts.output.md | null |
| reviewer-voice | executed | 15832.977 | runs/wo-gh-18/reviewer-voice.output.md | null |
| reviewer-brand | executed | 15784.264 | runs/wo-gh-18/reviewer-brand.output.md | null |
| reviewer-design | executed | 16530.668 | runs/wo-gh-18/reviewer-design.output.md | null |
| approver | completed | 0.044 | runs/wo-gh-18/report.json | null |
| triage-human | completed | 0.016 | - | null |
| publisher | executed | 25303.887 | runs/wo-gh-18/publisher.output.md | null |
| observer | executed | 61041.425 | runs/wo-gh-18/observer.output.md | null |

## Decision

- Approver: All counted reviews passed.
- Human gate: Verdict approved, but the work order carries the risk hint 'publishing', so a human is required.
