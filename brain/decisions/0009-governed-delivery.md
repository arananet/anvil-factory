# 0009: The line is operable and governable on Cloudflare and GitHub first

Status: recorded 2026-11-12 at the owner's request.

## Context

The owner's direction is idea to impact: the factory builds and deploys, and
later deploys to AKS with a namespace per thing it creates. Asked whether the
factory made sense for enterprise use, the assessment was that its record was
forensic, not operational, and that approvals, containment and environments
were not governed. The owner asked for those gaps to be closed now, for the
platforms the factory already deploys to.

## Decision

- A run is observable while it runs (state.json), emits structured events
  (events.jsonl) and can export them (webhook, OpenTelemetry trace).
- An approval is an identity checked against a policy, read from the
  operator's checkout.
- Stations and project checks never hold deploy or repository credentials;
  a container sandbox is available and optional.
- Every work order gets its own preview environment before review, named
  after the order; production stays behind the approver and the human gate.
  This is the same shape the AKS plan needs: the preview name is the
  namespace name, and the preview, cleanup and provision commands are where
  a namespace is created, deployed to and removed.

Spec: .openspec/specs/governed-delivery/spec.md.

## Not decided here

- Prices. Cost stays unmeasured until the owner records sourced prices.
- Network egress control for stations.
- AKS itself.

## Provenance

Owner-authored work outside the line (decision 0006). The line neither
produced nor reviewed it. The Cloudflare commands and the Docker sandbox were
not exercised against real services when this was recorded.
