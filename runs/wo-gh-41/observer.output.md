# Observer report: wo-gh-41 (continuous-run-accounting)

Run observed: f5ea98411b994563a8e4ccf1f6851b4b, pipeline sdlc-default, branch anvil/wo-gh-41.

## Release record: missing

There was no release to watch. The deployer station ended with status `packet_ready`
(runs/wo-gh-41/envelopes/deployer.envelope.json, events.jsonl `station.finished` deployer).
It wrote only runs/wo-gh-41/deployer.packet.md. There is no deployer output, no release
record and no deployment status for this run. That matches the work order guardrail:
"Nothing in this order merges, publishes or deploys anything; the run stops at the owner
human gate." So I have no post-release behavior to report. A real observation needs a
release record from the deployer once the owner approves at the gate.

## What I could verify (pre-release state of the branch)

- Upstream outcome for this run (state.json): checks-gate passed, five reviewers executed
  and all returned `pass` (spec 9 findings, security 6, tests 8, architecture 9, design 0),
  reviewer-ux routed out, approver completed with verdict `approved`, triage-human completed.
- Change on the branch vs main: anvil/runner.py, anvil/line.py, tools/line_comment.py,
  docs/EXECUTION.md, CHANGELOG.md, brain/decisions/0013-continuous-run-accounting.md and the new
  file tests/test_continuous_run_accounting.py. All of these are inside the authorized surface.
  Nothing under pipelines/ and no change to anvil.json relative to the merge base with main.
- Focused check I re-ran: `python -m unittest tests.test_continuous_run_accounting` ran 19 tests, OK.
  The checks gate recorded the full suite at 760 tests, OK (skipped=6)
  (runs/wo-gh-41/checks-gate.pre-review.output.md).
- No em dash or en dash characters in the produced files I checked (runner.py, EXECUTION.md,
  CHANGELOG.md, decision 0013, the new test file, builder report).
- Working tree is not committed yet: the spec, the new test file and run artifacts show as modified.

## Observation on the feature in this run

The process that ran this order did not use the new checkpointing. runs/wo-gh-41/report.json
on disk still belongs to the previous run 51d802ce7e4740e4a38bd90cb02ba1f0 (verdict `no_reviews`,
no `checkpoint` fields). The current run has completed 14 stations and it has not checkpointed
report.json once. I expected this. The runner that runs a work order comes from the factory
base, not from the branch under change. So R1 and R2 have not been seen working in a real run yet.
Only the scripted tests cover them so far. History preservation (R3) can be seen in its existing
form: runs/wo-gh-41/history/ holds four earlier records of this order, including a
`budget_exceeded` run (6fc43cc391534641a9fdf48ab5053bab).

## To watch after release

1. The first factory run after merge writes report.json with checkpoint fields after each station.
   A mid-run read of it parses.
2. A budget death, timeout or SIGTERM leaves a completed record with exit status and reason, and
   line_comment.py and the swimlane render it with no station executing.
3. The rerun of a killed order keeps the killed record in runs/<id>/history/.

## Missing inputs

- Release record (deployer output). It does not exist because the run stops at the owner gate.
{"model": "claude-opus-5-5"}
