Security review complete. Found **1 critical, 1 medium, and 1 low severity security issue**.

## Critical Finding

The CLI does not pass `base_ref` to `run_pipeline` (anvil/cli.py:103), causing the checks configuration to be read from the **working tree instead of the base ref**. This directly violates the S4 requirement and the threat model.

**Threat**: A malicious builder could modify `anvil.json` on the work branch to inject arbitrary shell commands that execute with `shell=True` before any reviewer sees the work.

The spec explicitly states: "Reading the working tree file at run start does not satisfy S4, because the working tree at run start is the work branch tip, not the base ref state."

The regression tests pass because they explicitly provide the `base_ref` parameter, but production CLI usage leaves it as `None`, bypassing the entire security control.

**Review JSON written to:** `runs/wo-gh-6/reviewer-security.review.json`
