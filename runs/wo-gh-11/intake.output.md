Looking at this work order for intake evaluation.

This is a GATE LOOPBACK 2 refinement with two clear, specific fixes:
1. Wire S10 guided designation into the runtime (add guided field to Station dataclass, wire it through load_registry, apply design model from routing policy)
2. Fix three skipped tests to actually test their implementations

The work is clearly scoped, buildable as stated, and has all necessary information. It's touching core factory runtime logic (station loading, routing policy integration) and test implementations - moderate complexity with reversible changes and moderate blast radius.

```json
{
  "intake_outcome": {
    "outcome": "accepted"
  },
  "risk": "medium",
  "surfaces": ["data"]
}
```
