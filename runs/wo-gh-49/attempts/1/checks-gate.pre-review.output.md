# Checks Gate: pre-review
Basis: builder_delta
Attempt: 1

# Check Commands
## Command 1: python -m unittest discover -s tests -p 'test_*.py'
Exit code: 1
Output:
```
----------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-49/tests/test_station_budgets_completeness.py", line 642, in test_s4_failing_checks_verdict_dispatches_zero_reviewers
    self.assertEqual(len(evaluations), 2)
AssertionError: 1 != 2

======================================================================
FAIL: test_s4_missing_builder_report_dispatches_zero_reviewers (test_station_budgets_completeness.CompletenessGate.test_s4_missing_builder_report_dispatches_zero_reviewers)
S4: a builder attempt with no report artifact: completeness fails naming it, loops back once, zero reviewers
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-49/tests/test_station_budgets_completeness.py", line 582, in test_s4_missing_builder_report_dispatches_zero_reviewers
    self.assertEqual(len(evaluations), 2)
AssertionError: 1 != 2

======================================================================
FAIL: test_s9_completeness_never_reruns_the_suite_or_literal_check (test_station_budgets_completeness.CompletenessGate.test_s9_completeness_never_reruns_the_suite_or_literal_check)
S9: suite runs equal the red check plus gate runs, and builder report validation runs once per attempt
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-49/tests/test_station_budgets_completeness.py", line 758, in test_s9_completeness_never_reruns_the_suite_or_literal_check
    self.assertEqual(len(seen), runtime.count("builder"),
AssertionError: 1 != 2 : the builder report literal validation ran more than once per attempt

----------------------------------------------------------------------
Ran 862 tests in 92.026s

FAILED (failures=10, skipped=14)

```

## Gate practices

Gate enforced practices this run resolved. The gate is accountable for them:

- P-1: Traversal proof for platformer orders
- P-2: Deterministic validation of builder reports with declared literals
- P-3: Capture evidence must exist before design review

## Artifact validation

- builder report: /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-49/runs/wo-gh-49/builder.output.md
- observed: present
- report source: station
- required literals declared: 0
- result: pass
