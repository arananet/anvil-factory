# Checks Gate: pre-review
Basis: builder_delta
Attempt: 1

# Protected Path Additions (Observed, Not Violations)
Protected path addition (observed): tests/test_model_migration.py (matches tests/)
Protected path addition (observed): tests/__pycache__/test_model_migration.cpython-312.pyc (matches tests/)

# Check Commands
## Command 1: python -m unittest discover -s tests -p 'test_*.py'
Exit code: 1
Output:
```
t = run_pipeline(proj, hotfix_pipe(reg), wo, registry=reg, executor=executor)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/anvil-factory/anvil-factory/anvil/runner.py", line 1287, in run_pipeline
    result = executor.execute(packet_text, station_id, packet_path=packet,
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: HttpExecutor.execute() got an unexpected keyword argument 'configured_model'

======================================================================
FAIL: test_command_executor_never_guesses_a_model_s8 (test_execution.TestModelProvenance.test_command_executor_never_guesses_a_model_s8)
agent-execution S8: a command runtime's executed model is null unless the runtime reports one
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/anvil-factory/anvil-factory/tests/test_execution.py", line 416, in test_command_executor_never_guesses_a_model_s8
    self.assertIsNone(builder["executed_model"])
AssertionError: 'fast-builder' is not None

======================================================================
FAIL: test_command_executor_records_a_self_reported_model_s8 (test_execution.TestModelProvenance.test_command_executor_records_a_self_reported_model_s8)
agent-execution S8: when command output reports a model field, that model is recorded
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/anvil-factory/anvil-factory/tests/test_execution.py", line 435, in test_command_executor_records_a_self_reported_model_s8
    self.assertEqual(builder["executed_model"], "self-reported-1")
AssertionError: 'fast-builder' != 'self-reported-1'
- fast-builder
+ self-reported-1


----------------------------------------------------------------------
Ran 505 tests in 48.528s

FAILED (failures=2, errors=7, skipped=1)

```
