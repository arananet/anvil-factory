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

- id: wo-gh-25
- kind: bug
- title: Render crash tolerance: judge chunks by their outputs, sweep the missing ranges
- source: github-issue
- description: Implement the spec in .openspec/specs/render-crash-tolerance/spec.md in the factory. Pipeline for this order is sdlc-default, selected by the run workflow.

The defect: the video line render wrapper (content/youtube-anvil-v2/blender/render_all.sh) judges each 60 frame chunk by the Blender process exit code, and a worker exiting 255 stops GNU xargs from launching the rest of the queue. Blender 4.5.15 headless under xvfb intermittently segfaults on exit after a chunk has completed (frames saved, SECTION_RENDER_DONE printed, then a crash writing /tmp/blender.crash.txt). Evidence: run 41382655551 died at the section 6 chunk at frame 121; run 41576145698 died at the section 7 chunk at frame 541 with 60 of 60 frames saved, stopping at 2,359 of 2,515 frames with 156 frames in three unlaunched chunks and no assembly. Peak memory in the logs is about 119 MB.

Staging provenance: the two files under change are staged in this run branch byte identical from anvil/run-youtube-video-v2 at f48ddb50, where the video line tooling lives today: content/youtube-anvil-v2/blender/render_all.sh (blob 2d77ea0ac5fabe11ca39ced436cffca908949194) and tools/render_stats.py (blob 4cb98dbd0a6e42db55e46b02301c046929c145e4). Verify the blobs before building; if they differ, stop and say so in the builder output. The fix lands on main as the canonical home of this tooling.

Build, per the spec scenarios:

S1, output judgment: a chunk (section s, frames a to b) succeeds if and only if every expected frame file frames/s<s>/f_<frame>.png (zero padded to 4 digits) for a..b exists AND frames/logs/render-s<s>-<a>.log contains a SECTION_RENDER_DONE line whose frames count equals b-a+1. The Blender exit code alone never decides. When the outputs satisfy the judgment but the process exited non-zero, the chunk is a success recorded as a tolerated crash with its chunk id.

S2, the queue never aborts: no chunk outcome prevents later queued chunks from launching. Remove the xargs abort behavior (today a worker exit of 255 stops the queue). The mechanism is the builder choice (for example workers that record their outcome and exit 0, with failure decided after the queue drains); the observable behavior is the spec.

S3 and S4, completion sweep: after the initial queue drains, compute missing frame ranges per section from durations.json and re-queue only those ranges at the configured chunk size, at most two sweep passes. A chunk recovered by a sweep is reported as requeued. If frames remain missing after the second pass, the render step exits non-zero and names each missing range (section and frame range).

S5, per chunk statistics: the wrapper leaves a machine readable per attempt outcome record under frames/logs/ (chunk id, range, exit code, output judgment), and tools/render_stats.py aggregates it into render-stats.json: every chunk reported under one of clean_exit, tolerated_crash, requeued, failed, with attempts count and final attempt exit behavior recorded for re-queued chunks. Existing render-stats.json keys and the production-notes statistics block form (read by tools/video_checks_v2.py scenario S8) are preserved exactly; per chunk data is additive only.

Compatibility, frozen: bash blender/render_all.sh runs from content/youtube-anvil-v2 with BLENDER and CHUNK honored; python3 tools/render_stats.py runs from the repo root with no arguments; frame and log naming unchanged; the SECTION_RENDER_DONE format from blender/film.py unchanged; durations.json remains the expectation source; frames already on disk are not re-rendered. Python stays standard library only. Bash for the wrapper shell.

Frozen surfaces: blender/film.py, blender/scene_line.py, blender/scene_proof.py, blender/common.py, blender/narrate.py, blender/soundbed.py, blender/durations.py, blender/assemble.py, the wo-gh-18 script and narration, work-orders/issue-18.json, the stations, the pipelines, model routing, parse_review semantics, the canonical review contract wording in anvil/runner.py, the nine reviewer prompts Output Format sections, and the wrapper review_suffix. Do not modify the run workflow (.github/workflows/anvil-execute-wo-gh-25.yml).

Tests (in tests/, named for their scenarios, deterministic, no Blender): drive the wrapper and the statistics aggregation with a fake chunk binary standing in for Blender through the BLENDER environment variable. T1: a fake chunk that writes its frames and DONE line then exits 1 counts success, records tolerated_crash, and the next chunk still runs. T2: a fake chunk writing partial frames is re-queued by range only, and completes when the missing frames appear, reported as requeued. T3: a chunk that never writes its frames fails the step after exactly two sweep passes, with the missing range named in the output. T4: the statistics aggregation folds outcome records into render-stats.json under the per chunk classes while preserving the existing keys. T5: with the first job failing hard, every later job is observed to launch. Full factory suite green, all eight pipelines valid. Add a CHANGELOG Unreleased entry. No em dash or en dash character in any produced file (project style rule).

Review channel discipline, restated for every reviewer station in this run: your review is exactly one JSON object that YOU write to runs/wo-gh-25/<your station>.review.json, and nothing else in that file. Prose and narrative belong in your .output.md only. Under the fixed producer merged in wo-gh-24, a review you only say in chat is not produced at all: if you do not write the file, the run records review_file_missing against your station.

GitHub issue: https://github.com/arananet/anvil-factory/issues/25

LOOPBACK ROUND (gate round 2, operator brief). Round 1 verdict of record: REJECTED (Actions run 41598962979), reviews counted 5 of 5 under the fixed producer: reviewer-spec fail, reviewer-security changes_requested, reviewer-tests pass, reviewer-architecture pass, reviewer-design pass. The round 1 implementation stands and is the base of this round (output based chunk judgment, the never abort queue, the completion sweep bounded at two passes, per attempt outcome records, the statistics outcome classes, and the deterministic tests). This round's only scope is the counted findings below; fix them and nothing else.

F1 (reviewer-spec, fail): the Blender invocation in render_all.sh changed film.py's call from six arguments to four, dropping the section total frames count and the resolution percent. The production invocation, as anvil/run-youtube-video-v2 runs it and as blender/film.py documents its entry point, is: blender -b -P blender/film.py -- $s $n frames/s$s 100 $a $b (section, total frames, outdir, res percent, first frame, last frame). Restore exactly that argument shape.

F2 (reviewer-spec, fail): the deterministic tests' fake Blenders implement the broken four argument shape, so the suite ratifies the break instead of catching it. Rebuild the fakes on film.py's real argument contract, and add a test that pins the wrapper's invocation: the fake records the arguments it received and the test asserts all six, including the total frames count and the res percent 100.

F3 (reviewer-spec, fail): tools/render_stats.py reads outcome.get("sweep", 0) when computing attempts, but the outcome records the wrapper writes carry an "attempts" field and never a "sweep" field (verified in the round 1 tree: render_all.sh writes attempts at its outcome writer; render_stats.py reads sweep at its aggregation), so attempts are always reported as 1. Align the two sides on the field the wrapper actually writes, and cover it with a test whose fixture outcome records are produced through the wrapper's own outcome writing path, not hand written copies that can drift again.

F4 (reviewer-security, changes_requested; five items, one theme: unvalidated values reach paths, JSON text and a command line). (a) Section ids from durations.json are used to construct file paths in render_all.sh and in render_stats.py without validation: validate section ids as integers where durations.json is parsed, on both sides, rejecting anything else before it reaches a path. (b) The outcome records in render_all.sh are built by shell heredoc interpolation into JSON strings: produce them with a real JSON encoder (python3 and its json module) so no interpolated value can break or inject the record. (c) render_stats.py trusts the VIDEO_CONTENT_DIR environment variable as a path without validation: resolve it and require an existing directory containing durations.json before use, with a clear error or the established fallback to the production location; state the chosen behavior in the builder output. (d) The section id reaches the Blender command line: integer validation under (a) closes the exposure; keep the existing quoting as well.

Everything else stays frozen exactly as round 1 specified, including the workflow file, the frozen scene and script surfaces, the compatibility contracts, and every round 1 test assertion (the fakes change only where F2 requires their interface to match film.py). Full factory suite green, all eight pipelines valid. Review channel discipline for this run: your review file is the channel. Write exactly one JSON object to your own runs/wo-gh-25/<station>.review.json and keep narrative in your .output.md only. The runner removes any pre-existing review file before your step, so round 1 files do not leak into this round's counting.
- risk_hints: 
- status: new

## Upstream steps

- intake: completed
