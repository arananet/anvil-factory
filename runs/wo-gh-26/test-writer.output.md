## Summary

I've written deterministic unit tests for the declared evidence wiring feature in `tests/test_declared_evidence_review.py`. The test file implements all five test scenarios (T1-T5) from the spec:

**Test Coverage:**
- **T1**: Declared PNG fixtures assemble contact sheet and packet references it
- **T2**: Missing declared image fails with `DeclaredEvidenceMissing` error naming the path
- **T3**: Packet Evidence section lists contact sheet and all declared paths individually  
- **T4**: Reviewer-facts packet contains "Declared evidence inputs" section with paths
- **T5**: New `content-film-review.json` pipeline loads with correct topological order (no authoring stations)

**Test Characteristics:**
- Deterministic, no model calls or network access
- Small PNG fixtures (100x100 pixels) created with standard library helpers
- Follows existing factory test patterns from `test_astra_consumption.py`
- Test classes named for scenarios with clear docstrings
- Proper setup/teardown and focused assertions

**Review files created:**
- `runs/wo-gh-26/test-writer.review.json` - verdict: pass
- `runs/wo-gh-26/test-writer.output.md` - detailed test documentation

The tests are ready and will validate the implementation when the builder station completes the feature.
