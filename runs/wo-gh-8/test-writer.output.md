Perfect! I've created comprehensive tests for the risk and surface routing feature. Here's what was delivered:

## Test File Created

**Location:** `tests/test_risk_routing.py`

## Test Coverage Summary

The test suite includes **16 test methods** organized into **8 test classes**, covering all spec scenarios S1-S6:

### Scenario Coverage

- **S1 (Low risk reduced panel)**: 2 tests
  - Reduced reviewer set selection (reviewer-spec, reviewer-tests)
  - Routing record in report with reasons

- **S2 (Security surface routing)**: 2 tests
  - Security reviewer kept at any risk level with strong model
  - Security surface with medium risk

- **S3 (Full panel routing)**: 4 tests
  - Null risk defaults to full panel with "unrated" reason
  - UI surface keeps reviewer-design
  - Medium risk uses full panel
  - High risk uses full panel with explicit "no reduction" statement

- **S4 (Policy ceiling validation)**: 1 test
  - Configuration exceeding policy ceiling fails at load

- **S5 (Routed out reviewers)**: 2 tests
  - Routed out reviewers not counted as failures
  - Routed out reviewers listed with rules

- **S6 (Routing in reports)**: 2 tests
  - Routing section in report with details
  - Swimlane shows one-line routing summary

### Additional Tests

- Gates remain unaffected by routing
- Default routing table configuration
- Project-specific routing overrides

## Test Status

All tests are properly structured following the factory's testing patterns:
- ✓ Syntax valid
- ✓ Follows factory test style (similar to `test_intake_outcomes.py`)
- ✓ Uses mock executors for different risk/surface scenarios
- ✓ Tests fail appropriately (routing not yet implemented)

The tests are ready to guide implementation and will verify all spec requirements when the routing capability is built.
