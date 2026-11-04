# Source pack: ANVIL launch film v2

Work order: wo-gh-18. Inputs used: the brief (content/youtube-anvil-v2/brief.md), the spec (.openspec/specs/youtube-anvil-video-v2/spec.md), the repository files cited below, and the live Sentia site fetched on 2026-11-01. The pack covers the spec's closed claim list C1 to C11 and nothing else. Wording of the claims is the spec's wording and is not changed here. Where a source supports less than the claim says, the gap is flagged under "Flags" so reviewer-facts can judge it.

## Claims and sources

### C1. I am a software factory: work enters as an intake and leaves as reviewed, approved output.
- brain/project.md, "What ANVIL is": "ANVIL is a composable software factory framework. Work moves down a line of stations, each station has a clear contract, and the artifacts stay in the repo."
- docs/ARCHITECTURE.md, flow paragraph: a work order enters, a spec is written, a builder changes code, reviewers write reviews, the approver aggregates them, and human triage checks risk.
- README.md, opening: ANVIL is a framework for running software work down a line of stations.
- Supports: work enters as an intake (a work order) and passes reviewers and the approver before release.

### C2. The intake is one of three things: a feature, an idea, or an issue.
- anvil/model.py: KINDS = {"idea", "feature", "bug", "incident", "task", "content"}. The station is stations/intake/station.json ("Normalize an incoming work order into the shared shape", input: raw request).
- README.md, Greenfield: "The entry is an idea, not an issue." Brownfield: "The entry is a feature, a bug report, a production incident or a task, from a GitHub issue, the intake worker, or a file."
- intake-worker/worker.test.js posts kind "feature"; the worker maps GitHub issues to work orders (README, intake-worker section).
- Supports: feature and idea are intake kinds; an issue is a way in. See Flag F2.

### C3. The spec is written before any code.
- brain/project.md, Principles: "Spec before code: a change starts with an OpenSpec spec under .openspec/specs/."
- docs/ARCHITECTURE.md, Gates: "Spec gate: a spec exists, has a Status line and at least one Scenario line."
- pipelines/sdlc-default.json: spec-writer precedes test-writer and builder. For this very piece the spec was committed before the run (spec.md, "approved and written before this run").

### C4. Specialized stations do the work in a line, and no station approves its own work.
- brain/project.md: "The station that builds never approves its own work: builders and reviewers are different stations." Also "Work moves down a line of stations, each station has a clear contract."
- pipelines/content-video.json: ordered stages intake, brief-writer, researcher, writer, media-producer, a parallel review panel, approver, triage-human, publisher, observer.
- Every station prompt under stations/ carries the rule "Never approve your own work. Approval belongs to a different station." (for example stations/publisher/PROMPT.md, stations/observer/PROMPT.md, stations/researcher/PROMPT.md).
- tools/claude_station.py: reviewer stations get Edit, Write and NotebookEdit disallowed, so they cannot change the work they judge.

### C5. Five reviewers check the work in parallel.
- pipelines/sdlc-default.json: parallel group of five: reviewer-spec, reviewer-security, reviewer-tests, reviewer-architecture, reviewer-design.
- pipelines/content-default.json: parallel group of five: reviewer-facts, reviewer-voice, reviewer-platform, reviewer-brand, reviewer-design.
- Scope warning: the pipeline for this film, pipelines/content-video.json, has FOUR parallel reviewers (reviewer-facts, reviewer-voice, reviewer-brand, reviewer-design). README.md and docs/ARCHITECTURE.md also describe "four reviewers". See Flag F1.

### C6. A human approves before anything ships; nothing passes the human gate without that approval.
- README.md: "Publishing is a risk hint in ANVIL, so a content work order that will be published always stops at the human gate before the publisher station runs. That is deliberate: the factory prepares and checks, a human decides what goes out under their name."
- stations/publisher/PROMPT.md: it runs only after the approver passes and the human gate clears; "A human gate result that says required means stop. Do not publish, prepare the piece for the human instead."
- docs/ARCHITECTURE.md, Gates: human gate by risk hints (auth, payments, data-deletion, production-deploy, secrets; content adds publishing). "A verdict that is not approved also forces human review."
- pipelines/content-video.json: approver, then triage-human, then publisher.
- This work order carries the publishing risk hint, so this film stops at the gate. See Flag F3 for scope.

### C7. I keep a verified memory: a learning enters it only with provenance tied to a run record, and proposals that cannot be verified wait in quarantine.
- brain/learnings.md header: an entry belongs only after the memory gate checked its provenance against the run record; proposed learnings wait in brain/inbox/ (quarantined) and are never station context until `anvil promote-learning` verifies them.
- docs/MEMORY-GATE.md: the cited run report must exist, the cited artifact must exist, and the evidence must match the report; a refusal changes nothing on disk. Inbox content is listed as quarantined.
- README.md: "agent written learnings wait in a quarantined inbox and reach the verified store only when deterministic code verifies their provenance against the run record."
- stations/observer/PROMPT.md and docs/MEMORY-GATE.md: the observer is one source of proposals.

### C8. The models that staff the stations are routed per station through Cloudflare AI Gateway, and the work lives on GitHub.
- tools/anvil_station.py docstring: "per station routing lives here"; it reads the station's configured model from anvil.yaml and sends claude-* models to tools/claude_station.py; any other value fails loudly, with no silent substitution.
- tools/claude_station.py docstring: "Claude Code reaches the Cloudflare AI Gateway through the environment (ANTHROPIC_BASE_URL, ANTHROPIC_API_KEY, ANTHROPIC_CUSTOM_HEADERS)". No secret values are in the pack.
- anvil.yaml: a per station "model" field and a runtime command `python3 tools/anvil_station.py {packet} {output}`.
- GitHub: this repository is github.com/arananet/anvil-factory (linked from the live Sentia site footer); work orders arrive from GitHub issues (this one is issue 18); README.md describes GitHub issue intake and GitHub Pages publishing.

### C9. I am open source under the Apache 2.0 license.
- LICENSE: Apache License, Version 2.0, January 2004, with the appendix boilerplate.
- pyproject.toml: license = {text = "Apache-2.0"}.
- README.md, last section: "Apache 2.0 (LICENSE)", and the Apache 2.0 license badge.

### C10. Sentia is a concept sensor patch product that I designed and built end to end. It is live at sentia.info-693.workers.dev, including an interactive page where its five layers can be taken apart.
Live site, fetched 2026-11-01, HTTP 200 for https://sentia.info-693.workers.dev/ and https://sentia.info-693.workers.dev/take-apart:
- Home page: "Sentia Patch One is a square adhesive sensor patch". The FAQ calls it "a wellness and monitoring concept product". The page section "Five layers, 2.5 mm profile" lists layers 1 to 5: Top cover, Comfort foam, Sensing and processing board, Adhesive layer, Release liner.
- Home page footer: the site was designed and built end to end by ANVIL, an open source software factory (the footer links to github.com/arananet/anvil-factory). The footer also names a person; that name must not enter the film (spec: no person may be named).
- /take-apart: an interactive study with "Take apart the layers", a "Layer by layer" control, and the assembled stack listing the same five layers. Its model is the asset in the Assets section below.
- Stack order, top to bottom, confirmed in the GLB scene root nodes: Top cover (y 2.2), Comfort foam (1.55), Sensing and processing board (0.95), Adhesive layer (0.5), Release liner (0.15). Separation in the film runs along y, in that order.

### C11. This video was itself produced by my content line: written, rendered, produced and reviewed by my stations, and it stopped at the human gate.
- pipelines/content-video.json: the line is brief-writer, researcher, writer, media-producer, reviewers (facts, voice, brand, design), approver, triage-human, publisher, observer.
- This work order: risk hint "publishing" and the instruction that the finished video stops at the human gate and nothing is posted anywhere. The artifacts that evidence it (script.md, storyboard.md, production-notes.md, the MP4, checks.txt, reviews) are produced later in this run; this pack can only cite the pipeline and the work order. Reviewer-facts should confirm against those artifacts.

## Asset provenance: assets/patch-one.glb

As the spec records it (Assets section):
- File: content/youtube-anvil-v2/assets/patch-one.glb, 386708 bytes.
- sha256: daea8110b356865396b062bb1ca20944dd7103286758214cbc7804b43c50f523.
- The factory's own Blender product model of the Sentia Patch One, built by the Sentia project's product model run.
- Source: repo arananet/sentia, branch anvil/run-take-apart-product-model, commit c9f9bf9fcdf23cbd2107d26b11077ba5740f7a44, decoded from src/patch-one-glb.js. First party material, the same asset the live take apart page binds its interaction model to.

Checked in this run:
- Size on disk: 386708 bytes. sha256 on disk matches the value above.
- Committed in the wo-gh-18 setup commit, as the spec records (the commit hash is not resolvable in this checkout, so none is cited).
- glTF 2.0 binary, generator "Khronos glTF Blender I/O v4.5.51"; the scene has five root nodes: Top cover, Comfort foam, Sensing and processing board, Adhesive layer, Release liner.
- Not verified here: the upstream commit and the contents of src/patch-one-glb.js in the Sentia repository. The `gh` call was unauthenticated in this environment, so the provenance line rests on the spec's record.

## Flags for reviewer-facts

- F1 (C5, scope). Five parallel reviewers exist in pipelines/sdlc-default.json and pipelines/content-default.json. The panel for this film, pipelines/content-video.json, has four. The claim "Five reviewers check the work in parallel" is true of the factory's default software line and default content line, but not of this video's own line. If the film also says in the same breath that this video was reviewed by that panel, the two statements can read as a conflict. The pack does not change the claim; the writer should keep section 5 about the factory generally and section 7 about the video without a reviewer count.
- F2 (C2, kinds). Code lists six kinds (idea, feature, bug, incident, task, content). "Issue" is a source, not a kind in anvil/model.py, though README treats a GitHub issue as an entry point. The claim "one of three things: a feature, an idea, or an issue" is a simplification, and the pack cites what supports each word. No count beyond three may be stated, as the spec says.
- F3 (C6, scope). In code the human gate is triggered by risk hints and by a non approved verdict, not for every work order. Publishing is one of the hints, so anything that is published stops at the gate. The claim is supported for shipped content and for this film; "nothing ships without a human" in a broader sense (for example a plain code deploy with no risk hint) is not supported by the sources.
- F4 (C10). The live site says "concept product" and names the build by ANVIL in the footer. It also states product specs (profile, wear time, radios, certifications, weight) and a person's name. None of those is on the claim list and none may enter the script or on screen text.
- F5 (C11). The evidence for the produced, rendered and reviewed parts does not exist yet at this station.

## Not in the pack on purpose

Anything outside C1 to C11: product specifications of Sentia, build or run statistics, names of people, employers or other projects, and any count other than three intake kinds, five reviewers and five Sentia layers.
