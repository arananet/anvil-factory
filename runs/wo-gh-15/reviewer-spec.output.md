Review complete. Written to `runs/wo-gh-15/reviewer-spec.review.json`.

**Verdict: changes_requested**

**Finding:** The PROMPT.md does not explicitly document the S7 same-subject test duty as required by the loopback scope. While line 73 adds a generic instruction to "follow duties in the packet", the PROMPT should explicitly state what the same-subject test duty is, when it applies (both identity_reference and deliverable_set declared), and what it requires (cross-set comparison against identity reference on enumerated traits, with divergence as quality failure).

The packet injection (anvil/quality.py:129-160) is correct and comprehensive. The tests (test_quality_same_subject.py) prove it end-to-end. The suite is green at 393 tests. But the PROMPT itself needs explicit same-subject test documentation, not just the meta-instruction at line 73.
