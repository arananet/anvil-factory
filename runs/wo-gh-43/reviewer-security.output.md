I reviewed the change and passed it on security, with two low advisory notes that don't block it. The review is in `runs/wo-gh-43/reviewer-security.review.json`. I read the diff and `anvil/attribution.py` but didn't run the test suite.

- **Attack surface:** the change adds no secrets, dependencies, outbound calls or network access. It only reads the project's deliverable HTML and its spec files.
- **Parsing:** the HTML is parsed, not executed. Script, style, template and noscript text, comments and attributes are ignored, so hidden markup can't fake the attribution. The regexes are bounded, so there is no regex-denial risk.
- **Failure behaviour:** an unreadable page fails the check, and a missing attribution with no exception fails the gate. Projects without an HTML deliverable are unaffected.
- **Advisory, owner exception:** any matching line in any project spec, or the `attribution_exception` config key, is honoured as an owner exception. A builder station could write that line itself to skip the check. The exact-form match limits accidents, and the human gate reviewing spec diffs is the mitigation.
- **Advisory, symlinks:** `index.html` is read even if it is a symlink. The content is only tested for a string and never echoed, so the impact is negligible.

I didn't check the loopback finding that the builder report artifact was missing and lacked required literals. That falls outside a security review.
{"model": "claude-sonnet-5-5"}
