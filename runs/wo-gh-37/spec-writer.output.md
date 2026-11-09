I revised `.openspec/specs/station-artifact-contract/spec.md` with one added requirement. The spec was already present and approved, and it covers S1 to S5 from the work order. I haven't committed it, and no tests were run because only the spec changed.

The spec said the work order "declares" required literals but never said how. The implementer would have had to guess the field name and the matching rule. The new requirement fixes both:
- **Field:** the work order carries an optional top-level `required_literals`, a list of non-empty strings.
- **Matching:** exact substring containment on the report text. An abbreviation like `67217b9d...c83b86f`, an ellipsis or a case change does not match.
- **When absent or empty:** validation only checks that the report exists and is non-empty, so work orders that declare nothing behave as before.

The spec file contains no em or en dashes. I changed nothing outside the spec. `work_orders/wo-gh-37.json` was already modified when I started, and I left it alone.

The field name `required_literals` is my choice. Nothing in the repo, the brain or the work order defines it. If the owner wants a different name, change it in the spec before the build station starts.
{"model": "claude-sonnet-5-5"}
