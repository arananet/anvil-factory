I wrote the spec at `.openspec/specs/model-migration-verification/spec.md`. It is a draft; I didn't run any tests and didn't edit the work order or any other file.

- **No code changes:** the builder changes no files.
- **Model policy:** each executed step must show `configured_model` and `executed_model` agreeing with the assignments in the work order. `executed_model` must come from the runtime's self-report.
- **Builder on this run:** the work order carries a `ui` surface, so the builder is `openai/gpt-6.1-sol`. This follows the operator ruling and `model-migration` R5. The evidence test encodes both cases: `claude-opus-5-5` on non-UI work and `openai/gpt-6.1-sol` on UI work.
- **Design reviewers:** `reviewer-design` and `reviewer-ux` must run on Codex, and each must write its own review file that the runner counts.
- **Tier labels:** none may remain unresolved as `configured_model`. `review-cheap` must resolve to `claude-sonnet-5-5`, which ties to the tier totality merge.
- **Surface under review:** the spec lists the rendered status page, the six wiring files, `brain/decisions/0004-model-migration.md` and `tools/model_route_smoke.py`.
- **Verdict:** the rule is fail on a route that can't execute, a model disagreement or a missing self-report, with the evidence named. Otherwise pass.
- **Round 2:** the spec records the test-writer's one test correction. It also says the readme showcase failure came from the missing `runs/` tree, which was repaired at d5368392, and that no action is needed for it.

The spec has seven scenarios, S1 to S7.

I named the new capability `model-migration-verification` because the work order gave no `spec_path`. Say so if you want a different slug or location.
{"model": "claude-sonnet-5-5"}
