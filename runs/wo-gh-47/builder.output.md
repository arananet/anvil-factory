# Builder report: wo-gh-47 (live-progress-sinks), attempt 3

## Base

- Base ref verified against: 10168fa560af7284b23f99e4e639621cf47eacd2 (factory main after the operator recalibration). It is an ancestor of the run branch HEAD fd67af9f03faedc6dccfa4cc46babc6f01bba763.
- No existing test file at the base ref is modified: `git diff --name-only 10168fa560af7284b23f99e4e639621cf47eacd2 -- tests/` lists nothing; only new files were added.
- Nothing under .github/workflows, pipelines/, anvil.json or tools/ is touched.

## What this attempt did

Attempt 2 was sent back because it changed no file and wrote no builder report. The implementation from attempt 1 is in the tree and was kept (the loopback asks not to start over). This attempt re-ran the whole suite, found the one remaining gate failure, showed that it is a contradiction between two tests rather than a code defect, and wrote this report. No code was changed in this attempt, because the only fix that would turn the gate green is editing a test, which this station must not do (see "Blocking conflict").

## Changes and the scenarios they serve

- `anvil/sinks.py` (new): the sink module beside the recorder (R1). `SinkSet` runs the configured sinks in order, bounds each call by `observability.timeout_seconds` and records a failure as `<type>: <reason>` in export_errors without stopping the line (R1, S3). `GitHubIssueSink`, entry type `github-issue` (R2): active only for `wo-gh-<n>` with `GITHUB_REPOSITORY` and the token variable (default `GH_TOKEN`) set, otherwise inactive with one recorded reason and no network call; creates one comment and then edits it, found again by a hidden marker with the run id; one row per pipeline station in pipeline order with status, attempt and tokens; verdict and any exit status shown as given, without a fixed list (so `runtime_refused` shows too); API base from `GITHUB_API_URL`. `GitHubProjectSink`, entry type `github-project` (R3): maps stations to the phases intake, spec, build, checks, review, human, done, failed; sends a status change only when the phase changes; adds a missing item; a missing project, field or option is recorded by name and the sink goes inactive; never changes the project's shape; inactive and said once when `token_env` is unset.
- `anvil/observe.py`: the recorder builds a `SinkSet` from `observability.sinks`, calls it with the state record (anvil/run-state@1, existing fields unchanged, adds `stations`, per-step `total_tokens`, `sinks`) at run start, before each station, after the last one and at run end; the crash path (`mark_crashed`) also delivers. No new event kind; events.jsonl is unchanged (R1).
- `anvil/config.py`: validation of `observability.sinks` (an ordered list; an entry with an unknown type, a missing or malformed `owner`/`number`, or unknown keys fails loading naming the entry index) (R1, test g); `render_anvil_yaml` (used by `anvil/scaffold.py`) now writes the `github-issue` sink for new projects (R4).
- `anvil/runner.py`: one line, the recorder is told the pipeline order (`stations=order`). No network code, no occurrence of the word the review-producer test forbids.
- `anvil.yaml`: the factory enables `{"type": "github-issue"}` (R4). See the blocking conflict.
- Docs: `docs/OPERATIONS.md` (sink configuration, github-project setup and token), `docs/EXECUTION.md` (when sinks are called), `README.md` (short "watching a run" section), `CHANGELOG.md`, `brain/decisions/0015-live-progress-sinks.md`.
- Tokens (R5): sinks read the token in the line process; the station environment reduction is unchanged; test (h) checks no token value appears in any file the run writes or any request body.

New test files (added by the test-writer, unchanged by the builder): `tests/test_live_progress_sinks.py` (24 tests) and `tests/test_live_progress_project_sink.py` (6 tests).

## Verification

Full factory suite, clean environment (the runner's own GITHUB_ACTOR and ANVIL_* variables removed, as on the checks gate):

```
env -i PATH="$PATH" HOME="$HOME" python -m unittest discover -s tests -p 'test_*.py'
Ran 832 tests in 100.868s
FAILED (failures=1, skipped=13)
FAIL: test_s3_factory_other_keys_and_packet_budgets_unchanged (test_station_budgets_completeness.PartitionConfiguration)
```

The exact full factory test count is 832. The single failure is the conflict below. Every test in both new files passes.

When I ran the suite inside this station's own environment, the approval tests in test_autonomous_line and test_governed_delivery also failed, because GITHUB_ACTOR is set to the real actor there, and so did two test_token_efficiency wrapper tests, because of the inherited ANVIL_* variables. Both groups pass in the clean environment. They have nothing to do with this order.

## Blocking conflict (unmet: the checks gate cannot pass without a test change)

`tests/test_station_budgets_completeness.py::test_s3_factory_other_keys_and_packet_budgets_unchanged` is an existing protected test from wo-gh-42. It loads the factory anvil.yaml, removes only the two efficiency partition keys and asserts that the whole config equals anvil.yaml at its fixed base ref 72a84126a600fafb99446946694b5de809e01e66. R4 requires the factory anvil.yaml to enable the github-issue sink, and the new test `test_s12_factory_and_scaffold_enable_github_issue_only` asserts it does. The two cannot both pass:

- With the `observability.sinks` block in anvil.yaml (the current tree): the wo-gh-42 test fails (above).
- With anvil.yaml reverted to HEAD (checked, then restored): `python -m unittest tests.test_station_budgets_completeness tests.test_live_progress_sinks.Shipping` gives `Ran 37 tests`, `FAILED (failures=1, skipped=7)`, with test_s12 failing.

The work order's reconciliation note says the wo-gh-42 efficiency keys and this order's observability keys do not overlap. That is true of the keys, but this test compares the whole config, so any new top-level key breaks it. This is the same kind of pin the operator removed in 10168fa for two other assertions. I kept the tree as the work order specifies (R4 met) and did not edit the protected test. The owner can authorize a one-line change to that test: also pop `observability` from `stripped` before the comparison, as 10168fa did for the other pins. After that change the suite should be fully green.

## Other open items

- Flaky new test: `test_live_progress_sinks.SinkFailures.test_s3_http_500_changes_nothing_but_one_export_error` failed 1 of 5 isolated runs (`/steps[2]/duration_ms`). It decides which report keys are volatile by comparing two baseline runs. When both baselines happen to record the same `duration_ms` for a step, that key counts as stable and the sink run's different timing fails the test. This is a defect in the test, not in the sink, since the report differs only in wall-clock timing. I did not edit it. It should treat `duration_ms` and timestamp keys as volatile.
- Live GitHub behaviour (a real issue comment and a real Projects v2 board) was exercised only against the local HTTP collector in the tests, not against api.github.com.
- No em dash or en dash in any produced file (checked with grep on every changed and new file).
{"model": "claude-opus-5-5"}
