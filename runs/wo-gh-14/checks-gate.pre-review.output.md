# Checks Gate: pre-review
Basis: builder_delta
Attempt: 1

# Protected Path Additions (Observed, Not Violations)
Protected path addition (observed): tests/__pycache__/test_intake_outcomes.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_rendered_design_review.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_review_producer.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_risk_routing.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/test_runner_health_integration.py (matches tests/)
Protected path addition (observed): tests/__pycache__/test_cost_measurement.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_execution.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_design.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_content.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_review_parsing_integrity.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_lifecycle_board_links_contrast.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_design_knowledge.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_checks_gate.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_greenfield.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_statuspage.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_brain.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_lifecycle_stages.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_gates.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_supervisor.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_onboard.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_decision.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_community.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_reviewer_ux.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_anvil.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_runner_health_integration.cpython-312.pyc (matches tests/)

# Check Commands
## Command 1: python -m unittest discover -s tests -p 'test_*.py'
Exit code: 1
Output:
```
 method() is not None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
.....................................................................................................E.............................................................................................s......................................................
======================================================================
ERROR: test_exception_sanitization_prevents_credential_leakage (test_post_deploy_health.TestSecurityHardeningS6.test_exception_sanitization_prevents_credential_leakage)
Exception sanitization prevents internal topology or credential details from leaking
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/anvil-factory/anvil-factory/tests/test_post_deploy_health.py", line 739, in test_exception_sanitization_prevents_credential_leakage
    with patch('requests.get') as mock_get:
         ^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.12.15/x64/lib/python3.12/unittest/mock.py", line 1451, in __enter__
    self.target = self.getter()
                  ^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.12.15/x64/lib/python3.12/pkgutil.py", line 513, in resolve_name
    mod = importlib.import_module(modname)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.12.15/x64/lib/python3.12/importlib/__init__.py", line 90, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1324, in _find_and_load_unlocked
ModuleNotFoundError: No module named 'requests'

----------------------------------------------------------------------
Ran 387 tests in 31.312s

FAILED (errors=1, skipped=1)

```
