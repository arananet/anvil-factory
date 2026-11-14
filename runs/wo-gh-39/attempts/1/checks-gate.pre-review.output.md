# Checks Gate: pre-review
Basis: builder_delta
Attempt: 1

# Protected Path Additions (Observed, Not Violations)
Protected path addition (observed): tests/test_station_timeout.py (matches tests/)

# Check Commands
## Command 1: python -m unittest discover -s tests -p 'test_*.py'
Exit code: 1
Output:
```
ing stops at the human gate in execute mode
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-39/tests/test_autonomous_line.py", line 283, in test_publisher_held_until_approved_s5
    self.assertEqual(h.cli("approve", h.proj, "wo-s5", "--by", "ana")[0], 0)
AssertionError: 1 != 0

======================================================================
FAIL: test_identity_and_policy_s5 (test_governed_delivery.TestApprovalPolicy.test_identity_and_policy_s5)
S5: verified identity inside Actions, and the policy decides who may approve what
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-39/tests/test_governed_delivery.py", line 255, in test_identity_and_policy_s5
    self.assertIn("verified identity", err)
AssertionError: 'verified identity' not found in 'Approval refused: --by bo does not match the authenticated GitHub actor arananet\n'

======================================================================
FAIL: test_policy_comes_from_the_operator_checkout_s5 (test_governed_delivery.TestApprovalPolicy.test_policy_comes_from_the_operator_checkout_s5)
S5: a policy edited inside the run's worktree does not apply
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-39/tests/test_governed_delivery.py", line 291, in test_policy_comes_from_the_operator_checkout_s5
    self.assertIn("not in the approvers list", err)
AssertionError: 'not in the approvers list' not found in 'Approval refused: --by mallory does not match the authenticated GitHub actor arananet\n'

----------------------------------------------------------------------
Ran 729 tests in 54.943s

FAILED (failures=5, skipped=6)

```

## Gate practices

Gate enforced practices this run resolved. The gate is accountable for them:

- P-1: Traversal proof for platformer orders
- P-2: Deterministic validation of builder reports with declared literals
- P-3: Capture evidence must exist before design review

## Artifact validation

- builder report: /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-39/runs/wo-gh-39/builder.output.md
- observed: missing
- report source: none
- required literals declared: 0
- result: fail
- finding: Builder report artifact /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-39/runs/wo-gh-39/builder.output.md is missing.
