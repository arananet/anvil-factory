# Checks Gate: pre-review
Basis: builder_delta
Attempt: 1

# Check Commands
## Command 1: python -m unittest discover -s tests -p 'test_*.py'
Exit code: 1
Output:
```
6/x64/lib/python3.12/unittest/case.py:589: ResourceWarning: unclosed <socket.socket fd=3, family=2, type=1, proto=0, laddr=('127.0.0.1', 44215)>
  if method() is not None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
.../opt/hostedtoolcache/Python/3.12.16/x64/lib/python3.12/unittest/case.py:589: ResourceWarning: unclosed <socket.socket fd=3, family=2, type=1, proto=0, laddr=('127.0.0.1', 36117)>
  if method() is not None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
......................................................................................................................................s.....................................
======================================================================
FAIL: test_run_report_includes_cost_section (test_cost_measurement.TestCostInRunReport.test_run_report_includes_cost_section)
cost-measurement S4: run report includes cost section with coverage counts
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/anvil-factory/anvil-factory/tests/test_cost_measurement.py", line 261, in test_run_report_includes_cost_section
    self.assertEqual(cost["measured_steps"], 2)
AssertionError: 1 != 2

======================================================================
FAIL: test_gateway_response_with_usage (test_cost_measurement.TestGatewayUsageHandling.test_gateway_response_with_usage)
cost-measurement S2: HTTP gateway response with usage is priced
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/anvil-factory/anvil-factory/tests/test_cost_measurement.py", line 310, in test_gateway_response_with_usage
    self.assertIsNotNone(intake_step.get("cost"))
AssertionError: unexpectedly None

----------------------------------------------------------------------
Ran 282 tests in 29.556s

FAILED (failures=2, skipped=1)

```
