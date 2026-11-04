# Checks Gate: pre-review
Basis: builder_delta
Attempt: 1

# Protected Path Violations
Protected path violation: pipelines/sdlc-default.json (base ref file modified/deleted, matches pipelines/)
Protected path violation: pipelines/content-default.json (base ref file modified/deleted, matches pipelines/)
Protected path violation: pipelines/content-short.json (base ref file modified/deleted, matches pipelines/)

# Check Commands
## Command 1: python -m unittest discover -s tests -p 'test_*.py'
Exit code: 1
Output:
```
est_supervisor.TestSuperviseFlow.test_reordered_reviewers_still_accepted_s4)
bounded-supervisor S4: reordering reviewers keeps the set, so the proposal is valid
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/anvil-factory/anvil-factory/tests/test_supervisor.py", line 218, in test_reordered_reviewers_still_accepted_s4
    self.assertEqual(result["action"], "accepted")
AssertionError: 'rejected' != 'accepted'
- rejected
+ accepted


======================================================================
FAIL: test_second_execute_reads_the_new_output_not_a_stale_one (test_supervisor.TestSuperviseFlow.test_second_execute_reads_the_new_output_not_a_stale_one)
bounded-supervisor S4 and S5: repeated supervise runs judge the latest runtime output
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/anvil-factory/anvil-factory/tests/test_supervisor.py", line 193, in test_second_execute_reads_the_new_output_not_a_stale_one
    self.assertEqual(first["action"], "accepted")
AssertionError: 'rejected' != 'accepted'
- rejected
+ accepted


======================================================================
FAIL: test_valid_proposal_accepted_and_not_applied_s4 (test_supervisor.TestSuperviseFlow.test_valid_proposal_accepted_and_not_applied_s4)
bounded-supervisor S4: a catalog only, constitution passing proposal is filed, never applied
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/anvil-factory/anvil-factory/tests/test_supervisor.py", line 176, in test_valid_proposal_accepted_and_not_applied_s4
    self.assertEqual(result["action"], "accepted")
AssertionError: 'rejected' != 'accepted'
- rejected
+ accepted


----------------------------------------------------------------------
Ran 319 tests in 28.604s

FAILED (failures=10, skipped=1)

```
