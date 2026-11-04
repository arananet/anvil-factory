Spec updated. The revised spec at `.openspec/specs/risk-routing/spec.md` now incorporates all five gate loopback findings:

**Finding A (validation not wired)**: Added explicit requirement that configuration validation happens at load time, with all model assignments validated against the policy ceiling during `load_routing_config`.

**Finding B (structure validation missing)**: Added requirement that reviewer lists are validated for valid station IDs and all model references are validated against the model hierarchy. Expanded S4 to cover these validation failures.

**Finding C (policy ceiling config misalignment)**: Added requirement that projects can override policy ceilings via `policy_ceilings` section in configuration, with factory defaults as fallback. New S7 scenario covers this explicitly.

**Finding D (placeholder tests)**: Expanded S4 with concrete validation cases and added S7 - these provide clear scenarios for proper test implementation with real assertions.

**Finding E (security trust model)**: Added explicit requirement documenting that routing trusts intake outcomes as authoritative - this is the accepted design choice, with intake owning rating and routing owning panel selection. Documented as an intentional decision rather than an oversight.
