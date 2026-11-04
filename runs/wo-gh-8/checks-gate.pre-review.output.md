# Checks Gate: pre-review
Basis: builder_delta
Attempt: 1

# Check Commands
## Command 1: python -m unittest discover -s tests -p 'test_*.py'
Exit code: 1
Output:
```
 "git config set advice.defaultBranchName false"
Switched to a new branch 'work-branch'
...................................................../opt/hostedtoolcache/Python/3.12.15/x64/lib/python3.12/unittest/case.py:589: ResourceWarning: unclosed <socket.socket fd=3, family=2, type=1, proto=0, laddr=('127.0.0.1', 33355)>
  if method() is not None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
.../opt/hostedtoolcache/Python/3.12.15/x64/lib/python3.12/unittest/case.py:589: ResourceWarning: unclosed <socket.socket fd=3, family=2, type=1, proto=0, laddr=('127.0.0.1', 41735)>
  if method() is not None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
...........................................................................................................E.s.....................................
======================================================================
ERROR: test_config_above_policy_fails_load_s4 (test_risk_routing.TestModelPolicyCeiling.test_config_above_policy_fails_load_s4)
S4: configuration assigning model above policy ceiling fails at load
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/anvil-factory/anvil-factory/tests/test_risk_routing.py", line 525, in test_config_above_policy_fails_load_s4
    config = load_routing_config(proj)
             ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/anvil-factory/anvil-factory/anvil/routing.py", line 187, in load_routing_config
    validate_model_assignment(
  File "/home/runner/work/anvil-factory/anvil-factory/anvil/routing.py", line 86, in validate_model_assignment
    raise RoutingConfigError(
anvil.routing.RoutingConfigError: Station 'reviewer' configured with model 'review-strong' exceeds policy ceiling 'review-balanced' for reviewer stations

----------------------------------------------------------------------
Ran 242 tests in 16.088s

FAILED (errors=1, skipped=1)

```
