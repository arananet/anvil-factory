The test corrections pass spec review.

**Test 1: test_gateway_response_with_usage (S2)**
- Corrected to test the builder station (model: fast-builder, priced) instead of intake (model: default, unpriced)
- Now properly exercises S2: gateway usage is consumed and priced when the model has a price table entry
- Assertions correctly expect non-null cost and verify the calculated amount

**Test 2: test_run_report_includes_cost_section (S4)**  
- Corrected expectations to measured_steps=1, unmeasured_steps=1 for the intake+builder pipeline
- Intake station uses model 'default' (no price entry) → unmeasured per S3
- Builder station uses model 'fast-builder' (priced) → measured per S1/S2
- Total correctly equals only the measured step's cost per S4

Both corrections align with the spec scenarios. The review JSON has been written to runs/wo-gh-10/reviewer-spec.review.json with verdict "pass".
