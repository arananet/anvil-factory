# Swimlane

Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | completed | 0.012 | runs/wo-gh-17/report.json | null |
| brief-writer | executed | 26785.974 | runs/wo-gh-17/brief-writer.output.md | null |
| researcher | executed | 58050.698 | runs/wo-gh-17/researcher.output.md | null |
| writer | executed | 60692.936 | runs/wo-gh-17/writer.output.md | null |
| media-producer | executed | 425520.335 | runs/wo-gh-17/media-producer.output.md | null |
| reviewer-facts | executed | 15231.965 | runs/wo-gh-17/reviewer-facts.output.md | null |
| reviewer-voice | executed | 15370.182 | runs/wo-gh-17/reviewer-voice.output.md | null |
| reviewer-brand | executed | 26854.803 | runs/wo-gh-17/reviewer-brand.output.md | null |
| reviewer-design | executed | 18441.383 | runs/wo-gh-17/reviewer-design.output.md | null |
| approver | completed | 0.031 | runs/wo-gh-17/report.json | null |
| approver | loopback | 0.0 | - | null |
| triage-human | completed | 0.005 | - | null |
| publisher | executed | 22342.387 | runs/wo-gh-17/publisher.output.md | null |
| observer | executed | 94124.524 | runs/wo-gh-17/observer.output.md | null |

## Decision

- Approver: Reviewer reviewer-design requested changes.
- Human gate: Verdict is changes_requested, not approved, so a human is required.
