The architecture review passes, with no blocking findings. I wrote it to `runs/wo-gh-42/reviewer-architecture.review.json`; it parses as valid JSON and has no em or en dashes.

**Why it passes:**
- **Structure:** each part of the change sits where the existing code would put it, and dependencies point one way:
  - Budget settings are parsed and checked in `anvil/config.py`, once, before any station runs.
  - Consumption is read in `anvil/telemetry.py` from the existing per-attempt usage records.
  - The mid-session kill is in `tools/claude_station.py`.
  - The completeness check is in the runner and only reads the checks gate's verdict; `anvil/gates.py` is unchanged.
- **Existing decisions respected:** refused dispatches and mid-session kills end the run through the exit path from decision 0013. `max_run_tokens` is still the outer limit. The station-timeout keys and the frozen parts of the checks gate and artifact validation are untouched.
- **Owner ruling of 2026-11-22:** the completeness check only applies when a project configures partitions. The code does exactly that, and decision record 0014 states the scope and what it costs.
- **Guardrails:** only authorized files changed, and no new dependency was added. Pipeline files, `anvil.json` and the existing tests are untouched.

**Smaller follow-ups:**
1. Decision 0014 still says "proposed"; move it to "accepted" once the owner signs off.
2. The list of stations that don't call a model now exists in four places that disagree: a new copy in `anvil/config.py`, two in `anvil/runner.py` and one in `anvil/telemetry.py`. One shared helper would stop them drifting apart.
3. The runner spots a refused retry by searching the error text for a sentence that is also copied in `tools/claude_station.py`. The wrapper already exits with a dedicated code (12) for this case, which would be more reliable. The security reviewer raised the same point.
4. The handling for a station stopped at its token limit is copied in two places (`anvil/runner.py:2322` and `:2794`). A small shared function would keep the two from diverging.
{"model": "claude-opus-5-5"}
