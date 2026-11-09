I wrote `runs/wo-gh-36/observer.output.md`. It says no observation was possible, because the release record this station needs doesn't exist.

- **Missing release record:** the deployer's envelope status is `packet_ready`. It has a packet and no output file. The work order also says nothing in this loopback publishes or deploys, so a release may never have been intended.
- **Context only:** `report.json` shows verdict `no_reviews`, which matches the corrected S8 expectation. I didn't find a top-level `practices` field in it and didn't investigate. The packet's upstream list shows the checks gate passed, and reviewer-spec and reviewer-tests ran.
- **To proceed:** the deployer needs to produce a release record, or state that no release occurred. The owner could instead confirm no release is intended. Then the observer can be re-run.

The report contains no em or en dashes.
