Spec revision complete. I've updated the Testing discipline section in the rendered design review spec to eliminate the ambiguity that caused loopback 2.

**The problem**: The original text "unit tests cover X" was interpreted as "check that X exists" rather than "actually call and verify X", leading to stub tests.

**The fix**: The Testing discipline section now explicitly requires tests to:
- Import the capture module and packet functions
- Call validation functions with both valid and invalid inputs  
- Call packet_rendered_evidence_section and assert on output
- Drive capture_breakpoints through the injectable seam with mocks
- Assert mocks were called and failures are recorded correctly

The revised spec provides clear, unambiguous guidance that should prevent stub tests in future implementations.

Files modified:
- `.openspec/specs/rendered-design-review/spec.md` - Updated Testing discipline section
- `runs/wo-gh-9/spec-writer.output.md` - Created output documenting the revision
