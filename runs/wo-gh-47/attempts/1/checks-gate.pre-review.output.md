# Checks Gate: pre-review
Basis: builder_delta
Attempt: 1

# Check Commands
## Command 1: python -m unittest discover -s tests -p 'test_*.py'
Exit code: 1
Output:
```
........................................................s.................................................................F........ss.sss...........................................................................................
======================================================================
FAIL: test_s3_http_500_changes_nothing_but_one_export_error (test_live_progress_sinks.SinkFailures.test_s3_http_500_changes_nothing_but_one_export_error)
S3 (test c): an API answering 500 leaves verdict, report and events as without the sink
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-47/tests/test_live_progress_sinks.py", line 434, in test_s3_http_500_changes_nothing_but_one_export_error
    self.assertEqual(with_sink[key], base_a[key], key)
AssertionError: 0.013 != 0.012 : /steps[12]/duration_ms

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
Ran 832 tests in 105.187s

FAILED (failures=2, skipped=11)

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
