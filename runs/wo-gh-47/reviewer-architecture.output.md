I passed the architecture review of wo-gh-47 and wrote it to `runs/wo-gh-47/reviewer-architecture.review.json`. I found no blockers, only three small notes.

**The finding sent back from attempt 1 is fixed.** The builder's change in attempt 2 is not empty. It closes the failed request's connection in `anvil/sinks.py`, adds `tests/test_live_progress_sink_errors.py`, and adds a `CHANGELOG.md` line. All three files are on the authorized list. I re-ran the order's three test files and all 31 tests passed. I did not run the full factory suite. Reviewer-tests reports 833 tests passing on the final tree.

**How it fits the project structure:**
- **Where the code sits:** all sink code is in `anvil/sinks.py`, next to the run recorder. Only `anvil/observe.py` calls it. `anvil/runner.py` changes in one line, where the recorder is created and given the station order. The runner has no network code and no use of the word "retry".
- **Frozen parts:** sinks are fed from the run state record, not from a new event, so `events.jsonl`, the webhook and the OTLP trace are unchanged. The state record only gains fields. A failing sink is recorded as an export error and the run goes on.
- **Config checking:** the allowed sink settings are defined once in `anvil/sinks.py`, and `anvil/config.py` checks `anvil.yaml` against them. A bad entry is refused when the file is loaded, and so is a token variable that could be passed to a station.
- **Decision record:** `brain/decisions/0015-live-progress-sinks.md` exists and states the trade-offs. The factory's `anvil.yaml` and the template for new projects both turn on only the issue comment sink. The project board sink is documented and off, as required.

**Small notes (non-blocking):**
- `SINK_TYPES` in `anvil/sinks.py:28` is never used. The sink types are also listed in two other places, so the lists could drift apart.
- When a run crashes, the code finds `anvil.yaml` by assuming the run folder is `runs/<work order id>`. If that fails it calls no sink and the crash is still recorded.
- Sinks are called before each local `state.json` write. A slow GitHub API delays that write by up to the configured timeout per request.

**Left for the approver:** as reviewer-spec noted, a resumed run calls no sink at the moment it resumes. The issue comment catches up at the next state write.
{"model": "claude-opus-5-5"}
