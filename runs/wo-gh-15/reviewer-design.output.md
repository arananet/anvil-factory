## Review Complete

**Verdict: changes_requested**

The round 4 loopback scope has three items:

1. ✗ **PROMPT.md documentation** - INCOMPLETE
2. ✓ **Packet injection** - Complete (anvil/quality.py:130-160)
3. ✓ **Tests** - Complete (tests/test_quality_same_subject.py, 5 tests passing, full suite green at 393 tests)

### The Finding

**S7 same-subject test duty documentation incomplete in stations/reviewer-design/PROMPT.md**

The loopback scope item 1 requires explicit documentation of the same-subject test duty in the station prompt: when it applies, what the reviewer must do, and how to record the ruling.

Current state at PROMPT.md:73: "When the Quality Charter section in your packet includes additional duties beyond the standard criteria comparison, follow those instructions as part of your quality section judgment."

This is a generic fallback statement that tells the reviewer to follow additional duties IF they appear in the packet, but it does not document:
- What the same-subject test duty is
- When it applies (when identity_reference + deliverable_set are declared)  
- What specifically must be compared (identity traits across deliverable set against canonical reference)
- How to record the ruling (in quality section with divergent asset and trait named)

A reviewer reading the prompt would not know what a same-subject test is or what it requires. The duty must be explicitly documented in the prompt itself, not just injected via packet.

The packet injection and tests are working correctly - only the prompt documentation remains to close this loopback round.
