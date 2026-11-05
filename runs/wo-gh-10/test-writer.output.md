Test corrections complete. Both failing tests now align with spec S3:

**test_gateway_response_with_usage**: Switched from intake (unpriceable 'default' model) to builder ('fast-builder' has price entry). Now properly exercises S2 gateway usage pricing.

**test_run_report_includes_cost_section**: Updated expectations to measured_steps=1, unmeasured_steps=1. Only builder is measured; intake's 'default' model has no price entry per S3.
