# Live Progress Sinks: a Run Seen While It Runs, on GitHub First

Status: proposed
Slug: live-progress-sinks

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose

A run of the line cannot be watched. The record is now complete at every moment (state.json is rewritten before every station, report.json is checkpointed after every station since wo-gh-41), but both live on the disk of the machine that runs the line and reach the repository only when the run ends. The five runs of wo-gh-41 on 2026-11-20 and the run of wo-gh-42 on 2026-11-21 each ran between 5 and 27 minutes during which the only visible fact was "In progress"; the owner asked "why is it taking so long, what is it doing" and the honest answer was that nobody could tell from outside.

The export that exists (observability.events_url, observability.otlp_endpoint) needs a receiver someone has to build and host. The owner's direction of 2026-11-21 is that the factory must not depend on one vendor for this and that a person who copies ANVIL should see their runs without standing anything up. Every ANVIL work order is already a GitHub issue and every run already has a token that can write to it.

This order adds progress sinks: destinations that receive the run state each time it changes. Two ship with the factory. The first keeps one comment on the work order's issue up to date, station by station, and needs no setup. The second, optional, moves the issue's card across the columns of a GitHub Projects board. The sink list is configuration: nothing about GitHub lives in the runner, and a third sink is one small class.

## Requirements

### R1. Sinks receive the run state
- anvil.yaml accepts observability.sinks: an ordered list of sink entries, each an object with a type and that type's own keys. Loading validates the list: an unknown type, a missing required key or a malformed entry fails loading and names the entry.
- A sink is called with the run state record (the schema anvil/run-state@1 that state.json holds) every time the recorder rewrites the state: when the run starts, before each station, after the last one, and when the run ends, crashes or is stopped early. No new event kind is added and events.jsonl is unchanged.
- A sink never decides a run. A sink that raises, times out or is refused is recorded in the state's export_errors under its type, once per distinct failure, and the line goes on. Each call is bounded by observability.timeout_seconds.
- With no sinks configured the run makes no additional network call and behaves exactly as before.
- The sink code lives outside anvil/runner.py, beside the recorder.

### R2. The github-issue sink
- Entry: {"type": "github-issue"} with optional token_env (default GH_TOKEN). It is active for a run only when the work order id has the form wo-gh-<number>, the environment names a repository (GITHUB_REPOSITORY) and the token variable is set. When any of these is missing the sink is inactive for that run and records why once, without a network call.
- On its first call it creates one comment on issue <number>. On every later call it edits that same comment in place; a run never leaves more than one progress comment. The comment carries a hidden marker with the run id so a resumed run of the same run id finds and continues its own comment.
- The comment shows: the work order id and pipeline; the run's state (running, finished, crashed, stopped) and, once known, the verdict and exit status; one row per pipeline station in pipeline order with its status (done, failed, running, pending, skipped, not run), attempt number and measured tokens; the loopbacks used; measured tokens and the priced cost so far where the cost section has one; the time of the last update; and a link to the workflow run when the environment provides one.
- The comment carries scalar facts only, the same rule the events follow: no prompt, no station output, no file path, no token value.
- The GitHub API base comes from GITHUB_API_URL when set, so the sink works on GitHub Enterprise Server.

### R3. The github-project sink
- Entry: {"type": "github-project", "owner": ..., "number": ...} with optional owner_type (user or organization, default user), status_field (default Status), token_env (default GH_TOKEN) and columns, a map from phase to the name of an option of the status field.
- Phases and their default option names: intake (Intake), spec (Spec), build (Build: the test-writer and builder stations), checks (Checks), review (Review: every reviewer station and the approver), human (Needs human), done (Done), failed (Failed). A station outside the default pipeline maps to build unless the entry's columns names it.
- On each call the sink sets the status of the issue's item in the project to the option for the current phase, adding the issue to the project when it is not there. It changes the status only when the phase changed since its last call.
- The sink never alters the project's shape. A project, field or option it cannot find is recorded as an export error naming what is missing, and the sink goes inactive for the rest of the run.
- The token of a workflow run cannot reach Projects; the entry's token_env names a variable holding a token that can. When that variable is unset the sink is inactive and says so once.

### R4. What ships enabled
- The factory's own anvil.yaml enables the github-issue sink. The github-project sink ships documented and off.
- The scaffold for new projects enables the github-issue sink, so a project created from ANVIL shows its runs on its issues with no further setup.
- The final "ANVIL line report" comment the workflow posts is unchanged.

### R5. Tokens stay where they are
- Sinks run in the line process and read their token from its environment. Stations never receive it: the reduced environment a station gets is unchanged.
- No token value appears in state.json, events.jsonl, report.json, a comment or an export error.

### R6. Regression tests
- New test files under tests/, using a local HTTP collector in the manner of tests/test_governed_delivery.py: (a) a scripted run with the github-issue sink makes exactly one comment creation and then only edits of that comment, and the last edit shows every station done and the verdict; (b) mid-run, the edit sent before the builder shows the builder running and later stations pending; (c) a collector that answers 500, and one that is unreachable, leave the verdict and the report unchanged and one export error on record; (d) a work order whose id is not wo-gh-<number>, or a missing token, produces zero network calls and one recorded reason; (e) the github-project sink sends a status change when the phase changes and none when it does not, adds a missing item, and goes inactive naming a missing option; (f) no sink configured produces zero additional network calls; (g) a malformed sinks list fails loading naming the entry; (h) a token value placed in the environment appears in no file the run writes and in no request body.

### Guardrails
- Python standard library only (urllib), consistent with the factory spine. No new dependency.
- Authorized surface: anvil/observe.py, a new module beside it for the sinks, anvil/config.py (validation of observability.sinks), anvil/scaffold.py (the default for new projects), anvil.yaml (the factory's own sink entry), docs/OPERATIONS.md, docs/EXECUTION.md, README.md (one short section on watching a run), CHANGELOG.md, one new decision record under brain/decisions/, and new test files under tests/. anvil/runner.py may change only where the recorder is constructed or told the pipeline order, and gains no network code.
- Not touched: every file under .github/workflows (the run's own token cannot push workflow changes, and none are needed: the line step already carries GH_TOKEN); pipeline files under pipelines/ and anvil.json (protected paths).
- Frozen: the events contract (kinds, fields, order, the webhook and its bearer token), the OTLP trace, the run-state schema's existing fields (additions are allowed), the rule that export never decides a run, the station environment reduction, tools/line_comment.py and the final report comment.
- Known constraints from existing tests, stated here so the line does not discover them: tests/test_governed_delivery.py asserts that the events POSTed to the webhook equal the events in events.jsonl and counts station.finished and loopback events against the report's steps, so sinks must not add, remove or reorder events; tests/test_review_producer.py asserts that the word "retry" does not occur in anvil/runner.py; tests/test_continuous_run_accounting.py asserts the report's shape after every exit path.
- Existing test files at the base ref are not modified or deleted; new tests arrive as new files.
- No em dash or en dash character in any produced file (project style rule).
- Nothing in this order merges, publishes or deploys anything; the run stops at the owner human gate.

## Scenarios

### Scenario: The issue shows the run from start to end
- S1: Given a work order wo-gh-<number> and the github-issue sink, when the line runs, then the issue receives one progress comment at the start, the same comment is edited as each station begins and ends, and at the end it shows every station's outcome, the verdict and the exit status.

### Scenario: A run in flight names its current station
- S2: Given a run in flight, when the builder is about to start, then the comment shows the builder as running, earlier stations with their outcome and later stations as pending.

### Scenario: A failing sink never decides a run
- S3: Given a GitHub API that fails or cannot be reached, when the line runs, then the verdict, the report and the events are what they would have been without the sink, and export_errors names the sink once.

### Scenario: An order that is not an issue makes no call
- S4: Given a work order that is not a GitHub issue, or no token in the environment, when the line runs, then the sink makes no network call and its reason is on record once.

### Scenario: The board follows the phases
- S5: Given the github-project sink and a board whose status field has the default options, when the run moves from spec to build to review, then the issue's card is set to each column once, in that order, and is set to Done or Failed at the end.

### Scenario: A board that lacks a column is reported, not altered
- S6: Given a board that lacks one of the options, when the sink needs it, then the run records which option is missing, the sink stops for that run and the run's outcome is unchanged.

### Scenario: No sink, no new network call
- S7: Given a project with no observability.sinks, when the line runs, then it makes no network call it did not make before this change.

### Scenario: The token appears nowhere
- S8: Given a token in the line's environment, when a run finishes, then the token value is in no file under runs/ and in no comment body.

### Scenario: New projects watch their runs by default
- S9: Given a project created with anvil init after this change, when its configuration is read, then the github-issue sink is enabled.
