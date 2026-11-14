The checks gate will probably fail again on this attempt, and not because of the timeout work. The suite has 5 approval tests that fail whenever they run inside GitHub Actions, and I can't fix them within this order's rules.

**Why those 5 fail.** The Actions runner sets `GITHUB_ACTOR=arananet`. The approval tests don't clear that, so `anvil/line.py:151` correctly refuses `--by ana` as someone else's identity. They were already failing before this change: on a clean copy of HEAD (c673c25) the same 5 fail. With those GitHub variables unset, the full suite passes on the final tree: 736 tests, 6 skipped, no failures.

I left them alone for three reasons:
- the code involved (`anvil/line.py`, `anvil/gates.py`) is outside the files this order may change;
- existing tests are protected;
- making them pass would mean loosening the check on who is approving.

**Decision for you:** either run the project check without the host GitHub identity variables, or fix the tests' environment handling in a separate order. Until one of those happens, the gate fails in Actions whatever this order contains.

**This attempt:** the code from attempt 2 is unchanged; re-checked, it covers S1 to S5:
- **Configuration:** `ANVIL_STATION_TIMEOUT_SECONDS` wins over anvil.yaml, which wins over the defaults (3600 seconds for producing stations, 1500 for the rest). Anything above 7200 is cut down to 7200.
- **Executor:** its timeout is always at least the largest station timeout plus 60 seconds, so the station's own limit is the one that kills it.
- **Timeout record:** a killed station records `timed_out`, the elapsed time, the timeout value, the reason, the model and any partial usage.
- **Root cause:** confirmed at the file and line positions the order gave, at each historical ref and the run base.
- **Evidence:** the two new timeout test files pass (26 tests), and I checked the setting's resolution by calling it directly.

I wrote the missing builder report to `runs/wo-gh-39/builder.output.md`. It contains all four required literals and no en or em dashes. No station has actually run past 1500 seconds; the proof is the scaled-down tests, which is what the spec asks for.