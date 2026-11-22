# Builder report: wo-gh-47 (live-progress-sinks)

Base ref I checked the tree against: factory main `ae0bbfb2af95b41d96d8e2af7c9f8b787f54d83b`. The spec is `.openspec/specs/live-progress-sinks/spec.md`. The sinks are `github-issue` and `github-project`.

## What this attempt did

This attempt made no code changes. The implementation from the earlier builder pass is already on this branch. I re-read it against the spec and the tests on the current tree, after the merge of ae0bbfb. In attempt 3 the checks gate failed on `test_station_budgets_completeness`, an anvil.yaml comparison from wo-gh-42. That failure is gone: factory main ae0bbfb limited that check to wo-gh-42's own run, and the test passes on this tree. No other change was needed.

## Changed files (diff against ae0bbfb, outside `runs/`) and the scenario each serves

| File | Change | Scenarios |
|---|---|---|
| `anvil/sinks.py` (new) | The sink module beside the recorder. `SinkSet` calls each sink in order and turns any exception into an export error `"<type>: <ExceptionClass>"` or `"<type>: HTTP <code>"`. Each request is bounded by `timeout_seconds`. `github-issue`: activation checks; one comment found again by the `<!-- anvil-progress run_id=... -->` marker; one POST, then PATCH edits; station rows in pipeline order; scalar facts only; API base from `GITHUB_API_URL`; workflow run link. `github-project`: phase mapping; looks up the project, field, option and item over GraphQL; adds a missing item; sets the status only when the phase changes; a missing project, field or option is recorded by name and the sink goes inactive. | S1 to S7, S9 to S11, S15, S16 |
| `anvil/observe.py` | `RunRecorder` builds a `SinkSet` from `observability.sinks` and takes the pipeline order (`stations`). `state()` hands the record to the sinks before writing `state.json`, then adds `sinks` and `export_errors`. A state write happens at `run.started`. `finish()` passes `exit_status` on. `mark_crashed` hands the crashed record to the sinks, reading the config from the project's anvil.yaml. Events, the webhook and the OTLP trace are unchanged. | S1, S2, S3, S10, S11 |
| `anvil/runner.py` | One line: the recorder is built with `stations=order`. No network code. The word "retry" does not appear (count 0). | S2, S13 |
| `anvil/config.py` | `validate_sinks`, called from `load_anvil_config`. It fails loading with an error that names the offending `observability.sinks[i]` entry and key. A `token_env` that would reach a station is refused. `build_default_config` enables `github-issue`; the scaffold uses this through `render_anvil_yaml`, so `anvil/scaffold.py` needed no change. | S8, S12 |
| `anvil.yaml` | `observability.sinks: [{"type": "github-issue"}]`. | S12 |
| `docs/OPERATIONS.md`, `docs/EXECUTION.md`, `README.md` ("Watching a run"), `CHANGELOG.md`, `brain/decisions/0015-live-progress-sinks.md` | Documentation. The `github-project` sink is documented and ships off. | S12, S14 |
| `tests/test_live_progress_sinks.py`, `tests/test_live_progress_project_sink.py` (new, from test-writer) | Regression tests with a local HTTP collector. | R6 |

The `status/*` and `work_orders/wo-gh-47.json` diffs come from the line's own run commits (0871de5, 77151ca), not from the builder.

## Verification (run on the final tree)

New test files added: `tests/test_live_progress_sinks.py` and `tests/test_live_progress_project_sink.py`.

- `ANVIL_WORK_ORDER_ID=wo-gh-47 python -m unittest tests/test_live_progress_sinks.py tests/test_live_progress_project_sink.py`: `Ran 30 tests in 19.049s`, `OK`. This includes S13 and S14, which skip for other orders.
- Project check `python -m unittest discover -s tests -p 'test_*.py'`, run with `GITHUB_ACTOR`, `GITHUB_TRIGGERING_ACTOR` and the station `ANVIL_*` variables unset (the checks gate environment): `Ran 832 tests in 107.593s`, `OK (skipped=14)`. **Full factory test count: 832** (802 at the base ref plus the 30 new tests).
- Same command in this builder's raw station environment: `Ran 832 tests in 106.310s`, `FAILED (failures=6, errors=1, skipped=14)`. The 7 failing tests are 3 in `test_autonomous_line.TestHumanGate`, 2 in `test_governed_delivery.TestApprovalPolicy` and 2 in `test_token_efficiency.WrapperEvidenceTests`. This order did not cause them: I ran the same three modules on `git archive ae0bbfb` in the same environment and got the same failures (`FAILED (failures=3)`, `FAILED (failures=2)`, `FAILED (failures=1, errors=1)`). With those variables unset, all of them pass.
- Run by hand:
  - `render_issue_comment` on a running record shows done, running and pending rows, the attempt, tokens, loopbacks, cost and the workflow link.
  - On a finished `runtime_refused` record it shows the verdict and exit status verbatim and "not run" for stations that never ran.
  - `validate_sinks` rejects an unknown type with `observability.sinks[1]: type 'nope' is unknown ...` and a project sink without a number with `observability.sinks[0]: type github-project requires key 'number'`.
  - `load_anvil_config('anvil.yaml')` returns `{'sinks': [{'type': 'github-issue'}]}`.
- Guardrails, checked against the diff from ae0bbfb:
  - No file was touched under `.github/workflows`, under `pipelines/`, in `anvil.json` or `tools/line_comment.py`, and no existing test file.
  - No added line contains an em dash or en dash.
  - Standard library only.

## Open or unverified

- No sink has been run against real GitHub. Everything is verified against the local collector only. The first live check will be this factory's next run, where the issue comment should appear.
- The `github-project` sink cannot run in the factory until a workflow supplies a Projects-capable token in `token_env`, and this order forbids workflow changes. It ships documented and off.
- S13 reads the "no urllib in runner.py" rule as a ban on network calls: `urllib.request`, `urlopen`, `http.client` and `socket`. The base ref already imports `urllib.parse.urlparse` in the runner. A reviewer should confirm this reading.
- The sinks have no retry. When the API cannot be reached, each state write can wait up to `timeout_seconds`, 5 by default.
- If someone runs the suite locally with `GH_TOKEN` and `GITHUB_REPOSITORY` exported, the existing tests that scaffold `wo-gh-<n>` projects could post to real issues. CI and the checks step do not carry `GH_TOKEN`.
{"model": "claude-opus-5-5"}
