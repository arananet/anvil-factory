I re-checked the spec for wo-gh-30 round 2 against the brief. It needed no edits.

The spec is at `.openspec/specs/model-migration-verification/spec.md` (status: draft) and has seven scenarios, S1 to S7. I changed no other file and ran no tests. I rewrote `runs/wo-gh-30/spec-writer.output.md` as the output summary, because the re-fire had deleted it.

The spec covers the round 2 points:
- **Builder policy:** it is `claude-opus-5-5` on non-UI work and `openai/gpt-6.1-sol` on UI-surface work. This work order carries a UI surface, so the builder is `openai/gpt-6.1-sol`.
- **Test correction:** the test-writer's builder-policy correction is the only test change this round. The readme showcase link test needs no action, because `runs/` was repaired on main at d5368392.
- **Per-station policy:** every executed step must show `configured_model` and `executed_model` agreeing with the assignment, and `executed_model` must be the runtime's self-report. The design reviewers run on Codex, each writing its own counted review file.
- **Verdict rule:** fail on a route that can't execute, a model disagreement or a missing self-report, naming the evidence. Otherwise pass.

I chose the slug `model-migration-verification` myself, because the work order gave no spec path.
{"model": "claude-sonnet-5-5"}
