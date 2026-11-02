# Decision 0003: Evidence must exercise the production shape

Status: accepted
Adopted: 2026-10-31, by the owner's order.

## Decision
Run evidence for any deliverable that ships through a build or serving step must exercise the production shape: the artifact bundled the way production bundles it, served the way production serves it, and rendered in a real browser. Evidence gathered only against the source shape does not establish that the deliverable works.

## Why
The Sentia take apart page passed its local evidence while production rendered nothing. Its capture exercised the source directly and never the production bundle, and the production bundler rewrote served code in a way that made the page's scripts fail before anything drew. The root cause and the fix are recorded in the Sentia take apart bundling order, which made the production shape the evidence of record.

## Consequences
A work order whose deliverable is bundled or served states its production shape checks in the spec: a clean bundle build with no local patches, and the built output served and verified rendered with zero console errors. Reviewers treat source shape only evidence as insufficient for such deliverables.
