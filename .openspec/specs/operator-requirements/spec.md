# Operator credential and permission requirements

## Problem

Operating this factory depends on two stored credentials: a fine-grained
GitHub personal access token and a Cloudflare credential, both held in the
Secure Vault and reached through connector entries. Which permission each
factory operation needs has so far been learned by trial and error and
recorded only in operator memory and chat. The failure modes are expensive:
a missing permission surfaces as a 403 deep inside a run (a report comment
that cannot post, a runs list that cannot be read), one wrong probe shape
produced a false diagnosis that a working credential was invalid, and one
settings detour confused a GitHub App client secret with a personal access
token. The owner ordered on 2026-11-04 that these requirements be
documented in the factory itself, so they are never forgotten or
re-derived.

## Requirements

R1. A new document at docs/OPERATOR-REQUIREMENTS.md records the operator
credential and permission requirements for GitHub, Cloudflare, and the
Secure Vault. Every fact in it is one verified in operation, and each
permission entry names the operation that proves it (the call that works
with the permission and the observed failure without it).

R2. The GitHub section covers the fine-grained PAT held in the Secure
Vault via the custom.github connector, permission by permission:
Contents read and write (file reads, pushes via the Git Database tooling,
branch and tree operations); Actions read and write (list workflow runs
and jobs, read run outcomes, dispatch and re-fire workflows; without it,
403 on the runs list and logs, and operators fall back to empty trigger
commits); Issues read and write (create issues and comment run reports;
without it, 403 on issue creation and on the workflow's report comment
step); Administration read and write (PATCH repository for the homepage
and PUT topics; without it, 403 on both, verified repeatedly); Secrets
write (PUT Actions secrets, used to load CF_AIG_TOKEN and provider keys
per repo), with the standing fact that Actions secrets are write-only: a
secret's value can never be read back or copied between repos, so each
repo needs its own load. The section also records that branch merges go
through the merges API, that the PAT cannot manage webhooks, labels, or
Pages enablement (403s on record), and the one hard limit with no API at
all: the repository social preview image can only be uploaded through the
web Settings UI, and no permission changes that.

R3. The GitHub section records the credential kind distinctions: a GitHub
App client secret is not a personal access token and authenticates
nothing by itself against the REST API (verified 401 against GitHub,
Cloudflare, and the gateway); the settings areas must not be confused
(Developer settings, GitHub Apps, Credentials is a different mechanism
from Personal access tokens, Fine-grained tokens). Permissions are
granted per repository in the token's Repository access list, under
Repository permissions; editing any other credential changes nothing for
the vault token.

R4. The Cloudflare section covers the credential held in the Secure Vault
via the custom.cloudflare connector: it is a user token carrying API
Tokens Edit; it can list and mint account tokens and read account
permission groups (415 visible), and it cannot list user tokens (403,
code 9109). AI Gateway (arananet-ai-gateway) authorization: the gateway
accepts account tokens; the verified working shape for the Anthropic
route sends the token as x-api-key AND as cf-aig-authorization Bearer,
which is what the factory workflows set via ANTHROPIC_API_KEY and
ANTHROPIC_CUSTOM_HEADERS; the placeholder shape (x-api-key set to a
literal placeholder) returns 401, AiGatewayError code 2009. Per-repo
gateway access is delivered as the GitHub Actions secret CF_AIG_TOKEN in
each repo that runs stations; a dedicated minted token per repo is the
standing pattern, revocable in the Cloudflare panel. Gateway settings on
record: authentication on, BYOK-only off, log collection on; inference
billed through Unified Billing with credit top-ups by the owner. Wrangler
and deploys authenticate with the vault credential fetched in process and
passed as an environment token.

R5. The document closes with placement and care: where each credential
lives (the Secure Vault connector entries), what breaks without each
permission, and the two never-again lessons. One: a credential is only
declared invalid after a probe in the exact shape its consumer uses; the
placeholder-shape probe already produced one false diagnosis. Two: check
for an existing reservation, ticket, or secret before asking the owner
for a value; the values the factory needs are already held or mintable
through the vault connectors.

R6. No credential value, token id, or secret appears in the document or
in any other file this order produces. Credentials are referenced by
name and purpose only. This is verified by a scan of the produced files
for credential-shaped strings, which must find nothing.

R7. The README Documentation table gains a row for the new document, and
CHANGELOG gains an Unreleased entry. Nothing else changes: no code, no
tests created or modified, no other docs edited. The full factory suite
stays green.

## Acceptance scenarios

S1. A reader who has never operated the factory can answer, from the
document alone, which GitHub permission a given API operation needs and
what failure to expect without it, for every operation listed in R2.

S2. A reader can state why a GitHub App client secret cannot be used as
the factory's GitHub credential, and where the PAT's permissions are
actually granted.

S3. A reader can state the exact gateway authorization shape the factory
workflows use, why the placeholder shape must not be used to judge a
credential, and how a new repo receives its gateway access.

S4. A scan of every file the run produces finds no credential value, no
token id, and no secret; the document refers to credentials by name and
purpose only.
