Excellent! The regression test T6 is complete. Let me create a final summary:

## Summary

Added regression test **T6** to `tests/test_declared_evidence_review.py` for the relative project path defect found in wo-gh-27 run 41774853775.

**Test class:** `TestRelativeProjectPathSupport`

**Test method:** `test_relative_project_path_with_declared_evidence`

**What it tests:** 
- Creates a temporary project with declared PNG evidence
- Changes to the project directory and calls `prepare_reviewer_design_step` with `Path('.')` (the CLI invocation shape)
- Asserts the packet is built successfully and lists declared evidence paths

**Current status:**
- Tests T1-T5 (from rounds 1 and 2): ✅ passing
- Test T6 (this round): ❌ failing with the expected defect

The test correctly catches the ValueError at line 560 of `anvil/runner.py` where absolute paths are computed relative to the unresolved `Path('.')`. The test will pass once the builder applies the fix: using `project_resolved` instead of `project` to compute display paths.

Test output written to: `runs/wo-gh-26/test-writer.output.md`
