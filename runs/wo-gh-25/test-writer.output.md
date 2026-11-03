Test suite complete. Created five deterministic tests (T1-T5) mapping to spec scenarios S1-S5:

- **test_render_crash_tolerance_s1.py**: Chunk crashes after writing frames/DONE → success, tolerated_crash recorded
- **test_render_crash_tolerance_s2.py**: First job fails hard → all later jobs still launch  
- **test_render_crash_tolerance_s3.py**: Partial frames → re-queued by missing range only, reported as requeued
- **test_render_crash_tolerance_s4.py**: Persistent failure → fails after 2 sweeps, missing range named
- **test_render_crash_tolerance_s5.py**: All outcome classes recorded, existing keys preserved

Tests drive render_all.sh with fake Blender binaries via BLENDER environment variable. CHANGELOG updated with Unreleased entry. Output documented at runs/wo-gh-25/test-writer.output.md.
