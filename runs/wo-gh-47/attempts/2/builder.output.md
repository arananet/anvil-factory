# Builder report: wo-gh-47, live-progress-sinks (attempt 2 of 3)

Base ref verified against: 10168fa560af7284b23f99e4e639621cf47eacd2 (factory main after the
operator recalibration; it is an ancestor of the run branch HEAD fd67af9f03faedc6dccfa4cc46babc6f01bba763).
Spec: .openspec/specs/live-progress-sinks/spec.md. Sinks: github-issue (enabled), github-project (documented, off).

## Summary of this attempt

The checks gate of attempt 1 reported two failures. I looked at both and made no code change in
this attempt. Neither failure can be fixed by the builder without editing a test, and the rules
forbid that. Both need an owner or test-writer decision (see "Blocked" below). The implementation
from attempt 1 stays as it was. No builder report existed in the run tree after attempt 1, so this
file is the first one.

## What changed (whole order, against 10168fa560af7284b23f99e4e639621cf47eacd2)

- anvil/sinks.py (new): `SinkSet` plus the github-issue and github-project sinks. The issue sink
  creates one comment, then edits it, and finds it again by a hidden marker carrying the run id. Each
  call is bounded by observability.timeout_seconds. A failure is recorded as `<type>: <reason>` in
  export_errors. An inactive sink records its reason once and makes no network call. (R1, R2, R3, R5)
- anvil/observe.py: `RunRecorder` takes the pipeline order (`stations=`), adds `stations` and
  per-step `total_tokens` to the state record, and hands the record to the sinks at every state write.
  That covers run start, before each station, after the last one, finished with exit_status, and
  crashed through `mark_crashed`. No new event kind. events.jsonl, the webhook and OTLP are unchanged.
  (R1.2, R1.3, R1.10)
- anvil/config.py: validation of observability.sinks, which fails loading and names the entry.
  `render_anvil_yaml` (used by anvil/scaffold.py) now writes the github-issue entry for new
  projects. (R1.1, R4.2)
- anvil/runner.py: one line. The recorder is built with `stations=order`. No network code, and no
  new urllib or retry text. (R1.10, guardrail)
- anvil.yaml: `"observability": {"sinks": [{"type": "github-issue"}]}`. (R4.1)
- docs/OPERATIONS.md, docs/EXECUTION.md, README.md ("Watching a run"), CHANGELOG.md,
  brain/decisions/0015-live-progress-sinks.md. (R4.3, R4.5)
- anvil/scaffold.py is not modified. It already writes the config through `render_anvil_yaml`, so the
  default for new projects comes from anvil/config.py.
- New test files (from test-writer): tests/test_live_progress_sinks.py,
  tests/test_live_progress_project_sink.py.

## Verification

- Full suite, clean environment (station env vars removed, as in the gate):
  `env -i PATH="$PATH" HOME="$HOME" python -m unittest discover -s tests -p 'test_*.py'`
  -> `Ran 832 tests in 105.423s` / `FAILED (failures=1, skipped=13)`. The only failure is
  test_station_budgets_completeness...test_s3_factory_other_keys_and_packet_budgets_unchanged.
  Full factory test count: 832.
- In my raw station shell, with GITHUB_ACTOR and the other station env vars set, 7 more tests in
  test_autonomous_line, test_governed_delivery and test_token_efficiency fail. They react to the
  station's own GitHub environment (example: "does not match the authenticated GitHub actor") and
  pass in the clean environment. They are not caused by this change.
- New tests with this order's id:
  `env -i PATH="$PATH" HOME="$HOME" ANVIL_WORK_ORDER_ID=wo-gh-47 python -m unittest tests.test_live_progress_sinks tests.test_live_progress_project_sink`
  -> `Ran 30 tests in 19.891s` / `OK`.
- Protected surface: `git diff --quiet 10168fa560af7284b23f99e4e639621cf47eacd2 -- tools/line_comment.py .github/workflows pipelines anvil.json anvil/executor.py tests/test_*.py`
  is clean. The existing test files are unmodified. No U+2013 or U+2014 in any file this order
  produced.

## Blocked: needs a decision outside the builder

1. Contradiction between a protected existing test and R4.1, which fails on every tree.
   tests/test_station_budgets_completeness.py::test_s3_factory_other_keys_and_packet_budgets_unchanged
   compares the factory anvil.yaml with wo-gh-42's fixed base ref
   72a84126a600fafb99446946694b5de809e01e66. It removes only the two efficiency keys before the
   comparison, so any other addition to anvil.yaml fails it. R4.1 and the new S12 test
   (test_s12_factory_and_scaffold_enable_github_issue_only) require the factory anvil.yaml to carry
   the github-issue sink. If I removed the entry, S12 and R4.1 would fail instead. No tree passes
   both. This is the same kind of problem as the wo-gh-42 tree evidence the operator unpinned in
   10168fa: a fact about wo-gh-42's run, asserted on every later order. The file is protected for
   this order, so I did not edit it. Proposed owner fix: guard that test with
   `ANVIL_WORK_ORDER_ID == "wo-gh-42"`, as was done for `changed_paths`, or also remove
   `observability.sinks` in its comparison.

2. Flaky new test (test-writer defect, not an implementation defect).
   tests/test_live_progress_sinks.py::SinkFailures::test_s3_http_500_changes_nothing_but_one_export_error
   treats a report key as stable when two baseline runs happen to agree on it. It then requires the
   sink run to match that key. Step `duration_ms` values are wall-clock times of a few microseconds
   to a few ms (example: triage-human 0.013, approver 0.04), and they sometimes round equal across
   the two baselines. In 6 isolated runs, 3 failed on such keys (0.034 != 0.038 at /steps[11],
   0.763 != 0.735 at /steps[10]) and 3 passed. The full-suite run above passed it. The sink does not
   run inside any step's timed region, and the differences are microsecond noise, not sink latency.
   Suggested test fix: drop keys ending in `/duration_ms` from the comparison.

## Open items

- I did not exercise the sinks against the real GitHub API from this station. Stations do not get the
  token, by design (R5). Behaviour is covered against the local HTTP collector only.
{"model": "claude-opus-5-5"}
