## Summary

Fixed the relative project path crash in reviewer-design preparation (loopback round 3 for wo-gh-26).

**The fix:** Changed line 560 in `anvil/runner.py` to use `project_resolved` instead of `project` when computing declared evidence display paths. This prevents ValueError when the CLI runs with a relative project argument like `python3 -m anvil.cli run . --pipeline ...`

**Verification complete:**
- Content staging verified: video file hash and size correct, durations.json absent, no modifications to content/
- Full factory suite: 204 tests passed (including T6 regression test for relative paths)
- All 9 pipelines valid

The implementation from rounds 1 and 2 stands unchanged. This was a surgical fix for the path resolution bug discovered when wo-gh-27 executed the new code path.
