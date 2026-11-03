Architecture review complete. I've written the review to `runs/wo-gh-8/reviewer-architecture.review.json`.

**Verdict: changes_requested**

The routing implementation fits the project architecture well in most respects - proper layering, correct placement in artifact flow, clean model changes, and good documentation. However, I found four architectural issues:

1. **S4 not implemented** (echoing other reviewers): The `validate_model_assignment` function exists but is never called during config loading. This violates the fail-fast principle - invalid configurations should be rejected at load time with clear errors, not cause runtime failures.

2. **Incomplete configuration validation**: The config loader doesn't validate that reviewer station IDs exist in the registry or that model names are valid, allowing typos and invalid references to slip through to runtime.

3. **Hardcoded policy ceiling**: `MODEL_POLICY` is a hardcoded constant, but `ROUTING.md` documents `policy_ceilings` as configurable. This violates the "configuration over code" principle.

4. **Config structure mismatch**: Documentation shows `policy_ceilings` with keys like `reviewer-security`, but the code uses `reviewer-strong`. The documented structure doesn't match the implementation's data model.

The routing capability itself is architecturally sound - it's deterministic, properly layered, and integrates cleanly with runner and model layers. The issues are about configuration validation and documentation consistency.
