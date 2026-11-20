# Checks Gate: pre-review
Basis: builder_delta
Attempt: 1

# Protected Path Additions (Observed, Not Violations)
Protected path addition (observed): tests/test_continuous_run_accounting.py (matches tests/)

# Check Commands
## Command 1: python -m unittest discover -s tests -p 'test_*.py'
Exit code: 1
Output:
```
ch'
...................................................................................................................................................../opt/hostedtoolcache/Python/3.12.16/x64/lib/python3.12/unittest/case.py:589: ResourceWarning: unclosed <socket.socket fd=3, family=2, type=1, proto=0, laddr=('127.0.0.1', 39691)>
  if method() is not None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
.../opt/hostedtoolcache/Python/3.12.16/x64/lib/python3.12/unittest/case.py:589: ResourceWarning: unclosed <socket.socket fd=3, family=2, type=1, proto=0, laddr=('127.0.0.1', 37543)>
  if method() is not None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
.......................F............................................................s....................................ss.........................................................................................................................................................s......s......................................................................................................s.................................................................................................................................
======================================================================
FAIL: test_crash_and_stall_are_visible_s1 (test_governed_delivery.TestLiveState.test_crash_and_stall_are_visible_s1)
S1: a run that raises is crashed, not running; an abandoned one is stalled
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-41/tests/test_governed_delivery.py", line 113, in test_crash_and_stall_are_visible_s1
    self.assertFalse((h.proj / "runs/wo-crash/report.json").exists())
AssertionError: True is not false

----------------------------------------------------------------------
Ran 760 tests in 84.191s

FAILED (failures=1, skipped=6)

```

## Gate practices

Gate enforced practices this run resolved. The gate is accountable for them:

- P-1: Traversal proof for platformer orders
- P-2: Deterministic validation of builder reports with declared literals
- P-3: Capture evidence must exist before design review

## Artifact validation

- builder report: /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-41/runs/wo-gh-41/builder.output.md
- observed: present
- report source: station
- required literals declared: 0
- result: pass
