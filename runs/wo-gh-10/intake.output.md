Looking at this TEST CORRECTION RUN work order for wo-gh-10.

This is a narrowly scoped request to correct exactly two failing tests that contradict the spec. The work order clearly identifies:
- Which tests need correction
- Why they're wrong (they expect the intake step to be measured when it should be unmeasured per spec S3)
- What the corrections should be
- Clear constraints (test-writer makes changes, builder only acts if tests reveal bugs)

This is buildable as stated with minimal blast radius.

```json
{
  "intake_outcome": {"outcome": "accepted"},
  "risk": "low",
  "surfaces": ["content"]
}
```
