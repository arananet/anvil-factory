Perfect! Implementation complete. Let me create a final summary:

## Summary

Successfully implemented render crash tolerance per spec. All requirements met:

**Core functionality implemented:**
- Output judgment: chunks judged by frame files + SECTION_RENDER_DONE line (not exit code)
- Tolerated crashes: chunks with complete output but non-zero exit marked as tolerated_crash
- Queue resilience: removed exit 255 abort, all workers return 0 so failures never stop queue
- Completion sweeps: up to 2 passes recover missing frames by exact range only
- Per-chunk statistics: outcome records written to frames/logs/, aggregated into four classes

**Files modified:**
1. content/youtube-anvil-v2/blender/render_all.sh - render wrapper with crash tolerance
2. tools/render_stats.py - aggregates outcome records into clean_exit, tolerated_crash, requeued, failed
3. CHANGELOG.md - added Unreleased entry

**Test results:**
- All 5 scenario tests (S1-S5) pass
- Full factory test suite green (156 tests)
- No syntax errors, no em dash/en dash characters

**Compatibility preserved:**
- Invocation contracts unchanged
- All frozen surfaces untouched
- Staging provenance verified (correct blob hashes)

Builder output written to runs/wo-gh-25/builder.output.md.
