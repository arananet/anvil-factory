# Swimlane

Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | completed | 0.009 | runs/wo-gh-4/report.json | null |
| brief-writer | executed | 126293.699 | runs/wo-gh-4/brief-writer.output.md | null |
| researcher | executed | 234159.06 | runs/wo-gh-4/researcher.output.md | null |
| writer | executed | 204749.512 | runs/wo-gh-4/writer.output.md | null |
| media-producer | executed | 361887.04 | runs/wo-gh-4/media-producer.output.md | null |
| reviewer-facts | executed | 179450.443 | runs/wo-gh-4/reviewer-facts.output.md | null |
| reviewer-voice | executed | 154423.401 | runs/wo-gh-4/reviewer-voice.output.md | null |
| reviewer-platform | executed | 64231.597 | runs/wo-gh-4/reviewer-platform.output.md | null |
| reviewer-brand | executed | 142594.822 | runs/wo-gh-4/reviewer-brand.output.md | null |
| reviewer-design | executed | 133028.73 | runs/wo-gh-4/reviewer-design.output.md | null |
| approver | completed | 0.029 | runs/wo-gh-4/report.json | null |
| approver | loopback | 0.0 | - | null |
| triage-human | completed | 0.005 | - | null |
| publisher | executed | 160447.354 | runs/wo-gh-4/publisher.output.md | null |
| observer | executed | 68843.612 | runs/wo-gh-4/observer.output.md | null |

## Decision

- Approver: Reviewer reviewer-voice requested changes.
- Human gate: Verdict is changes_requested, not approved, so a human is required.
