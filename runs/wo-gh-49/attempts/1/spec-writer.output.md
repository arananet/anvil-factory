I've revised the spec at `.openspec/specs/stop-futile-loops/spec.md`. It already existed and covered R1 to R6, so I kept that content and added what the work order asks for beyond it. I ran no tests, since this station writes only the spec. A scan found no em or en dash in the file.

**What I added or changed**
- **Header:** the base ref `d74c83aefff95fba777ca04505116cfb63c6c8f3` and the issue link.
- **New sections:** a short Terms section (counted review, loopback, stop), Out of scope, and an explicit Allowed write set that lists the protected paths too.

**Requirement ids, now split into sub-ids:**
- R1.1 to R1.3: the `owner_ruling` field. The instruction goes in the packet the runner builds and in each reviewer prompt, never in `review_suffix`. A non-string or blank value is dropped and recorded as `owner_ruling_ignored` with its reason.
- R2.1 to R2.5: the `owner_ruling_needed` stop, a top-level `owner_rulings` list of station and question, a human gate rule containing "owner ruling needed", an "Owner ruling needed" heading in the comment, and no new verdicts.
- R3.1 to R3.3: `no_progress`. A change means a file created, deleted or edited outside `runs/`, ignoring files in `.gitignore`. The first attempt is never compared.
- R4.1 to R4.3: `checks_stuck`. This covers the failure signature, the default patterns, and a configuration error for bad `gate_failure_patterns`. The stop compares only with the attempt just before. The reason is capped at 2000 characters. `checks_stopped` is unchanged.
- R5.1 to R5.4: the three stops join the set of exit statuses, have the three on/off switches with defaults in `anvil/config.py`, add a `next_human_action` field, and reach live progress with no change to `anvil/sinks.py` or the events contract.
- **New R6.2, R6.3:** tests about this order's own run skip unless `ANVIL_WORK_ORDER_ID=wo-gh-49`, no test compares wall-clock figures between runs, and the full suite stays green.
- **New R7.1, R7.2:** what the builder report must contain, and the rule to stop and report on the first attempt if an existing test contradicts the order.

**Scenarios:** S1 to S8 are rewritten with concrete values, and each names its requirement ids. S9 (the stops reach the live progress comment) and S10 (suite green, the run's own facts guarded, protected paths untouched, no dashes) are new.

**Decisions for the owner.** These are choices I made to keep the scenarios testable:
1. **Field names:** `owner_rulings`, `next_human_action` and `owner_ruling_ignored` are my names, not the order's.
2. **2000-character cap:** the order only says the reason must be "bounded in length", so I picked the number.
3. **Where the defaults live:** today the efficiency defaults are kept in `anvil/telemetry.py`, which is outside the allowed write set. I put the new defaults in `anvil/config.py`, so a new project's generated config won't list the new keys. Allowing `telemetry.py` would change that.
4. **Ruling on a passing review:** a kept `owner_ruling` stops the run even when every counted review passes. The verdict is then approved but the human gate is closed. That follows the order's "any counted review" literally. Confirm or narrow it.
5. **Switch off but question asked:** with `stop_on_owner_ruling` off, the question is still recorded on the review but causes no stop.
{"model": "claude-opus-5-5"}
