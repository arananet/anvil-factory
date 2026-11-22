I didn't need to change any code. The owner ruling of 2026-11-22 narrowed R4 in the spec, and the code already did exactly that. The full suite passes on the final tree: `Ran 802 tests ... OK (skipped=6)`.

- **Why no code change:** the only blocking finding from the last run was that R4 said "always" while the code ran the completeness check only when partitions are configured. With the spec amended, `anvil/runner.py:1652` and `anvil/runner.py:2440` match it as they are.
- **What I changed:** `brain/decisions/0014-station-budgets-completeness.md` now says the "only where partitions are configured" scope comes from the owner ruling and that the spec carries it in R4, S4, S5 and S8. Before, it read as the builder's own choice.
- **Report:** I wrote `runs/wo-gh-42/builder.output.md`. It has the required literals, the base ref, the 14-station partition table with its sum of 15000000, the test count, the new test file name, and the open items.
- **Checks:**
  - The first suite run had one failure, `test_s10_builder_report_evidence`, only because the report file didn't exist yet. After I wrote it, the full suite passed: 802 tests, which is 771 at the base ref plus 31 new.
  - Loading the factory `anvil.yaml` gives 14 partitions summing to 15000000, equal to the run cap.
  - No existing test, pipeline file or `anvil.json` differs from the base ref, and neither changed file has an em or en dash.

**Still open (listed in the report):**
- I didn't build the three small follow-ups the reviewers suggested, to keep this change small:
  - The in-flight ceiling should record "ceiling unmeasured" when the CLI streams no usage.
  - The wrapper should pass SIGTERM on to the CLI process it started.
  - The empty-file check should read only a bounded amount of the file.
- No test runs the refusal of an in-session correction through the runner.
- The in-flight ceiling has only been tested against a stand-in CLI, not the real one.
- Making the completeness check apply to every project is left to a separate order.

Nothing is committed.