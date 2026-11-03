# Checks Gate: pre-review
Basis: builder_delta
Attempt: 1

# Protected Path Additions (Observed, Not Violations)
Protected path addition (observed): tests/__pycache__/test_gates.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_content.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_greenfield.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_execution.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_checks_gate.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_onboard.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_anvil.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_supervisor.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_review_producer.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_community.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/test_intake_outcomes_map.md (matches tests/)
Protected path addition (observed): tests/__pycache__/test_intake_outcomes.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_design.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_review_parsing_integrity.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/test_intake_outcomes.py (matches tests/)
Protected path addition (observed): tests/__pycache__/test_decision.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_statuspage.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_brain.cpython-312.pyc (matches tests/)

# Check Commands
## Command 1: python -m unittest discover -s tests -p 'test_*.py'
Exit code: 0
Output:
```
ult branch name
hint: will change to "main" in Git 3.0. To configure the initial branch name
hint: to use in all of your new repositories, which will suppress this warning,
hint: call:
hint:
hint: 	git config --global init.defaultBranch <name>
hint:
hint: Names commonly chosen instead of 'master' are 'main', 'trunk' and
hint: 'development'. The just-created branch can be renamed via this command:
hint:
hint: 	git branch -m <name>
hint:
hint: Disable this message with "git config set advice.defaultBranchName false"
Switched to a new branch 'work-branch'
.hint: Using 'master' as the name for the initial branch. This default branch name
hint: will change to "main" in Git 3.0. To configure the initial branch name
hint: to use in all of your new repositories, which will suppress this warning,
hint: call:
hint:
hint: 	git config --global init.defaultBranch <name>
hint:
hint: Names commonly chosen instead of 'master' are 'main', 'trunk' and
hint: 'development'. The just-created branch can be renamed via this command:
hint:
hint: 	git branch -m <name>
hint:
hint: Disable this message with "git config set advice.defaultBranchName false"
Switched to a new branch 'work-branch'
...................................................../opt/hostedtoolcache/Python/3.12.15/x64/lib/python3.12/unittest/case.py:589: ResourceWarning: unclosed <socket.socket fd=3, family=2, type=1, proto=0, laddr=('127.0.0.1', 40163)>
  if method() is not None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
.../opt/hostedtoolcache/Python/3.12.15/x64/lib/python3.12/unittest/case.py:589: ResourceWarning: unclosed <socket.socket fd=3, family=2, type=1, proto=0, laddr=('127.0.0.1', 35805)>
  if method() is not None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
.................................................................................................
----------------------------------------------------------------------
Ran 192 tests in 8.480s

OK

```
