# Checks Gate: pre-review
Basis: builder_delta
Attempt: 1

# Protected Path Additions (Observed, Not Violations)
Protected path addition (observed): tests/__pycache__/test_design.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_review_producer.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_decision.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_supervisor.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_post_deploy_health.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_quality_wiring.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_anvil.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_checks_gate.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_quality_same_subject.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_reviewer_ux.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_brain.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_review_parsing_integrity.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_render_crash_tolerance_s1.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_quality_final_loopback.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_lifecycle_stages.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_content.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_greenfield.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_render_crash_tolerance_s3.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_risk_routing.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_onboard.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_render_crash_tolerance_s2.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_community.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_lifecycle_board_links_contrast.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_quality_standard.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_cost_measurement.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_gates.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_statuspage.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_rendered_design_review.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_design_knowledge.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_render_crash_tolerance_s4.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_render_crash_tolerance_s5.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_readme_showcase.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_execution.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_runner_health_integration.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_intake_outcomes.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_astra_consumption.cpython-312.pyc (matches tests/)

# Check Commands
## Command 1: python -m unittest discover -s tests -p 'test_*.py'
Exit code: 0
Output:
```
 'master' are 'main', 'trunk' and
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
.............................................................................................../opt/hostedtoolcache/Python/3.12.16/x64/lib/python3.12/unittest/case.py:589: ResourceWarning: unclosed <socket.socket fd=3, family=2, type=1, proto=0, laddr=('127.0.0.1', 40497)>
  if method() is not None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
.../opt/hostedtoolcache/Python/3.12.16/x64/lib/python3.12/unittest/case.py:589: ResourceWarning: unclosed <socket.socket fd=3, family=2, type=1, proto=0, laddr=('127.0.0.1', 34821)>
  if method() is not None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
.............................................................................................................................................................s......s......s......................................................................................................s......................................................
----------------------------------------------------------------------
Ran 502 tests in 114.035s

OK (skipped=4)

```
