I wrote the observation report to `runs/wo-gh-36/observer.output.md`. It says no observation was possible, because the release record this station needs doesn't exist.

- **Missing release record:** the deployer's envelope status is `packet_ready`. It has only a packet and has produced no output. The work order also says nothing in it publishes or deploys, so a release may never have been intended.
- **Upstream status worth checking:** the packet lists the checks gate as failed and all six reviewers as skipped, yet the approver and triage-human steps show as completed. I recorded this as context only and didn't verify it.
- **To proceed:** the deployer needs to produce a release record, or state that no release occurred. The owner could instead confirm the order isn't to be released. After that, the observer can be re-run.

The report doesn't claim the change works, and it neither approves nor rejects it. It contains no em or en dashes.
