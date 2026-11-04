# Task packet: test-writer

## Station prompt

# Test Writer

## Role
Write tests that map to spec scenarios before implementation.

## Inputs
- spec

## Outputs
- tests

## Rules
- Work only from the inputs listed above and the work order in the packet.
- Produce the output as a file in the repo, not as chat text.
- If the inputs are not enough, say what is missing instead of guessing.
- Never approve your own work. Approval belongs to a different station.
- Keep the change small and mapped to a spec scenario where one applies.


## Work order

- id: wo-gh-26
- kind: feature
- title: Declared evidence wiring: reviewer-design receives declared evidence images, plus a review only content pipeline
- source: github-issue
- description: Implement the spec in .openspec/specs/declared-evidence-review/spec.md in the factory. Pipeline for this order is sdlc-default, selected by the run workflow.

The defect, with its executed evidence: the reviewer-design step in anvil/runner.py assembles its contact sheet only from capture-*.png files in the run directory. Declared evidence on a work order (WorkOrder.evidence_images) is validated by validate_work_order_paths and listed in the builder packet, but never reaches reviewer-design. Two runs proved the gap: the wo-gh-21 proof run on Sentia (design audit), where the packet referenced no contact sheet because the declared capture inputs were empty and reviewer-design declined to judge; and the wo-gh-18 polish run 41741357479, whose film review pass repeated authoring because no dedicated review execution with declared evidence exists.

Staging provenance: the film evidence under content/youtube-anvil-v2/ is staged in this run branch byte identical from anvil/run-youtube-video-v2 at 312e606. Verify before building: content/youtube-anvil-v2/anvil-youtube-v2.mp4 must hash to a277ce32c3ac7c30de5679524f49b1017ff028cfea2d38277deed73c4b44ecac and measure 21,401,761 bytes; if it differs, stop and say so in the builder output. That tree is input for the sibling film review order (issue 27): no station in THIS order modifies anything under content/.

Build, per the spec requirements and scenarios:

R1, declared captures: when a work order declares evidence_images, the reviewer-design step's capture set for contact sheet assembly is the declared PNG images (declaration order) plus any capture-*.png in the run directory. Only .png files join the capture set.

R2, loud failure: before the reviewer-design step executes, check every declared evidence image: it resolves inside the project tree and exists as a file. A missing or escaping declared image fails the step with the named error declared_evidence_missing and the offending path in the step detail; no review from that step is counted.

R3, packet naming: the reviewer-design packet's Evidence section lists the assembled contact sheet path AND each declared evidence image path individually.

R4, reviewer packets generally: when a work order declares evidence_images, the packet prepared for any reviewer station carries a "Declared evidence inputs" section listing each declared path. Additive only: existing packet sections, budgets and trimming are unchanged.

R5, review only pipeline: new file pipelines/content-film-review.json with exactly these stages: intake; parallel [reviewer-design, reviewer-facts]; approver; triage-human; publisher; observer. No authoring stations.

Tests (tests/, deterministic, named for their scenarios, small PNG fixtures in the style of tests/test_astra_consumption.py): T1 declared PNG fixtures with no run directory captures assemble a contact sheet through the reviewer-design preparation path and the packet references it. T2 a missing declared image fails preparation with declared_evidence_missing naming the path. T3 the packet lists the contact sheet and each declared path. T4 another reviewer station's packet carries the Declared evidence inputs section. T5 the new pipeline loads and its topological order matches R5 exactly. Full factory suite green, all pipelines valid (nine now). Add a CHANGELOG Unreleased entry.

Frozen surfaces: parse_review semantics and its file channel, the canonical review contract wording in anvil/runner.py, the nine reviewer prompts' Output Format sections, the verbatim review_suffix in tools/claude_station.py, the wo-gh-24 producer channel, and the wo-gh-21 PNG hardening (reuse it, never weaken it). Python standard library only. No em dash or en dash character in any produced file. Do not modify the run workflow (.github/workflows/anvil-execute-wo-gh-26.yml) and do not modify anything under content/.

Review channel discipline, restated for every reviewer station in this run: your review is exactly one JSON object that YOU write to runs/wo-gh-26/<your station>.review.json, and nothing else in that file. Prose and narrative belong in your .output.md only. Under the fixed producer merged in wo-gh-24, a review you only say in chat is not produced at all: if you do not write the file, the run records review_file_missing against your station.

GitHub issue: https://github.com/arananet/anvil-factory/issues/26
- risk_hints: 
- status: new

## Upstream steps

- intake: completed
- spec-writer: executed
