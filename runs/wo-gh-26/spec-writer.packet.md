# Task packet: spec-writer

## Station prompt

# Spec Writer

## Role
Write or revise an OpenSpec spec from a work order.

## Inputs
- work order
- brain

## Outputs
- spec

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

LOOPBACK ROUND (gate round 2, operator brief). Round 1 verdict of record: changes_requested (Actions run 41769521684), reviews counted 4 of 5 under the fixed producer: reviewer-spec changes_requested, reviewer-tests changes_requested, reviewer-security pass, reviewer-architecture pass. reviewer-design executed but its review file contained prose, not a JSON object, so it counted zero. The round 1 implementation stands and is the base of this round (declared captures in the reviewer-design preparation path, the DeclaredEvidenceMissing error, packet evidence naming, the reviewer packet Declared evidence inputs section, the content-film-review pipeline, and the six scenario tests, which reviewer-tests verified as real and green). This round's only scope is the counted findings below and their single root cause.

ROOT CAUSE (operator verified against the tree and the suite output): tools/render_stats.py find_piece_dir() prefers the production location content/youtube-anvil-v2 whenever that directory contains durations.json. The operator staged the film evidence tree at that location, durations.json included. When the render crash tolerance tests invoked render_stats.py without VIDEO_CONTENT_DIR, the tool aggregated the staged tree instead of the tests' tmp fixtures: it rewrote content/youtube-anvil-v2/render-stats.json and the statistics block in production-notes.md from a tree with no working frames on disk (2,515 frames became 0, Blender 4.5.15 became unknown), and the four tests (s1, s3, s4, s5) failed because their tmp render-stats.json was never created. On main the same tests pass because main's content/youtube-anvil-v2 carries no durations.json. One cause explains both counted findings: the content modifications (reviewer-spec, reviewer-tests) and the four suite failures (reviewer-tests: the suite read 4 failed, 199 passed).

OPERATOR STAGING IN THIS PUSH (already done; verify and hold): content/youtube-anvil-v2/production-notes.md and content/youtube-anvil-v2/render-stats.json are restored byte identical to anvil/run-youtube-video-v2 at 312e606, and content/youtube-anvil-v2/durations.json is removed from this branch. The removal is deliberate and permanent for this branch: nothing in issues 26 or 27 renders or runs the statistics tool against the staged tree (reviewer-facts in issue 27 judges from checks.txt, render-stats.json, ffprobe.json and the film file), and its absence returns the render tests to their main behavior. Verify the two restored files match the 312e606 blobs and that durations.json is absent; if either differs, stop and say so in the builder output.

F1 (reviewer-spec and reviewer-tests, counted): the content modifications must not recur. No station in this round writes under content/, and no station runs tools/render_stats.py without VIDEO_CONTENT_DIR set to a scratch directory. The builder confirms at the end of its work that the tree under content/ is byte identical to this push's staging (the two restored files, durations.json absent, everything else untouched).

F2 (reviewer-tests, counted): the full factory suite must be green in this round, the four render crash tolerance tests included. With the root cause removed they are expected to behave exactly as on main. The builder runs the full suite in session before finishing and reports the result; a red suite is reported, never worked around by editing the render tests or the statistics tool (both frozen in this round).

F3 (reviewer-design, uncounted in round 1): your review file contained prose, so nothing you said counted. Write exactly one JSON object to runs/wo-gh-26/reviewer-design.review.json and keep narrative in your .output.md only. Scope note: the design surface of this order is the reviewer-design packet itself (spec scenarios S1 to S3 are about design evidence reaching the design reviewer). Judge whether the implemented packet carries the declared evidence as the spec requires; the absence of a user interface product in a factory wiring order is not itself a finding.

Everything else stays frozen exactly as round 1 specified, including the workflow file, the frozen review channel surfaces, and every round 1 test assertion. Full factory suite green, all nine pipelines valid.
- risk_hints: 
- status: new

## Upstream steps

- intake: completed
