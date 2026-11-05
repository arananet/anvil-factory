# Post-Deploy Health Test Coverage

**Work Order**: wo-gh-14  
**Spec**: `.openspec/specs/post-deploy-health/spec.md`  
**Test File**: `tests/test_post_deploy_health.py`

## Test Summary

This test file provides comprehensive coverage for the post-deploy health verification feature specified in S1-S5 of the spec. The test suite includes **21 test methods** organized into 9 test classes.

## Scenario Coverage

### S1: Healthy Deploy (deployed and healthy)
- `test_healthy_deploy_reads_as_deployed_and_healthy_s1` - Verifies route checks pass, platform signals show no errors, outcome is healthy, and deployment status reflects this
- `test_health_section_in_report_with_deployment_status_s1` - Verifies health section appears in run report with proper deployment status
- `test_health_step_shown_in_swimlane_s1` - Verifies health step appears in swimlane after deploy step

### S2: Unhealthy Deploy (failing signals, forces gate)
- `test_unhealthy_deploy_quotes_failing_signals_and_forces_gate_s2` - Verifies failing route check (500 status) results in unhealthy outcome with quoted signals and human gate requirement
- `test_unhealthy_deploy_with_platform_errors_above_acceptable_s2` - Verifies platform error counts above acceptable threshold trigger unhealthy outcome
- `test_unhealthy_outcome_sets_human_required_s2` - Verifies unhealthy outcome forces human gate even when approver verdict is approved

### S3: Unknown Health (no target or unreadable signals)
- `test_no_target_reads_unknown_never_healthy_s3` - Verifies no health target results in unknown outcome with appropriate reason and warning
- `test_unreadable_signals_read_unknown_with_failure_reason_s3` - Verifies signal read failures result in unknown outcome with specific failure reason
- `test_unknown_never_rendered_as_healthy_anywhere_s3` - Verifies unknown is never aggregated or rendered as healthy

### S4: Metrics Slot (opt-in, provider agnostic)
- `test_init_creates_metrics_slot_provider_agnostic_s4` - Verifies `anvil init` creates metrics section with empty endpoint/provider_key fields and no vendor names
- `test_new_project_creates_metrics_slot_s4` - Verifies `anvil new-project` creates metrics section
- `test_onboard_never_overwrites_existing_config_s4` - Verifies `anvil onboard` preserves existing configuration byte-for-byte
- `test_onboard_adds_metrics_to_new_config_s4` - Verifies `anvil onboard` adds metrics slot when creating new configurations

### S5: Demonstration (factory-owned target)
- `test_demonstration_target_selection_recorded_s5` - Verifies demonstration target choice (status-page or intake-worker) and reason are recorded
- `test_demonstration_run_carries_health_evidence_s5` - Verifies demonstration run report contains health section with route results and platform signals

## Additional Test Coverage

Beyond the core scenarios, the test suite includes supporting tests for:

### Route Checks
- `test_route_check_records_expected_and_observed_status` - Verifies route checks record all required fields
- `test_route_check_records_transport_error` - Verifies transport errors are captured
- `test_route_check_defaults_to_200_status` - Verifies default expected status is 200

### Platform Signals
- `test_cloudflare_workers_signal_reading` - Verifies Cloudflare Workers API signal reading
- `test_platform_signal_read_failure_recorded` - Verifies platform read failures are recorded with error detail

### Non-Blocking Behavior
- `test_no_health_target_run_proceeds_normally` - Verifies runs without health targets proceed without blocking

## Test Structure

The tests follow factory conventions:
- Use Python `unittest` framework
- Reference spec scenario IDs in docstrings (e.g., "post-deploy-health S1")
- Use `tempfile.TemporaryDirectory()` for isolated test environments
- Use `unittest.mock.patch` to mock external dependencies (HTTP requests, API calls)
- Create minimal fixture projects using `make_project()` helper
- Test both happy paths and error conditions

## Mock Strategy

Tests mock external dependencies to ensure deterministic, fast execution:
- **HTTP requests**: Mocked via `patch('anvil.health.check_route')`
- **Platform API calls**: Mocked via `patch('anvil.health.read_platform_signals')`
- **Cloudflare API**: Mocked via `patch('anvil.health.cloudflare_api_request')`

This ensures tests verify behavior without requiring network access or real deployment targets.

## Running the Tests

```bash
# Run all post-deploy health tests
python -m unittest tests.test_post_deploy_health

# Run specific test class
python -m unittest tests.test_post_deploy_health.TestHealthVerification

# Run specific test method
python -m unittest tests.test_post_deploy_health.TestHealthVerification.test_healthy_deploy_reads_as_deployed_and_healthy_s1
```

## Implementation Notes

These tests are written against the **expected API** of the health verification module (`anvil.health`). The implementation must provide:

- `verify_health(config, deploy_time)` - Main verification function
- `check_route(base_url, path, expected_status)` - Route checking function
- `read_platform_signals(platform_config, window_start, window_end)` - Platform signal reader
- `health_status_summary(result)` - Summary text generator
- `select_demonstration_target(candidates)` - Demonstration target selector

The tests also expect updates to:
- `anvil.scaffold.init_project()` - Must create metrics slot in config
- `anvil.onboard.onboard_project()` - Must preserve existing configs or add metrics to new ones
- `anvil.runner.RunReport` - Must include health section and updated deployment_status
