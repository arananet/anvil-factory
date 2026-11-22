# Observer: wo-gh-47 (live-progress-sinks)

Run id: 147148f794d445c4b597085f6b2b38a6. Base ref in report.json: ae0bbfb2af95b41d96d8e2af7c9f8b787f54d83b.
Observed on 2026-11-22 from the run branch anvil/wo-gh-47 in the run worktree.

## Verdict of this station: nothing to observe (release record missing)

The input of this station is the release record. None exists:

- `runs/wo-gh-47/deployer.packet.md` exists; `deployer.output.md` does not.
- state.json and events.jsonl show the deployer finished with status `packet_ready` (duration 0.918 ms), meaning no deployer work ran.
- report.json: `deployment_status` is `null`.

The work order says nothing in this order merges, publishes or deploys, and that the run stops at the owner human gate. So no release happened, and there is no released change to watch. To give an observation of a released change, this station needs a deployer release record (what was released, where, at which commit). That record can only exist after the owner merges the run branch.

## What actually happened in the run (facts from the run artifacts)

| Station | Status | Attempt |
|---|---|---|
| intake, spec-writer, test-writer, builder | executed | 1 |
| checks-gate | passed | 1 |
| loopback | loopback (completeness: "builder changed no file") | 1 |
| builder | executed | 2 |
| checks-gate | passed (completeness passed) | 2 |
| reviewer-spec, -security, -tests, -architecture, -design | executed, all verdict pass | 2 |
| reviewer-ux | routed_out | 2 |
| approver | completed ("All counted reviews passed. (Expected 5 reviews after routing.)") | 2 |
| triage-human | completed | 2 |
| deployer | packet_ready | 2 |

- Verdict `approved`, loopbacks 1 of max 2, 3657038 measured tokens over 10 measured calls, 0 unmeasured, `export_errors` empty, elapsed about 1723 s.
- state.json still reads `state: running`, `current_station: observer` (written before this station, as R1 requires).

## Discrepancies for the owner gate

1. **Human gate vs work order.** The work order says the run stops at the owner human gate. In the run, `triage-human` is `completed` in 0.028 ms, and report.json has `human_required: false`. Then the line went on to deployer and observer. No deploy happened (deployer only `packet_ready`), but the stop at the human gate that the work order describes is not what the record shows. The owner should confirm this is the intended gate behavior for an `approved` verdict.
2. **Uncommitted delta.** The working tree has changes that are not committed on the run branch: `anvil/sinks.py` (closes the HTTPError response before re-raising), `CHANGELOG.md` (one line plus the test list), and the untracked file `tests/test_live_progress_sink_errors.py`. CHANGELOG names that test file, so the committed branch alone would be inconsistent until these files are committed with the run.
3. **Committed delta against base includes `status/` files** (status/index.html, status/usage.json, status/projects/*). These are outside the authorized surface of the order. Commits 0871de5 and 77151ca (earlier ANVIL runs of this order) wrote them; they look like line-generated status output, not builder work. The owner should confirm they are expected in the merge.
4. **Suite in this environment.** `python -m unittest discover -s tests -p 'test_*.py'` here: Ran 833 tests, FAILED (failures=6, errors=1, skipped=14). The 7 are in test_autonomous_line (TestHumanGate x3), test_governed_delivery (TestApprovalPolicy x2) and test_token_efficiency (WrapperEvidenceTests x2). The same 7 fail the same way at base ae0bbfb in a clean worktree (for example: "--by ana does not match the authenticated GitHub actor"). So they come from the station environment (GitHub actor and ANVIL_* variables set) and not from this change. The checks-gate run of the line reported exit code 0.

## Checked and consistent

- R4: the factory anvil.yaml carries the sink entry. The scaffold enables `github-issue` through `anvil.config.render_anvil_yaml` (anvil/config.py:283), which `anvil/scaffold.py:57` uses. README has the short "watching a run" section.
- anvil/runner.py: 2 changed lines against base.
- New test files: tests/test_live_progress_sinks.py, tests/test_live_progress_project_sink.py (committed), tests/test_live_progress_sink_errors.py (uncommitted).

## Missing input

- A deployer release record. It cannot exist for this order before the owner merges. Re-run the observer after a real release to observe the released change (for example, a later run whose issue gets the live progress comment).
{"model": "claude-opus-5-5"}
