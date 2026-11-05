# Render Crash Tolerance

Status: proposed
Slug: render-crash-tolerance

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose

Make the video line's deterministic render wrapper survive the Blender exit crash that has now killed two full renders of the wo-gh-18 film. The render step (content/youtube-anvil-v2/blender/render_all.sh) splits each section into 60 frame chunks and runs them through GNU xargs at 4 parallel processes, judging each chunk by the Blender process exit code. Blender 4.5.15 headless under xvfb intermittently segfaults on exit after a chunk's work is complete: the chunk renders all its frames, prints SECTION_RENDER_DONE, saves every frame, then crashes writing /tmp/blender.crash.txt. In run 41382655551 that was the section 6 chunk at frame 121; in run 41576145698 it was the section 7 chunk at frame 541 (60 of 60 frames saved), while the round 1 chunk exited cleanly. The wrapper treated the non-zero exit as chunk failure, xargs stopped launching queued chunks (a worker exit of 255 aborts the xargs queue), and the production step died before assembly: round 2 stopped at 2,359 of 2,515 frames with 156 frames in three unlaunched chunks and no MP4 assembled. Peak memory in the logs is about 119 MB, so the crash is not resource exhaustion. The defect is mechanical and lives in the wrapper, not in Blender and not in the scene: a chunk must be judged by its outputs, a single chunk failure must never abort the queue, and the frames a dead queue never launched must be recovered by a bounded completion sweep.

The code under change lives today only on the video production branch: content/youtube-anvil-v2/blender/render_all.sh and tools/render_stats.py, staged into this order's run branch byte identical from anvil/run-youtube-video-v2 at f48ddb50 (blobs 2d77ea0ac5fabe11ca39ced436cffca908949194 and 4cb98dbd0a6e42db55e46b02301c046929c145e4). The fix lands on main as the canonical home of the video line's deterministic tooling; the operator stages the merged result back onto the video branch for the wo-gh-18 film run.

## Requirements

- Output judgment. A chunk covering section s, frames a to b, is a success if and only if every expected frame file frames/s<s>/f_<frame>.png (frame numbers zero padded to 4 digits) for a..b exists on disk AND the chunk log frames/logs/render-s<s>-<a>.log contains a SECTION_RENDER_DONE line whose frames count equals b-a+1. The Blender process exit code is never by itself a success or failure criterion.
- Tolerated crash. When a chunk satisfies the output judgment but its process exited non-zero, the chunk counts as success and the anomaly is recorded in the render statistics as a tolerated crash carrying the chunk id (section and first frame). A tolerated crash is visible evidence in render-stats.json, never silently absorbed.
- The queue never aborts. No chunk outcome prevents any other queued chunk from launching. The current behavior, in which a worker exiting 255 stops GNU xargs from launching the remaining jobs, is removed by whatever mechanism the implementation chooses; the observable behavior is that with a failing chunk early in the job list, every later chunk still runs.
- Completion sweep. After the initial queue drains, the wrapper computes the missing frame ranges per section from the expectations in durations.json and re-queues only those ranges, chunked at the configured chunk size. At most two sweep passes run. A range recovered by a sweep is reported with the re-queued outcome class. If frames are still missing after the second sweep pass, the render step exits non-zero and its output names the missing ranges (section and frame range per range).
- Per chunk statistics. The render statistics (tools/render_stats.py writing content/youtube-anvil-v2/render-stats.json) report every chunk's outcome under one of these classes: clean_exit, tolerated_crash, requeued, failed. To make that possible the wrapper leaves a machine readable per attempt outcome record in the frames/logs directory (chunk id, frame range, process exit code, output judgment) which the statistics tool aggregates. A chunk that needed a sweep carries the requeued class, and its attempts count and final attempt exit behavior are recorded as fields so nothing about the earlier failure is hidden. Existing render-stats.json keys and the production-notes statistics block form, which tools/video_checks_v2.py scenario S8 reads, are preserved exactly; per chunk data is additive only.
- Resume preserved. Frames already on disk are not re-rendered; the existing skip behavior of the render (existing frames are skipped inside Blender) is unchanged, and a re-run of the wrapper on a complete tree judges chunks from their existing outputs.
- Compatibility frozen. Invocation contracts do not change: the production step runs bash blender/render_all.sh from the content/youtube-anvil-v2 directory with the BLENDER and CHUNK environment variables honored, and runs python3 tools/render_stats.py from the repository root with no arguments. Frame file naming, chunk log naming, the SECTION_RENDER_DONE line format produced by blender/film.py, and durations.json as the expectation source are all unchanged.
- Frozen surfaces. Scene content and scripts (blender/film.py, blender/scene_line.py, blender/scene_proof.py, blender/common.py, blender/narrate.py, blender/soundbed.py, blender/durations.py), blender/assemble.py, the wo-gh-18 script, narration and work order (work-orders/issue-18.json), the stations, the pipelines, model routing, and the review channel contract (parse_review semantics, the canonical contract wording, the reviewer prompts' Output Format sections, the wrapper review_suffix). This order changes only how the render wrapper judges chunks, recovers missing ranges, and reports per chunk outcomes.
- Python code stays on the standard library only. No em dash or en dash character in any produced file (project style rule).

## Scenarios

### Scenario: A chunk that crashes on exit after completing its work counts as success
- S1: Given a chunk whose process writes every expected frame file and a SECTION_RENDER_DONE line with the full frame count and then exits non-zero, when the wrapper judges the chunk, then the chunk is counted a success, the queue continues, and the render statistics record the chunk as tolerated_crash with its chunk id.

### Scenario: A failing chunk never aborts the queue
- S2: Given a job list whose first chunk fails (missing frames, no DONE line, non-zero exit), when the wrapper runs the queue, then every remaining chunk in the list still launches and is judged on its own outputs.

### Scenario: Partial output is recovered by range in the completion sweep
- S3: Given a chunk that wrote only part of its frame range, when the initial queue drains and the completion sweep computes missing ranges, then only the missing range is re-queued (not the whole section and not the frames already on disk), and when the re-queued chunk writes the missing frames the render completes with that chunk reported as requeued.

### Scenario: Frames still missing after two sweep passes fail the step by name
- S4: Given a range whose frames cannot be produced (the chunk keeps failing), when both sweep passes have run, then the render step exits non-zero and its output names each still missing range by section and frame range.

### Scenario: Statistics record every outcome class
- S5: Given a render whose chunks include a clean exit, a tolerated crash, a re-queued recovery and a failure, when tools/render_stats.py aggregates the outcome records, then render-stats.json reports each chunk under its outcome class, and the pre-existing statistics keys and the production-notes block keep their established form.

## Tests

Deterministic tests in the factory suite (tests/), named for their scenarios, driving the wrapper and the statistics aggregation with a fake chunk binary in place of Blender (the wrapper already honors the BLENDER environment variable). No real Blender is required.

- T1 (S1): a fake chunk that writes its frames and its DONE line then exits 1 is counted success, is recorded as tolerated_crash, and the following chunk still runs.
- T2 (S3): a fake chunk that writes partial frames is re-queued by range in the sweep; the sweep asks only for the missing frames; when the re-queued attempt writes them, the step succeeds and the chunk is reported as requeued.
- T3 (S4): a fake chunk that never writes its frames fails the step after exactly two sweep passes, and the failure output names the missing range.
- T4 (S5): the statistics aggregation folds the wrapper outcome records into render-stats.json with the per chunk classes, preserving the existing keys.
- T5 (S2): with the first job in the list failing hard, all later jobs are observed to launch (the fake records its invocations).
- The full factory suite stays green and all eight pipelines stay valid.
