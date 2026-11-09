# Checks Gate: pre-review
Basis: builder_delta
Attempt: 1

# Protected Path Additions (Observed, Not Violations)
Protected path addition (observed): tests/__pycache__/test_render_crash_tolerance_s2.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_tier_map_totality.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_render_crash_tolerance_s5.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_onboard.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_station_artifact_wrappers.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_design_knowledge.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_anvil.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_supervisor.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_review_parsing_integrity.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_readme_showcase.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_model_migration_supervisor_handoff.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_codex_agentic.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_intake_outcomes.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_render_crash_tolerance_s3.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_astra_consumption.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_codex_reviewer_guard.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_gates.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_content.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_model_migration_loopback.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_decision.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_station_artifact_contract.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_rendered_design_review.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_cost_measurement.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_quality_final_loopback.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_execution.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_review_producer.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_model_migration_tiers.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_quality_same_subject.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_landing_page.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_community.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_model_migration_round4.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_runner_health_integration.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_render_crash_tolerance_s4.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_brain.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_lifecycle_board_links_contrast.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_greenfield.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_reviewer_ux.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_model_migration.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_statuspage.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_quality_wiring.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_quality_standard.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_post_deploy_health.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_render_crash_tolerance_s1.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_design.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_lifecycle_stages.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_risk_routing.cpython-312.pyc (matches tests/)

# Check Commands
## Command 1: python -m unittest discover -s tests -p 'test_*.py'
Exit code: 1
Output:
```
nch'
.............................................................................................................../opt/hostedtoolcache/Python/3.12.16/x64/lib/python3.12/unittest/case.py:589: ResourceWarning: unclosed <socket.socket fd=3, family=2, type=1, proto=0, laddr=('127.0.0.1', 44281)>
  if method() is not None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
.../opt/hostedtoolcache/Python/3.12.16/x64/lib/python3.12/unittest/case.py:589: ResourceWarning: unclosed <socket.socket fd=3, family=2, type=1, proto=0, laddr=('127.0.0.1', 41049)>
  if method() is not None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
...........................................................s.........s....................................ss.........................................................................................................F......................................................s......s......s......................................................................................................s..........................................................................
======================================================================
FAIL: test_no_base_changes_nothing_but_the_report_field_s8 (test_practice_skills.TestRunnerIntegration.test_no_base_changes_nothing_but_the_report_field_s8)
practice-skills S8: with no practices base, packets carry no Practices section and the report records an empty resolution
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/anvil-factory/anvil-factory/tests/test_practice_skills.py", line 441, in test_no_base_changes_nothing_but_the_report_field_s8
    self.assertEqual(report["verdict"], "approved")
AssertionError: 'no_reviews' != 'approved'
- no_reviews
+ approved


----------------------------------------------------------------------
Ran 649 tests in 125.535s

FAILED (failures=1, skipped=8)

```

## Artifact validation

- builder report: runs/wo-gh-36/builder.output.md
- observed: present
- report source: station
- required literals declared: 0
- result: pass
