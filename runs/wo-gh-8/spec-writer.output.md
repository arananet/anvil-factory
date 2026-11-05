Reading the spec and work order. The spec at `.openspec/specs/risk-routing/spec.md` is complete and correct for gate loopback 2.

The spec already clearly states the S4 behavior at load time:
- Line 18: "Configuration validation happens at load time. When routing configuration is loaded, every model assignment in the merged configuration... is validated against the policy ceiling. A configuration that assigns a model above the policy for a station kind fails to load with an error..."
- S4 scenario (line 43-44): "Given a project routing configuration that assigns a station kind a model above the recorded policy, when the configuration is loaded, then loading fails with an error..."

The spec also incorporates all loopback 1 findings:
- S7 added for policy_ceilings override capability (Finding C)
- Line 20 documents that routing trusts intake outcomes (Finding E)
- Configuration validation requirements expanded (Finding B)

Gate loopback 2 identifies a test implementation defect, not a spec defect. The test `test_config_above_policy_fails_load_s4` calls `load_routing_config(proj)` bare instead of wrapping it in `assertRaises(RoutingConfigError)`. The work order states "The test-writer station writes this fix."

**Spec-writer station output**: The spec is complete and requires no revision. The gate loopback 2 defect is in test implementation; the test-writer station owns the fix.
