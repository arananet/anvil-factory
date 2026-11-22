# Builder report: wo-gh-47, live-progress-sinks

Spec: .openspec/specs/live-progress-sinks/spec.md (slug live-progress-sinks).
Spec base ref: factory main 10168fa560af7284b23f99e4e639621cf47eacd2.
I checked the tree against HEAD fd67af9 of the run branch, which merges 10168fa560af7284b23f99e4e639621cf47eacd2. For the frozen paths I diffed against 10168fa560af7284b23f99e4e639621cf47eacd2 itself: `test_s13_frozen_paths_and_existing_tests_untouched` passes when ANVIL_WORK_ORDER_ID=wo-gh-47.

## Blocking conflict (needs the owner)

`tests/test_station_budgets_completeness.py::PartitionConfiguration::test_s3_factory_other_keys_and_packet_budgets_unchanged` fails on the final tree. It is an existing, protected test from wo-gh-42. It asserts that the factory `anvil.yaml` equals the file at wo-gh-42's base ref 72a84126 apart from the two efficiency partition keys. This order's R4.1 and scenario S12 (`test_s12_factory_and_scaffold_enable_github_issue_only`) require the factory `anvil.yaml` to carry `observability.sinks: [{"type": "github-issue"}]`. No tree can satisfy both. I followed the work order (R4.1). I did not change the test, and I did not hide the key at load time. The test passes at HEAD without my change, so this is the only suite failure this order introduces. The way out is the same kind of owner-authorized unpin that 10168fa applied to two sibling assertions in that file: compare only the keys that wo-gh-42 owns.

## What changed, by scenario

- `anvil/sinks.py` (new, standard library only). Holds both sinks and their HTTP calls.
  - `SinkSet.deliver` calls the sinks in list order. It catches any failure and records it as `<type>: HTTP <status>` or `<type>: <ExceptionClass>`, never with a message, URL or body. It returns the `sinks` state field. Covers R1.5, R1.6, R1.7, S3.
  - `GitHubIssueSink`: activation reasons are checked in R2.2 order. At its first call it lists comments, following `Link: rel="next"` only on the configured API host, and adopts the comment carrying the `<!-- anvil-progress run_id=... -->` marker. Otherwise it POSTs one comment, then PATCHes it on every later call. Headers are Bearer, `application/vnd.github+json` and `anvil-progress`. The API base is `GITHUB_API_URL`. Covers R2, S1, S2, S4, S11, S15.
  - `render_issue_comment` renders scalar facts only (R2.5, R2.6):
    - heading, Pipeline, State, Verdict and Exit status shown verbatim;
    - one row per station in pipeline order, with these statuses: running, done, not run, pending, and anything else as recorded;
    - attempt (an unstamped step counts as attempt 1, because the runner stamps attempts only from 2 on) and tokens;
    - Loopbacks, Tokens, Cost, Updated, and Workflow run when `GITHUB_RUN_ID` is set.

    It never includes `error`, `detail`, output or paths. Covers S10, S15.
  - `GitHubProjectSink` (R3, S5, S6, S16):
    - The phase follows `record_phase` (R3.3).
    - At the first change it runs two lookups: the project with its status field and options, then the issue with its project items.
    - It sends `addProjectV2ItemById` only when the issue is missing from the project, and `updateProjectV2ItemFieldValue` only when the phase changes.
    - A missing project, field or option is recorded as the exact R3.5 note, and the sink goes inactive with that same text as its reason. It never sends any other mutation.
- `anvil/observe.py` (R1.2, R1.3, R1.4, R1.10).
  - `RunRecorder` takes `stations=` and builds a `SinkSet` from `observability.sinks`.
  - `state()` adds `stations` and a per-step `total_tokens` (computed with `summarize_steps([step])`), calls the sinks, then writes state.json once, with `sinks` and `export_errors` as the sinks left them.
  - The `run.started` event now triggers the run-start state write.
  - `finish()` adds `exit_status` to the finished record.
  - `mark_crashed(run_dir, error)` keeps its signature. It adds `exit_status` from report.json, loads `<run_dir>/../../anvil.yaml`, and calls the sinks before writing the crashed record.
- `anvil/runner.py`: one line. `RunRecorder(..., stations=order)`. No network code, no "retry". Covers R1.10, S13.
- `anvil/config.py`: `validate_sinks`, called by `load_anvil_config` on JSON configs. It raises ValueError naming `observability.sinks` or `observability.sinks[<i>]` and the key or type, and checks that `token_env` cannot reach a station (in `runtime.env_keep`, or neither in `STATION_ENV_DENY` nor in `runtime.env_deny`). `build_default_config` (and so `render_anvil_yaml` and `anvil init`) now carries the github-issue sink. Covers R1.1, R3.1, R5.3, R4.2, S8, S12.
- `anvil.yaml`: adds `"observability": {"sinks": [{"type": "github-issue"}]}` and nothing else. Covers R4.1, S12; this is what triggers the conflict above.
- Docs (R4.3, R4.5, S12, S14):
  - docs/OPERATIONS.md: new section on progress sinks covering github-issue, github-project (keys, phase table, defaults, the token requirement, the env_deny rule), and how tokens stay with the line.
  - docs/EXECUTION.md: where sinks are called in a run.
  - README.md: "Watching a run" section, 8 lines.
  - CHANGELOG.md entry.
  - brain/decisions/0015-live-progress-sinks.md.
- Not touched: .github/workflows, pipelines, anvil.json, anvil/executor.py, tools/line_comment.py (R4.4), and every existing test file. The new test files were written by the test-writer, and I did not edit them.

## Verification (real summary lines)

- New tests: `ANVIL_WORK_ORDER_ID=wo-gh-47 python -m unittest tests.test_live_progress_sinks tests.test_live_progress_project_sink` gave `Ran 30 tests ... OK`.
- Full suite, as I ran it in this station's environment: `python -m unittest discover -s tests -p 'test_*.py'` gave `Ran 832 tests in 104.365s`, `FAILED (failures=7, errors=1, skipped=13)`.
  - Five of the failures are the GITHUB_ACTOR approval tests in test_autonomous_line and test_governed_delivery. The test-writer saw them on the base tree too.
  - Two are pre-existing failures in test_token_efficiency: one failure and one error.
  - One is the conflict above.
- Full suite in the checks gate's scrubbed environment (`env -u GITHUB_ACTIONS -u GITHUB_ACTOR -u GITHUB_ACTOR_ID -u GITHUB_TRIGGERING_ACTOR ANVIL_WORK_ORDER_ID=wo-gh-47 python -m unittest discover -s tests -p 'test_*.py'`) gave `Ran 832 tests in 107.140s`, `FAILED (failures=2, errors=1, skipped=11)`. That is:
  - test_token_efficiency `test_project_handoff_executes_in_target_tree_s2` (FAIL) and `test_claude_correction_includes_both_attempts_s2` (ERROR). Both reproduce on a clean worktree of HEAD without my change (`Ran 50 tests ... FAILED (failures=1, errors=1, skipped=5)` for test_token_efficiency plus test_station_budgets_completeness at HEAD).
  - The conflict test above.
- Exact full factory test count: 832 tests: 802 at the base plus the 30 new ones.
- Exercised as a user would: I ran a scripted sdlc-default run with a reviewer failure against the local collector. Requests were GET, POST, then PATCH only: 38 requests for 37 state writes. I read the final comment: the station table in pipeline order, `State: finished`, `Verdict: rejected`, `Exit status: completed`, `Loopbacks: 2`, `Cost: not priced`, and the workflow link.

## New test files

- tests/test_live_progress_sinks.py
- tests/test_live_progress_project_sink.py

## Open or unverified

- The run-start write happens for `run.started` only. A resumed run's first state write is the one before its first station, a moment later. The recorder does not hold the kept steps at `run.resumed`, and the runner may change only at the construction site. This is documented in docs/EXECUTION.md.
- Nothing was run against real GitHub. The REST and GraphQL calls follow the documented API shapes and were exercised only against the local collector.
- Deterministic stations show tokens `0`, not `-`, because `summarize_steps` returns 0 for a step with no model call. R1.4 asks for exactly that value.
- In CI, factory.yml runs the suite without GH_TOKEN, and the checks gate strips GH_TOKEN, so existing tests that use wo-gh ids cannot post to real issues. A developer shell that sets GH_TOKEN and GITHUB_REPOSITORY and leaves GITHUB_API_URL unset, while running scaffolded wo-gh test runs, would reach api.github.com.
{"model": "claude-opus-5-5"}
