Looking at this work order for the intake station.

This is a gate loopback requesting three specific fixes from a previous review:
1. Remove test files the builder shouldn't have created (process violation)
2. Revert unrelated intake station config changes (out of scope)
3. Handle legacy cost override path - either remove or document it

The scope is clear and buildable. The constraints are explicit (no modifications to .github/workflows/, tests/, anvil.json, or pipelines/). Success criteria are concrete.

**Risk assessment**: Medium - this touches cost measurement and runner execution, though it explicitly doesn't affect verdicts. Not high risk (no payments, credentials, or irreversible changes), but not low risk either (touches core runner functionality and pricing data).

**Surfaces**: Cost records, token usage, price tables (data), HTTP gateway integrations (api), and documentation updates (content).

```json
{
  "intake_outcome": {
    "outcome": "accepted"
  },
  "risk": "medium",
  "surfaces": ["data", "api", "content"]
}
```
