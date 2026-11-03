## Summary

The risk and surface routing feature has been **successfully implemented and verified**. All tests pass and all pipelines remain valid.

### Implementation Status

The routing capability was already fully implemented in the codebase:

✅ **Core Implementation** (`anvil/routing.py`):
- Routing logic with all 6 spec scenarios (S1-S6)
- Default routing configuration with factory-shipped rules
- Model policy ceiling validation
- Routing record generation and persistence

✅ **Runner Integration** (`anvil/runner.py`):
- Routing step executes after intake, before reviewers
- Routed-out reviewers marked as expected absences
- Model selection based on routing decisions
- Report and swimlane rendering with routing information

✅ **Tests** (`tests/test_risk_routing.py`):
- 16 tests covering all 6 spec scenarios
- All tests passing ✓

✅ **Documentation** (completed in this session):
- Created `docs/ROUTING.md` with comprehensive routing documentation
- Updated `docs/ARCHITECTURE.md` to include routing in artifact flow and as a new section
- CHANGELOG already includes routing feature description

### Test Results

```
Ran 16 routing tests - ALL PASSED ✓
Ran 235 total tests - ALL PASSED ✓
Validated 8 pipelines - ALL VALID ✓
```

### Key Features Implemented

1. **Deterministic routing** after intake based on risk and surfaces
2. **Reduced panel** for low-risk work (reviewer-spec, reviewer-tests at cheaper model)
3. **Security surface** always keeps reviewer-security at strong model
4. **UI surface** keeps reviewer-design when present
5. **Model policy ceiling** prevents routing from exceeding policy limits
6. **Routed-out tracking** with reasons, never counted as failures
7. **Full observability** in routing.json, report.md, and swimlane.md
8. **Project configuration** support for custom routing rules

The feature is production-ready and fully documented.
