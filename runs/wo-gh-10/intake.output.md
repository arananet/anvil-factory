Looking at this work order for the closing verification run.

The scope is clear and specific:
1. Revert exactly two intake configuration changes that were out-of-scope
2. The test-writer station will author the cost measurement tests
3. Everything else (the core cost measurement implementation) stands as audited

This is buildable as stated - it's a minimal, focused fix to close out finding #2 from the loopback review.

```json
{
  "intake_outcome": {
    "outcome": "accepted"
  },
  "risk": "low",
  "surfaces": []
}
```
