# Checks Gate: pre-review
Basis: builder_delta
Attempt: 1

# Protected Path Additions (Observed, Not Violations)
Protected path addition (observed): tests/__pycache__/test_render_crash_tolerance_s3.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_reviewer_ux.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_render_crash_tolerance_s2.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_intake_outcomes.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_tier_map_totality.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_quality_standard.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_design_knowledge.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_readme_showcase.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_render_crash_tolerance_s4.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_codex_reviewer_guard.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_model_migration.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_lifecycle_board_links_contrast.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_render_crash_tolerance_s1.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_quality_same_subject.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_post_deploy_health.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_brain.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_design.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_community.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_supervisor.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_review_parsing_integrity.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_model_migration_supervisor_handoff.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_lifecycle_stages.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_model_migration_loopback.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_anvil.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_cost_measurement.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_risk_routing.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_quality_wiring.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_execution.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_model_migration_tiers.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_codex_agentic.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_onboard.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_astra_consumption.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_quality_final_loopback.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_greenfield.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_rendered_design_review.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_content.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_checks_gate.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_gates.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_review_producer.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_model_migration_round4.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_runner_health_integration.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_render_crash_tolerance_s5.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_decision.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_statuspage.cpython-312.pyc (matches tests/)

# Check Commands
## Command 1: python -m unittest discover -s tests -p 'test_*.py'
Exit code: 1
Output:
```
  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.12.16/x64/lib/python3.12/pathlib.py", line 1027, in read_text
    with self.open(mode='r', encoding=encoding, errors=errors) as f:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.12.16/x64/lib/python3.12/pathlib.py", line 1013, in open
    return io.open(self, mode, buffering, encoding, errors, newline)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: '/tmp/tmpso0ciuw2/work/render-stats.json'

======================================================================
ERROR: test_s4_persistent_failure_after_two_sweeps (test_render_crash_tolerance_s4.RenderCrashToleranceS4Tests.test_s4_persistent_failure_after_two_sweeps)
render-crash-tolerance S4: frames missing after 2 sweeps fail step, missing range named
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/anvil-factory/anvil-factory/tests/test_render_crash_tolerance_s4.py", line 97, in test_s4_persistent_failure_after_two_sweeps
    stats = json.loads((work / "render-stats.json").read_text())
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.12.16/x64/lib/python3.12/pathlib.py", line 1027, in read_text
    with self.open(mode='r', encoding=encoding, errors=errors) as f:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.12.16/x64/lib/python3.12/pathlib.py", line 1013, in open
    return io.open(self, mode, buffering, encoding, errors, newline)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: '/tmp/tmpf0nwb2u6/work/render-stats.json'

----------------------------------------------------------------------
Ran 605 tests in 105.102s

FAILED (errors=3, skipped=7)

```
