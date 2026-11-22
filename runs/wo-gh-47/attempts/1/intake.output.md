Intake accepts wo-gh-47 as written. It is one feature (status sinks that show a run while it is still going) and the order spells out every part of it:

- **Scope:** requirements R1 to R6 and the guardrails cover the spec at `.openspec/specs/live-progress-sinks/spec.md` (129 lines).
- **Files it may write (P-15):** the order lists them all, and the existing files under `tests/` stay untouched because new tests come in as new files. It changes nothing under `anvil.json` or `pipelines/`, and limits what may change in `anvil/runner.py`.
- **Clashes with earlier orders (P-14):** the order already settles how it fits with governed delivery's frozen state and events files, the "retry" word check, the report shape from wo-gh-41, the wo-gh-42 settings, and the `runtime_refused` exit status. Tests that check this order's own run must skip for other orders, which avoids the problem wo-gh-42 hit.
- **Factory sink entry:** the factory's `anvil.yaml` already has `{"type": "github-issue"}` on this run branch, carried over from an earlier run.
- **Risk is high:** the sinks read a GitHub token and make network calls from the line process, and the order requires that no token value ever leaks.

This matches the outcome the previous intake run on this branch reached.

```json
{
  "intake_outcome": {"outcome": "accepted"},
  "risk": "high",
  "surfaces": ["api", "security", "data", "content"]
}
```
{"model": "claude-opus-5-5"}
