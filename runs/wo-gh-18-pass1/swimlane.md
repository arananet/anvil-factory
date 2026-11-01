# Swimlane

Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | completed | 0.02 | runs/wo-gh-18/report.json | null |
| brief-writer | executed | 18672.509 | runs/wo-gh-18/brief-writer.output.md | null |
| researcher | executed | 18428.208 | runs/wo-gh-18/researcher.output.md | null |
| writer | executed | 37016.794 | runs/wo-gh-18/writer.output.md | null |
| media-producer | executed | 42093.482 | runs/wo-gh-18/media-producer.output.md | null |
| reviewer-facts | executed | 14072.353 | runs/wo-gh-18/reviewer-facts.output.md | null |
| reviewer-voice | executed | 11123.014 | runs/wo-gh-18/reviewer-voice.output.md | null |
| reviewer-brand | executed | 18385.037 | runs/wo-gh-18/reviewer-brand.output.md | null |
| reviewer-design | executed | 11203.28 | runs/wo-gh-18/reviewer-design.output.md | null |
| approver | completed | 0.045 | runs/wo-gh-18/report.json | null |
| triage-human | completed | 0.017 | - | null |
| publisher | executed | 12569.064 | runs/wo-gh-18/publisher.output.md | null |
| observer | executed | 91453.184 | runs/wo-gh-18/observer.output.md | null |

## Decision

- Approver: All counted reviews passed.
- Human gate: Verdict approved, but the work order carries the risk hint 'publishing', so a human is required.
