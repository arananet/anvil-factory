Gate round 2 builder work complete.

## Summary

**Root cause fixed**: Four render crash tolerance tests (s1, s3, s4, s5) now set `VIDEO_CONTENT_DIR` to their tmp work directories when calling `render_stats.py`, preventing production file modifications.

**Verification results**:
- Video file staging: hash and size match ✓
- Test suite: 203 tests passed, 0 failed ✓
- Content directory: no modifications, byte-identical to staging ✓
- Pipeline validation: all 9 pipelines valid ✓

**Changed files**:
- tests/test_render_crash_tolerance_s1.py
- tests/test_render_crash_tolerance_s3.py
- tests/test_render_crash_tolerance_s4.py
- tests/test_render_crash_tolerance_s5.py
- runs/wo-gh-26/builder.output.md

Round 1 implementation remains intact: declared evidence wiring, DeclaredEvidenceMissing error, packet evidence naming, reviewer packet sections, content-film-review pipeline, and all six scenario tests.
