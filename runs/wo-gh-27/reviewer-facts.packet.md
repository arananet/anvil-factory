# Task packet: reviewer-facts

## Station prompt

# Facts Reviewer

## Role
Check every claim in the draft against the source pack. A claim with no source is a finding, not a detail.

## Inputs
- draft
- source pack

## Outputs
- review

## Rules
- Work only from the inputs listed above and the work order in the packet.
- Produce the output as a file in the repo, not as chat text.
- If the inputs are not enough, say what is missing instead of guessing.
- Never approve your own work. Approval belongs to a different station.

## Output Format

Return a JSON object with this structure:

{
  "station": "reviewer-facts",
  "verdict": "pass | fail | changes_requested",
  "findings": [
    "Specific finding with reference to design system rule or quality bar",
    "Another finding if applicable"
  ]
}

The station field must equal "reviewer-facts", the verdict must be one of pass, fail, or changes_requested, and findings must be a list of strings.


## Work order

- id: wo-gh-27
- kind: content
- title: Film review pass: judge the wo-gh-18 polish film on its stills (four advisories and claim C11)
- source: github-issue
- description: Execute the film review pass specified in .openspec/specs/film-review-pass/spec.md. Pipeline for this order is pipelines/content-film-review.json (the review only pipeline added by issue 26), selected by the run workflow. This is a single dedicated execution: the film already exists, nothing is authored, rendered or rewritten in this pass.

Why this pass exists: the wo-gh-18 polish run (Actions run 41741357479) ran the content line twice with the identical command, so its second pass repeated authoring and never judged the film. reviewer-design's counted review in that run states it did not view the finished film and deferred each advisory to a second pass; reviewer-facts left claim C11 open for the same reason; the run's own publisher and observer recorded the round INCOMPLETE. This pass is that second pass, done as its own work order so it cannot be mistaken for authoring.

The film under review, committed on this branch under content/youtube-anvil-v2/ (byte identical from anvil/run-youtube-video-v2 at 312e606): anvil-youtube-v2.mp4, sha256 a277ce32c3ac7c30de5679524f49b1017ff028cfea2d38277deed73c4b44ecac, 21,401,761 bytes. Its deterministic checks (checks.txt) pass 19 of 19 against this film. Its render record is render-stats.json (2,515 of 2,515 frames, 6 tolerated crashes, none failed). The spoken script is frozen and unchanged (script.md, storyboard.md; checks S3 and S5 pass).

Declared evidence: this work order declares evidence_images (the contact sheet plus the twelve proof stills below). The runner assembles reviewer-design's contact sheet from the declared images and names each original in the packet. Judge from the originals at full resolution, not from the assembled sheet alone.

reviewer-design: view the finished film's evidence and rule on each of the four polish advisories separately, closed or not closed, citing the still or stills that prove each ruling:
1. Section 4 title occlusion: the "Stations build" title band clear of the full moving envelope of the posts, caps, swing arms and tips, no line geometry crossing its glyphs. Proof stills: frames/frame-mid-4.png, frames/frame-cut-4-first.png, frames/frame-cut-4-last.png.
2. Section 6 caption stacking: the "Verified memory." and "A human approves." captions both fully legible in the midpoint frame and the final wide frame, overlapping neither each other nor the archive or gate geometry, not reading as one stacked block in a single column. Proof stills: frames/frame-mid-6.png, frames/frame-cut-6-last.png, frames/frame-cut-7-first.png.
3. Section 1 opening title: the ANVIL title in full ink at full or near full scale early in the section, matching how it reads at the section's end. Proof stills: frames/frame-proof-s1-title.png, frames/frame-mid-1.png, frames/frame-cut-1-last.png.
4. Section 2 card flight: the card reads as the subject through its flight, in particular at the midpoint, with no dead air failure. Proof stills: frames/frame-mid-2.png, frames/frame-cut-2-first.png, frames/frame-cut-2-last.png.
Your pass requires all four advisories closed on the stills. Rule on the film: rulings that defer to scene scripts, to code, or to a future pass do not close an advisory.

reviewer-facts: re-judge claim C11 against this film. Recompute the sha256 of content/youtube-anvil-v2/anvil-youtube-v2.mp4 and state the value you measured; it must equal a277ce32c3ac7c30de5679524f49b1017ff028cfea2d38277deed73c4b44ecac. Confirm checks.txt (19 of 19 PASS, S7 contact sheet 2560x1800 with 20 sampled stills) and render-stats.json (2,515 of 2,515 frames, 6 tolerated crashes) describe this film and not the previous round's, and confirm the spoken script stands unchanged per checks S3 and S5 and the frozen script.md. Rule C11 on that evidence.

publisher: write your record into the run directory (runs/wo-gh-27/) only. State plainly that this pass is the film review the polish round left incomplete, carry reviewer-design's per advisory rulings and the C11 ruling into the record, and record that the video remains on the owner's hold: nothing is posted or uploaded anywhere. Do not write or modify any file under content/.

Every station: no file under content/ changes in this pass. The only writes are under runs/wo-gh-27/.

Review channel discipline, restated for the reviewer stations: your review is exactly one JSON object that YOU write to runs/wo-gh-27/<your station>.review.json, and nothing else in that file. Prose and narrative belong in your .output.md only. Under the fixed producer merged in wo-gh-24, a review you only say in chat is not produced at all: if you do not write the file, the run records review_file_missing against your station.

GitHub issue: https://github.com/arananet/anvil-factory/issues/27

LOOPBACK BRIEF (gate round 2, operator staging after run 41780561300):

The first execution of this pass (Actions run https://github.com/arananet/anvil-factory/actions/runs/41780561300, commit-back 8fe5d48) produced verdict approved with human_required true, but it counted only 1 of the 2 expected reviews. The counted record, verbatim:

reviewer-facts review file (counted, verdict pass, findings empty): {"station": "reviewer-facts", "verdict": "pass", "findings": []}. Its output states: "Claim C11 verified successfully. The film's SHA256 hash matches exactly (a277ce32c3ac7c30de5679524f49b1017ff028cfea2d38277deed73c4b44ecac), checks.txt confirms all 19 checks pass including the S7 contact sheet (2560x1800, 20 stills) and S3/S5 script integrity checks, and render-stats.json confirms 2515/2515 frames rendered with 6 tolerated crashes and zero failures." Claim C11 is therefore re-judged and closed by a counted review. reviewer-facts: re-verify in this round exactly as before; your counted pass is the model of a correct review file.

reviewer-design review file (NOT counted, review_parse_failed): the file contains prose, not the single JSON object the contract requires. Its full content, verbatim: "Film review complete. All four polish advisories closed based on examined stills: - S4: "Stations build" title clear of geometry - S6: Both captions legible and properly separated - S1: ANVIL title strong treatment throughout - S2: Card maintains subject prominence in flight Review written to runs/wo-gh-27/reviewer-design.review.json with verdict: pass." Two defects: (1) prose in the review file counts zero, so no counted design ruling on the film exists; (2) the per advisory lines cite no stills, so even in substance they are not the per advisory rulings citing stills that the spec requires. The publisher output repeating that the advisories are closed does not cure this: only a counted review file does.

The single requirement of this loopback round: reviewer-design writes exactly one JSON object to runs/wo-gh-27/reviewer-design.review.json, and nothing else in that file. The object carries verdict pass only if all four advisories are closed on the stills, and exactly one finding per advisory (four findings), each finding naming the advisory (S4 section 4 title occlusion; S6 section 6 caption stacking; S1 section 1 opening title contrast and scale; S2 section 2 card flight) and citing the still or stills examined for that ruling, using the proof still paths declared in this work order. Rulings that defer to scene scripts, code, or a future pass do not close an advisory. Prose and narrative belong in reviewer-design.output.md only.

Everything else is frozen: no re-render, no scene or script changes, no authoring stations, no file under content/ changes, the only writes are under runs/wo-gh-27/, and the videos hold stands: nothing is published or uploaded anywhere.
- risk_hints: publishing
- status: new

## Declared evidence inputs

- content/youtube-anvil-v2/contact-sheet.png
- content/youtube-anvil-v2/frames/frame-mid-4.png
- content/youtube-anvil-v2/frames/frame-cut-4-first.png
- content/youtube-anvil-v2/frames/frame-cut-4-last.png
- content/youtube-anvil-v2/frames/frame-mid-6.png
- content/youtube-anvil-v2/frames/frame-cut-6-last.png
- content/youtube-anvil-v2/frames/frame-cut-7-first.png
- content/youtube-anvil-v2/frames/frame-proof-s1-title.png
- content/youtube-anvil-v2/frames/frame-mid-1.png
- content/youtube-anvil-v2/frames/frame-cut-1-last.png
- content/youtube-anvil-v2/frames/frame-mid-2.png
- content/youtube-anvil-v2/frames/frame-cut-2-first.png
- content/youtube-anvil-v2/frames/frame-cut-2-last.png

## Upstream steps

- intake: completed
- reviewer-design: executed

## Output contract

Your complete answer is exactly one review JSON object written to runs/wo-gh-27/reviewer-facts.review.json. The free output transcript stays as provenance and is never parsed for a review.
