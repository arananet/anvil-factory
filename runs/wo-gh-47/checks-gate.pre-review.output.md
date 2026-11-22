# Checks Gate: pre-review
Basis: builder_delta
Attempt: 3

# Check Commands
## Command 1: python -m unittest discover -s tests -p 'test_*.py'
Exit code: 1
Output:
```
rceWarning: Enable tracemalloc to get the object allocation traceback
.../opt/hostedtoolcache/Python/3.12.16/x64/lib/python3.12/unittest/case.py:589: ResourceWarning: unclosed <socket.socket fd=3, family=2, type=1, proto=0, laddr=('127.0.0.1', 44287)>
  if method() is not None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
....................................................................................s..................................................................ss.........................................................................................................................................................s......s......................................................................................................s.................................................................F........ss.sss...........................................................................................
======================================================================
FAIL: test_s3_factory_other_keys_and_packet_budgets_unchanged (test_station_budgets_completeness.PartitionConfiguration.test_s3_factory_other_keys_and_packet_budgets_unchanged)
S3 and guardrails: only the two efficiency keys are new; the packet budget lookup is unaffected
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-47/tests/test_station_budgets_completeness.py", line 358, in test_s3_factory_other_keys_and_packet_budgets_unchanged
    self.assertEqual(stripped, base)
AssertionError: {'ver[474 chars]0}, 'observability': {'sinks': [{'type': 'gith[2495 chars][]}}} != {'ver[474 chars]0}, 'stations': {'intake': {'context': ['brain[2439 chars][]}}}
Diff is 5413 characters long. Set self.maxDiff to None to see it.

----------------------------------------------------------------------
Ran 832 tests in 100.789s

FAILED (failures=1, skipped=11)

```

## Gate practices

Gate enforced practices this run resolved. The gate is accountable for them:

- P-1: Traversal proof for platformer orders
- P-2: Deterministic validation of builder reports with declared literals
- P-3: Capture evidence must exist before design review

## Artifact validation

- builder report: /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-47/runs/wo-gh-47/builder.output.md
- observed: present
- report source: station
- required literals declared: 0
- result: pass
