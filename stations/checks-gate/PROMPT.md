# Checks Gate

The checks gate is a deterministic gate that runs the project's configured check commands and validates that no protected paths have been touched.

This gate:
- Runs check commands from the base ref configuration
- Validates that changed files do not touch protected paths
- Returns pass/fail verdict based on check exit codes and protected path rules
- Is a machine verdict, not a model opinion

The gate runs:
1. After the builder station and before the reviewer stage
2. After merge sync and before the deployer or publisher station

Protected paths default to:
- The checks configuration itself (anvil.json)
- The project's tests directory (tests/)

A project may extend or replace the protected paths list in its configuration.
