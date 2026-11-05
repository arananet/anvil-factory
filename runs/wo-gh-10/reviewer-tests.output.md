Review complete. Both test corrections properly implement spec S3's requirement that models without price table entries record as unmeasured:

**test_gateway_response_with_usage**: Correctly switched from intake (unpriceable 'default' model) to builder ('fast-builder' has price entry). Now properly exercises S2 gateway usage pricing with a measurable step.

**test_run_report_includes_cost_section**: Correctly expects measured_steps=1 and unmeasured_steps=1. Builder is measured (fast-builder priced), intake is unmeasured ('default' has no price entry per S3).

Both tests are real (call actual implementation), mapped to spec scenarios, and aligned with the spec's handling of unpriceable models.
