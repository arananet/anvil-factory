# Decision 0001: Composable stations

Status: accepted

## Decision
Pipelines are composed from reusable stations. A station is defined once in stations/ with a manifest and, for agent stations, a prompt file. Pipelines only order stations, they do not redefine them.

## Why
The same reviewer can serve a full SDLC line, a hotfix line and a docs line. Reuse keeps contracts honest and makes a new line a small JSON file, not new code.

## Consequences
Station ids must be unique in a pipeline. Parallel groups need at least two stations. Unknown stations fail validation early.
