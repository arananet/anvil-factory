I passed the security review for wo-gh-47. The review is written to `runs/wo-gh-47/reviewer-security.review.json`, and the 31 new sink tests pass (2 are skipped because they only run for this order's own run). I did not run the full factory test suite.

**The checks-gate finding is fixed.** On the second attempt the builder did change files: `anvil/sinks.py` now closes the connection when the GitHub API returns an error, so failed calls no longer leak sockets. It also added `tests/test_live_progress_sink_errors.py` and a `CHANGELOG.md` entry. `anvil/runner.py` changes in one place only, where the recorder is created, and has no network code.

What I checked:
- **Token handling:** the token is read from the environment at call time and only ever goes into the request's `Authorization` header. Error notes record just the sink type and the HTTP status or error type, and "inactive" reasons name the variable, never its value. A test checks this end to end.
- **Stations can't get the token:** config loading refuses any `token_env` that isn't on the station blocked-variable list or that is explicitly kept, so a misconfigured sink fails at load time rather than leaking.
- **Input handling:**
  - The issue number only comes from a work order id that matches `wo-gh-<number>`.
  - `GITHUB_REPOSITORY` must look like `owner/repo`.
  - `owner_type` can only be `user` or `organization`.
  - Values go to GitHub's API as query variables, never pasted into the query text.
  - The sinks list is checked against a fixed set of types and keys.
- **Comment content:** only plain facts (ids, statuses, counts, cost, times, the public run link), with no prompts, station output, paths or secrets.
- **No new attack surface:** no new dependency, no workflow changes, and a sink failure never changes the verdict.

Two low-risk notes that don't block the pass:
1. When paging through comments, the code refuses to send the token to a different host, but a server redirect can still carry it. Python's standard HTTP client keeps the `Authorization` header when it follows a redirect to another host. Refusing redirects, or dropping the header on a cross-host redirect, would close that.
2. The API address comes from `GITHUB_API_URL`, as the spec requires, so anyone who can set that variable in the line process can point the token at another host. That is the same trust level as the rest of the runner environment, not something new.
{"model": "claude-opus-5-5"}
