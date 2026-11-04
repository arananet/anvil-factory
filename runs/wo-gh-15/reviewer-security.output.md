## Security Review Complete

**Verdict: changes_requested**

I've identified a control character injection vulnerability in the round 4 implementation:

**Finding**: The new same-subject test duty injection code in `anvil/quality.py` (lines 140 and 146-147) directly interpolates `work_order.identity_reference` and `work_order.identity_traits` into packet markdown without sanitizing control characters.

Round 1 finding F3 explicitly required: "Work order controlled strings interpolated into packet output are sanitized of control characters."

While these fields have proper path validation (no traversal), they lack control character sanitization. An attacker could craft a work order with embedded ANSI escape codes, null bytes, or other control characters that would be injected into reviewer packets.

**Fix needed**: Import and apply the existing `_sanitize_control_chars` function from `anvil.runner` (or define an equivalent in `quality.py`) to sanitize `identity_reference` and each trait in `identity_traits` before interpolation.

Review written to `runs/wo-gh-15/reviewer-security.review.json`
