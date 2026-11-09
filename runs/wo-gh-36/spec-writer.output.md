I made no changes, because the spec for this work order already exists and already matches it.

`.openspec/specs/practice-skills/spec.md` came in with the execute-workflow commit. I checked it against `wo-gh-36` and found:
- **Requirements:** R1 to R8 match the work order one for one: the base, the consistency check, deterministic resolution, recording, override precedence, the prompt/gate split, the empty base, and compatibility. The scope limits cover the standard-library-only, no-pipeline-change, no-prompt-rewrite and no-dash guardrails.
- **Scenarios:** S1 to S9 cover each requirement. Resolution, the override exclusion, the gate listing and the empty-base report field each have at least one scenario.
- **Dashes:** the spec and the work order JSON contain no em or en dash characters.
- **Issue 33:** I found no scoped-learnings spec, branch or commit in the repo, so I read it as not yet merged. The execution run should therefore implement the matcher in the brain module and record the parallel in the run report (R8). The R8 text already says this.

The spec's `Status: proposed` is left as is. Moving it past proposed is a decision for a different station.

The inputs were enough, so nothing is missing for the builder. The `brain/` files I read (`project.md`, `decisions/`, `inbox/`) have no practices base or practice proposals yet, which fits R7.
{"model": "claude-sonnet-5-5"}
