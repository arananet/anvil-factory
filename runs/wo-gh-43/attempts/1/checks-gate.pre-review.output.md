# Checks Gate: pre-review
Basis: builder_delta
Attempt: 1

# Protected Path Additions (Observed, Not Violations)
Protected path addition (observed): tests/test_attribution_default.py (matches tests/)

# Check Commands
## Command 1: python -m unittest discover -s tests -p 'test_*.py'
Exit code: 1
Output:
```
ce for reviewers, not a final verdict. Record what you observe; reviewers are not bound by your self-assessment.\n\nThis verification step only applies when the Quality Charter section is present in your packet. For non-visual work, this step does not apply.\n\n## Definition of done\n- Every spec scenario for this order is satisfied on the final tree, not only the ones a test happens to cover.\n- The project check command passes on the final tree. You ran it and read the output. You did not edit, skip or delete a test to get there.\n- You exercised the change the way a user would (ran it, opened it, called it) and it works.\n- For anything a person will see, you looked at the rendered result at the sizes the spec names and it meets the stated bar, the project design system and the Craft skills in your packet.\n- The change stays inside the write set the work order allows.\n\n## Before you hand off\nRe-read your whole diff as a reviewer would and fix what you find. Then write the builder report: what changed and which scenario each change serves, the exact verification commands with their real summary lines, and plainly what is unmet, unverified or left open. A gap you report is better than one a reviewer finds.\n' : builder

======================================================================
FAIL: test_s7_decision_record_exists_in_format (test_attribution_default.S7DecisionRecord.test_s7_decision_record_exists_in_format)
S7: 0012 record has the sections of 0011, mentions audit and line, no em dash
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-43/tests/test_attribution_default.py", line 177, in test_s7_decision_record_exists_in_format
    self.assertTrue(rec.is_file())
AssertionError: False is not true

----------------------------------------------------------------------
Ran 751 tests in 84.570s

FAILED (failures=3, skipped=6)

```

## Gate practices

Gate enforced practices this run resolved. The gate is accountable for them:

- P-1: Traversal proof for platformer orders
- P-2: Deterministic validation of builder reports with declared literals
- P-3: Capture evidence must exist before design review

## Artifact validation

- builder report: /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-43/runs/wo-gh-43/builder.output.md
- observed: missing
- report source: none
- required literals declared: 8
  - MISSING: Made with ANVIL, an open source software factory.
  - MISSING: 0012
  - MISSING: .openspec/specs/attribution-default/spec.md
  - MISSING: S1
  - MISSING: S2
  - MISSING: S3
  - MISSING: S4
  - MISSING: S5
- result: fail
- finding: Builder report artifact /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-43/runs/wo-gh-43/builder.output.md is missing.
- finding: Required literal not found in full in the builder report: Made with ANVIL, an open source software factory.
- finding: Required literal not found in full in the builder report: 0012
- finding: Required literal not found in full in the builder report: .openspec/specs/attribution-default/spec.md
- finding: Required literal not found in full in the builder report: S1
- finding: Required literal not found in full in the builder report: S2
- finding: Required literal not found in full in the builder report: S3
- finding: Required literal not found in full in the builder report: S4
- finding: Required literal not found in full in the builder report: S5
