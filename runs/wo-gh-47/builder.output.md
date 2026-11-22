# Builder report: wo-gh-47 (live-progress-sinks), attempt 2

Base ref I checked the tree against: factory main `ae0bbfb2af95b41d96d8e2af7c9f8b787f54d83b`. Spec: `.openspec/specs/live-progress-sinks/spec.md`. Sinks: `github-issue` and `github-project`.

## Loopback finding and how this attempt resolves it

The checks gate sent attempt 1 back because its delta was empty: that builder pass changed no file. The implementation from the earlier passes was already on the branch, so there was nothing new to write. This attempt re-reviewed that implementation against the spec and found one real defect, which it fixes:

- **Defect (R1.5, S3):** in `Sink.request` (`anvil/sinks.py`), `urlopen` raises `urllib.error.HTTPError` for a status of 400 or higher. That exception holds the open response, and nothing closed it. Every failed request kept a socket open until the exception was collected. I measured it: 5 failed requests with the exceptions still referenced left 5 descriptors open, and closing them released all 5.
- **Fix:** catch `HTTPError`, call `exc.close()`, then re-raise. Recording stays the same: still `github-issue: HTTP <status>` and nothing else.

Everything that already passed is kept as it was.

## Changed files in this attempt

| File | Change | Scenario |
|---|---|---|
| `anvil/sinks.py` | `Sink.request` closes the response of an `HTTPError` before re-raising (+8/-1 lines). | R1.5, S3 |
| `tests/test_live_progress_sink_errors.py` (new) | A regression test. A local collector answers 500. Five state writes give exactly `["github-issue: HTTP 500"]`. The test keeps the raised exceptions alive and asserts they hold no descriptor open. | R1.5, S3 |
| `CHANGELOG.md` | One line in the live-progress-sinks entry about the fix; the test list names the new file. | R4.5 |

The full change against ae0bbfb is unchanged from the earlier passes apart from these three files:
- `anvil/sinks.py` (new)
- `anvil/observe.py`
- `anvil/runner.py` (only the `RunRecorder(..., stations=order)` construction)
- `anvil/config.py` (`validate_sinks`, and the scaffold default in `build_default_config`)
- `anvil.yaml`
- `docs/OPERATIONS.md`
- `docs/EXECUTION.md`
- `README.md` ("Watching a run")
- `CHANGELOG.md`
- `brain/decisions/0015-live-progress-sinks.md`
- the new test files

`work_orders/wo-gh-47.json` and `runs/` were written by the line, not by the builder.

## Verification (final tree)

**Fail first:** with my `anvil/sinks.py` change set aside and only the new test present:

```
AssertionError: 6 not less than or equal to 0 : 6 descriptors held open by failed sink requests
FAILED (failures=1)
```

With the fix: `Ran 1 test`, `OK`.

**Project check** `python -m unittest discover -s tests -p 'test_*.py'`, run with the station `ANVIL_*` variables, `GITHUB_ACTOR` and `GITHUB_TRIGGERING_ACTOR` unset (the checks gate environment): exit 0, `Ran 833 tests in 111.164s`, `OK (skipped=14)`.

**Full factory test count: 833.** That is 802 at the base ref, plus 30 from the earlier passes, plus 1 new test.

**The order's own tests,** run with `ANVIL_WORK_ORDER_ID=wo-gh-47` (this command): `ANVIL_WORK_ORDER_ID=wo-gh-47 python -m unittest tests/test_live_progress_sinks.py tests/test_live_progress_project_sink.py tests/test_live_progress_sink_errors.py`. Result: `Ran 31 tests in 19.544s`, `OK`. S13 and S14 run here.

**New test files added by this order:**
- `tests/test_live_progress_sinks.py`
- `tests/test_live_progress_project_sink.py`
- `tests/test_live_progress_sink_errors.py` (this attempt)

**Guardrails, checked against ae0bbfb:**
- `git diff ae0bbfb -- .github/workflows pipelines anvil.json anvil/executor.py tools/line_comment.py` is empty.
- No existing test file was modified or deleted.
- `anvil/runner.py` has 0 matches for `urllib.request`, `http.client` or `retry`.
- No em dash or en dash appears in the files changed this attempt.
- Standard library only.

## Open or unverified

- **Resumed runs (R1.2):** a resumed run makes no separate state write at `run.resumed`. Its first write is the flush before the first remaining station, which comes right after. A separate write needs the kept steps, which the recorder does not have at that point. Getting them would mean changing the runner beyond the `RunRecorder(...)` construction, which this order does not allow. A reviewer should decide whether the first flush counts as the run start write.
- **S13 reading:** the runner already imports `urllib.parse.urlparse` at the base ref. So the check forbids network imports (`urllib.request`, `http.client`) rather than every `urllib` string.
- **Real GitHub:** neither sink has run against real GitHub, only against the local collector.
- **github-project:** this sink needs a Projects-capable token in `token_env`, which the workflow does not supply. It ships documented and off.
- **No retry:** a sink has no retry. When the API cannot be reached, each state write can wait up to `timeout_seconds` (5 by default).
- **Station environment:** in the raw station environment, with `GITHUB_ACTOR` and the `ANVIL_*` hand-off variables set, 7 existing tests fail. They fail the same way on `git archive ae0bbfb`, as recorded in the earlier passes. They pass in the checks gate environment.
{"model": "claude-opus-5-5"}
