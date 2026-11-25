I revised `.openspec/specs/proven-patterns/spec.md` to match the released work order. Nothing was built or run beyond checks on the spec itself: it has no em or en dash characters, decision number 0020 is free, and `blueprints/` exists.

**What changed in the spec**
- **Header:** it now names the work order and the base ref, `13244db35475b9a19dbd041bc69cf6487d806a45`, along with decisions 0015 to 0019.
- **New Terms section:** defines pack, proposal, promoted pack, the `OPEN:` marker for fields still needing judgment, budget tokens and raw tokens.
- **R1:** split into R1.1 to R1.6, with exact fields, types and loading errors. The content rule now lists the forbidden file extensions, the binary test, secret-style names and token file names. It also says how the source project's design token values are caught.
- **Token figures:** each one in `calibration.json` must say whether it is raw or budget tokens. A budget figure must carry its `cache_read_weight`, and one pack uses a single weight, as the release asked.
- **R2:** split into R2.1 to R2.5. It covers the harvest manifest, the provenance record (per-file commit and sha256), what makes harvest refuse, byte-identical repeat runs, and the rule that nothing in the inbox is ever used.
- **R3:** split into R3.1 to R3.3. It lists the promotion conditions, says a refusal names everything missing and changes nothing on disk, and keeps previous versions in `history/<version>/`. It also fixes what `check-patterns` prints and when it fails.
- **R4:** split into R4.1 to R4.4. It adds the tie-break and the run report's `pattern` key.
- **R5:** split into R5.1 to R5.5. It adds:
  - exact section headings for each packet;
  - a fourth trim step that runs after the three existing ones, so the order fixed by `tests/test_astra_consumption.py` is untouched;
  - a `pattern_trimmed` flag on the step record;
  - exactly what `init --pattern` writes, with the calibration feeding the new project's `efficiency.station_budgets`.
- **R6.1:** the sentence saying the project's own brain, practices and specs win is now required in every pattern section.
- **R7.1 to R7.3:** cover scenarios S1 to S10, follow the decision 0018 guard rule, and require the full suite to pass.
- **R8.1 and R8.2 (new):** the builder report must contain the four required strings, the base ref, the test count and the new test file names, and must stop on a conflict with a protected test.
- **Scenarios:** S1 to S9 were rewritten with real values and the requirement ids they prove. S10 is new and covers the suite and the builder report.
- **New sections:** "Out of scope" and an "Allowed write set". The write set lists the new files, the changed files, and the paths that must not change, naming the protected tests.

**Decisions I made that you need to confirm**
1. **Manifest:** it defaults to `<project>/anvil-harvest.json`, can be overridden with `--manifest`, and has the fields `files`, `provenance` and optionally `design_tokens`. The order named a manifest but no format.
2. **Who sets provenance:** the operator declares in the manifest whether the line produced the work or it was authored outside it. Harvest can't work that out on its own.
3. **Picking between two matching patterns:** the most specific wins (fewest product types served), then the highest version, then the lowest id. The order said "most specific" without defining it.
4. **Version format:** one to three dot-separated integers, compared part by part, so 1.10 beats 1.2.
5. **Product copy:** the validator can't reliably detect copied prose or product scripts. Those are left to your judgment at promotion, and `docs/PATTERNS.md` must say so.
6. **Starting budgets:** only budget-token figures become the new project's starting station budgets. Raw figures are skipped and named, not converted.
7. **Factory checks:** `check-patterns` is not added to the factory's own `anvil.json`, because that file is protected. Adding it later is your call.
8. **Fixture location:** test fixtures go in a new `tests/fixtures/patterns/`, and the decision record is numbered 0020.
{"model": "claude-opus-5-5"}
