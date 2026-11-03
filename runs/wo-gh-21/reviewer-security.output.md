## Security Review Complete

I've reviewed the wo-gh-21 round 3 implementation for security risks. My review is written to `runs/wo-gh-21/reviewer-security.review.json`.

**Verdict: changes_requested**

### Critical Security Vulnerability Found

**IDAT Decompression Not Actually Bounded** (anvil/runner.py:212)

The implementation attempts to comply with loopback gate round 3, finding 3b, but uses the wrong approach. Line 212 calls:

```python
raw_pixels = zlib.decompress(idat_data, bufsize=expected_raw_size)
```

The `bufsize` parameter is **not a maximum length** - it's only an initial buffer allocation hint. Python's zlib documentation states this is "the initial size of the output buffer", not a decompression limit.

A crafted PNG can decompress to gigabytes during this call, exhausting memory before the defensive size check at line 217 executes. The requirement explicitly states: "decompress with an explicit maximum length" and "fail loudly when the stream yields more than the expected size."

**Attack scenario**: Attacker provides a small PNG file (passing the 100MB file size cap) containing highly compressed IDAT data. During decompression at line 212, the data expands to gigabytes, causing memory exhaustion before line 217's size validation runs.

**Required fix**: Use actual bounded decompression - either the `max_length` parameter (Python 3.11+) or `zlib.decompressobj()` with incremental decompression and a hard cap.

### Verified Correct Implementations

- **Finding 1**: S3 provenance check properly wired into `prepare_reviewer_design_step` (line 482)
- **Finding 2**: Layer violation resolved - no `.stations` import in `build_reviewer_design_packet`
- **Finding 3a**: Allowlist path boundaries correctly enforced at path separator boundaries
- **Finding 3c**: IDAT accumulated bytes properly capped before decompression (lines 198-202)
- PNG file size caps, dimension caps, CRC verification, and path validation all correctly implemented

The IDAT decompression vulnerability is the single blocking security defect requiring changes.
