The security review passes. I found nothing that blocks the change, plus two low-severity issues worth a follow-up. The review is written to `runs/wo-gh-42/reviewer-security.review.json`, and the new test file passes (26 tests).

**No new exposure:**
- The change adds no dependency, endpoint, outbound call or permission.
- The Claude CLI is still started without a shell. The only change to its command line swaps in fixed values for the streaming output mode.

**Safe failure:**
- Partition values in `anvil.yaml` and the two new environment variables are checked strictly. A bad value is rejected, and the station stops before any model call is made.
- When `require_usage` is set, a station whose earlier usage was never measured is refused rather than counted as zero.

**Untrusted input:** the CLI's streamed output is parsed defensively. Only the token counts are read from it, and only to decide whether to stop the session. It is never run or used as a file path.

**Secrets and logs:** nothing sensitive is added to the repo. The new error and log messages contain only station names and token counts, never environment values.

**Low-severity issues for a follow-up:**
- **Ceiling can silently not apply:** if the CLI's stream ever stops reporting usage (for example after a format change), the per-station ceiling never triggers. The run-wide token cap and the check before each dispatch still apply. A record saying the ceiling went unmeasured would make this visible.
- **Orphaned CLI process:** the CLI now runs in its own process group. If the station wrapper itself is killed from outside, the CLI keeps running and spending tokens. This could already happen before the change, and the wrapper's own timeout normally fires first, so the risk is small. The fix would be for the wrapper to pass the stop signal on to the CLI's process group when it is killed.

Separately, the in-session ceiling is switched off for the Copilot runtime, with a warning printed, because Copilot only reports usage when the session ends. This is a known limitation, not a hidden bypass.
{"model": "claude-opus-5-5"}
