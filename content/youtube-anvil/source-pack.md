# Source pack: ANVIL, the software factory (YouTube explainer)

Work order: wo-gh-17. Inputs: brief.md, the spec (.openspec/specs/youtube-anvil-video/spec.md) and the repository files cited below. The live Sentia site was fetched on 2026-10-31. Only claims from the spec's closed list appear here. Each entry gives the source and the exact fact it supports. Where support is partial, the gap is stated and the writer must stay inside the "Safe wording" line.

## Status summary

| ID | Status | Note |
|----|--------|------|
| C1 | Sourced | |
| C2 | Partly sourced | Repository names feature, idea and issue as entry points, but also lists bug, incident and task. Use the safe wording. |
| C3 | Sourced | |
| C4 | Sourced | |
| C5 | Sourced | |
| C6 | Sourced | |
| C7 | Sourced | |
| C8 | Sourced | |
| C9 | Sourced | |
| C10 | Partly sourced | Live site supports "designed and built end to end by ANVIL", concept product, live URL. No file found saying Sentia is the FIRST product. |
| C11 | Partly sourced | pipelines/content-video.json exists. content/youtube-anvil/production-notes.md does not exist yet (the media-producer writes it after this step), so the produced and reviewed part can only be confirmed later. |

## Claims

### C1. ANVIL is a software factory: work enters as an intake and leaves as reviewed, approved output.
- brain/project.md, "What ANVIL is": "ANVIL is a composable software factory framework. Work moves down a line of stations, each station has a clear contract, and the artifacts stay in the repo."
- README.md, quote at the top: "ANVIL is a composable software factory: spec first, tests first, and no station approves its own work."
- docs/ARCHITECTURE.md: a work order enters, reviewers write reviews, the approver aggregates them, and human triage checks risk (line 13).
- Fact supported: ANVIL is a software factory, work enters and passes reviewers and an approver. Both "intake" and "approved output" are supported by the pipeline files (stations intake, approver in pipelines/sdlc-default.json).

### C2. The intake is one of three things: a feature, an idea, or an issue.
- README.md, "Two modes": greenfield "The entry is an idea, not an issue"; brownfield "The entry is a feature, a bug report, a production incident or a task, from a GitHub issue, the intake worker, or a file."
- docs/ARCHITECTURE.md line 58: "Intake accepts work orders of kind idea next to feature, bug, incident and task."
- stations/intake/station.json: intake is deterministic, "Normalize an incoming work order into the shared shape."
- Gap: the repository does not describe the intake as exactly three kinds. Idea, feature and GitHub issue are each supported as entry points; bug, incident and task also exist as kinds.
- Safe wording: say work comes in as a feature, an idea or an issue, which the spec allows. Do not say "only" or "exactly" these, and do not add other kinds.

### C3. The spec is written before any code.
- brain/project.md, Principles: "Spec before code: a change starts with an OpenSpec spec under .openspec/specs/."
- pipelines/sdlc-default.json: spec-writer precedes builder.
- Fact supported: a change starts with a spec, before the builder runs.

### C4. Specialized stations do the work in a line; no station approves its own work.
- brain/project.md: "The station that builds never approves its own work: builders and reviewers are different stations." Also "Work moves down a line of stations, each station has a clear contract."
- stations/publisher/PROMPT.md and stations/writer/PROMPT.md rule: "Never approve your own work. Approval belongs to a different station."
- pipelines/sdlc-default.json and pipelines/content-video.json: ordered stage lists of stations.

### C5. Five reviewers check the work in parallel: spec, security, tests, architecture and design.
- pipelines/sdlc-default.json, parallel group: reviewer-spec, reviewer-security, reviewer-tests, reviewer-architecture, reviewer-design.
- Station manifests exist for all five under stations/reviewer-*/station.json.
- Caution: this is the software pipeline. The content line, including this video's pipeline (content-video.json), uses a different four-reviewer panel (facts, voice, brand, design). The video must not suggest that these five reviewed the video itself.

### C6. A human approves before anything ships. The publisher does not run past the human gate.
- docs/ARCHITECTURE.md line 67: triage "treats publishing as a risk hint in the same set as payments or data deletion, because a published claim cannot be rolled back like a deploy"; line 22: a verdict that is not approved forces human review.
- stations/publisher/PROMPT.md: "It runs only after the approver passes and the human gate clears." and "A human gate result that says required means stop. Do not publish, prepare the piece for the human instead."
- README.md: "a content work order that will be published always stops at the human gate before the publisher station runs."
- pipelines/content-video.json: stages approver, triage-human, publisher in that order.
- Note for the writer: the gate described is the human gate for risky or publishing work. Say a human approves before anything ships, as the spec states.

### C7. Verified memory: a learning enters memory only with provenance tied to a run record, and unverifiable proposals wait in quarantine.
- docs/MEMORY-GATE.md, "The flow": proposals go to brain/inbox/ and are "quarantined"; "A learning becomes station context only after deterministic code verifies its provenance against the run record on disk."; promotion checks that the run report exists, the artifact exists and the evidence matches; a refusal "changes nothing on disk."
- brain/learnings.md header: "An entry belongs here only after the memory gate checked its provenance against the run record ... Proposed learnings wait in brain/inbox/ (quarantined) and are never station context until `anvil promote-learning` verifies them."
- Spec file: .openspec/specs/verified-memory/spec.md.

### C8. The models that staff the stations are routed per station through Cloudflare AI Gateway. The work lives on GitHub.
- tools/anvil_station.py docstring: "per station routing lives here"; the dispatcher reads the station's configured model from anvil.yaml and sends claude-* models through tools/claude_station.py.
- tools/claude_station.py docstring: "Claude Code reaches the Cloudflare AI Gateway through the environment (ANTHROPIC_BASE_URL, ANTHROPIC_API_KEY, ANTHROPIC_CUSTOM_HEADERS)".
- .github/workflows/anvil-execute-content-video.yml line 56: ANTHROPIC_BASE_URL points at gateway.ai.cloudflare.com (an AI Gateway route).
- Per station models are set in anvil.yaml (a "model" field per station).
- GitHub: repository remote is https://github.com/arananet/anvil-factory (.git/config); work orders come from GitHub issues (work-orders/issue-17.json, README intake section); the live Sentia footer links to the GitHub repositories.
- Do not state account names, gateway IDs or URLs from the workflow.

### C9. ANVIL is open source under the Apache 2.0 license.
- LICENSE: Apache License, Version 2.0, January 2004.
- README.md: license badge "License Apache 2.0" and the closing line "Apache 2.0".
- Live Sentia footer describes ANVIL as "an open source software factory."

### C10. Sentia, a concept sensor patch product, is the first product ANVIL designed and built end to end. It is live at sentia.info-693.workers.dev.
- Live site, https://sentia.info-693.workers.dev (fetched 2026-10-31): product "Sentia Patch One", "a square adhesive sensor patch"; footer: "Sentia is a concept product"; footer says it was "designed and built end to end by" ANVIL, "an open source software factory".
- Repository: docs/DESIGN-SYSTEM.md mentions "The Sentia launch page" shipped through the factory; tools/*.py docstrings refer to the Sentia project as origin of the station wrapper.
- Gap: nothing found in the repository or on the site says Sentia is the FIRST product ANVIL built. The spec's list contains it, so it is not outside the list, but the pack cannot confirm "first".
- Safe wording: "Sentia, a concept sensor patch product, was designed and built end to end by ANVIL, and it is live at sentia.info-693.workers.dev." Use "first" only if the operator confirms it. Do not describe product features (14 days, temperature, hydration, radios), since those are not on the claim list.

### C11. This video was itself produced by ANVIL's content line: written, produced and reviewed by its stations, and stopped at the human gate.
- pipelines/content-video.json: stages intake, brief-writer, researcher, writer, media-producer, parallel reviewer-facts, reviewer-voice, reviewer-brand, reviewer-design, approver, triage-human, publisher, observer.
- work-orders/issue-17.json: wo-gh-17, risk hint publishing, "stop at the human gate. Nothing is published anywhere."
- Gap: content/youtube-anvil/production-notes.md does not exist yet at the researcher step. The statement is true by design of the run, and the media-producer's notes and reviewer output will be the record.

## Words and names the writer must not use
- Names other than ANVIL and Sentia (plus Cloudflare AI Gateway and GitHub as in C8). The author's name appears on the live Sentia site footer and in repository files. It must not be spoken or shown, and no employer is to be named.
- Counts other than three intake kinds and five reviewers. Do not state the number of stations, pipelines or reviewers in the content panel.
- Do not mention the factory's expansion plans or product claims about the Sentia patch.

## Missing or open
1. "First product" (C10) is unsourced.
2. The "exactly three kinds" framing of intake (C2) is not literally in the repository.
3. production-notes.md (C11) will exist only after media-producer runs.
4. The five-reviewer panel (C5) belongs to the software pipeline, not the video line.
