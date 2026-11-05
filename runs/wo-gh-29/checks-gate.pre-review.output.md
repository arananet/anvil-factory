# Checks Gate: pre-review
Basis: builder_delta
Attempt: 1

# Protected Path Additions (Observed, Not Violations)
Protected path addition (observed): tests/__pycache__/test_design_knowledge.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_render_crash_tolerance_s2.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_intake_outcomes.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_risk_routing.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_content.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_review_producer.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_rendered_design_review.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_runner_health_integration.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_quality_wiring.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_lifecycle_board_links_contrast.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/test_model_migration_supervisor_handoff.py (matches tests/)
Protected path addition (observed): tests/__pycache__/test_review_parsing_integrity.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_render_crash_tolerance_s5.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_quality_standard.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_render_crash_tolerance_s3.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_greenfield.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_onboard.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_gates.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_model_migration_supervisor_handoff.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_post_deploy_health.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_decision.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_model_migration_tiers.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_render_crash_tolerance_s4.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_anvil.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_brain.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_reviewer_ux.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_execution.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_statuspage.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_supervisor.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_design.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_render_crash_tolerance_s1.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_checks_gate.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_quality_same_subject.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_cost_measurement.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_astra_consumption.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_lifecycle_stages.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_model_migration_loopback.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_model_migration.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_community.cpython-312.pyc (matches tests/)
Protected path addition (observed): tests/__pycache__/test_quality_final_loopback.cpython-312.pyc (matches tests/)

# Check Commands
## Command 1: python -m unittest discover -s tests -p 'test_*.py'
Exit code: 1
Output:
```
lf_report)
R3 + S8: runtime receives configured model; executed_model stays null
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/anvil-factory/anvil-factory/tests/test_model_migration_loopback.py", line 61, in test_model_handed_in_but_executed_model_null_without_self_report
    self.assertEqual(builder["configured_model"], "fast-builder")
AssertionError: 'claude-opus-5-5' != 'fast-builder'
- claude-opus-5-5
+ fast-builder


======================================================================
FAIL: test_missing_gateway_env_fails_loudly_without_values_s9 (test_model_migration_tiers.TestOpenAIRuntimeGatewayEnv.test_missing_gateway_env_fails_loudly_without_values_s9) (env=[])
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/anvil-factory/anvil-factory/tests/test_model_migration_tiers.py", line 193, in test_missing_gateway_env_fails_loudly_without_values_s9
    self.assertIn(missing, msg)
AssertionError: 'CF_AIG_TOKEN' not found in 'gateway environment absent, missing: ANTHROPIC_BASE_URL (or ANVIL_GATEWAY_OPENAI_URL)'

======================================================================
FAIL: test_missing_gateway_env_fails_loudly_without_values_s9 (test_model_migration_tiers.TestOpenAIRuntimeGatewayEnv.test_missing_gateway_env_fails_loudly_without_values_s9) (env=['ANTHROPIC_BASE_URL'])
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/anvil-factory/anvil-factory/tests/test_model_migration_tiers.py", line 190, in test_missing_gateway_env_fails_loudly_without_values_s9
    with self.assertRaises(RuntimeError) as ctx:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: RuntimeError not raised

----------------------------------------------------------------------
Ran 542 tests in 55.459s

FAILED (failures=3, skipped=3)

```
