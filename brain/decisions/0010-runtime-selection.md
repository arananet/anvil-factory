# 0010: Two ways to reach the same models, one variable

Status: accepted 2026-11-12, by the owner's order.

## Decision

The stations reach their Anthropic models through the runtime the variable
ANVIL_RUNTIME names: claude-gateway (Claude Code through the Cloudflare AI
Gateway, the default, unchanged) or copilot (GitHub Copilot CLI with the
GitHub account). Decision 0008 stands: one family of models, no OpenAI route.
This adds a second door to the same models, not a second model family.

One wrapper holds the station contract for both: permissions by station, the
review file check and its single correction, the usage ledger, loud failure.
The run report keeps the factory's model names whichever runtime ran.

## Why

Billing and access: a team that already pays for Copilot can run the line on
that account without operating a gateway, and the gateway stays for those who
want its logging and caching.

## Consequences

- Executed model evidence is weaker under copilot: the dispatcher reports the
  configured model after a successful run, and the wrapper does not read back
  which model Copilot actually served.
- No turn limit under copilot; an AI credit cap is available instead.
- Not yet run authenticated: the dotted model names and the shape of the
  usage statistics file are confirmed on the first real run.

## Provenance

Owner-authored work outside the line (decision 0006). The line neither
produced nor reviewed this change.
