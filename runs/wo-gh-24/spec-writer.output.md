The spec-writer station is configured without Write or Edit tools, but the station prompt requires producing output as a file. This is a configuration gap.

Given the constraint, I'll provide the revised spec content here so it can be written by other means:

The spec at `.openspec/specs/review-producer/spec.md` should be revised to incorporate the three loopback findings:

**Key changes needed:**

1. **F1 (Dual correction)**: Updated S4 and Requirements to explicitly state the correction lives only in the wrapper, not the runner. Added: "The correction logic exists only in the wrapper, never in the runner: the runner reads the file that stands when the step returns and records the outcome accordingly."

2. **F2 (Frozen suite)**: Updated S5 and Requirements to clarify that fixtures may be adapted to produce files the new way, but assertions about parse semantics, fail-closed behavior, shrinkage sentence and contract wording must remain exactly as merged in wo-gh-16. Added explicit language: "Weakening, renaming away or deleting an assertion is a spec violation."

3. **F3 (Path traversal)**: Added new S6 scenario for path traversal defense, requiring validation of packet-derived values (work order id, station id) to prevent escape from runs/<work-order-id>/. Updated Requirements to mandate validation at all path construction sites. Updated S7 (formerly S6) to include path traversal regression test.

**Required tooling:** The spec-writer station needs Write access to `.openspec/specs/review-producer/spec.md` to fulfill its station prompt requirement to "produce the output as a file in the repo, not as chat text."
