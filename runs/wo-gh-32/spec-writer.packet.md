# Task packet: spec-writer

## Station prompt

# Spec Writer

## Role
Write or revise an OpenSpec spec from a work order.

## Inputs
- work order
- brain

## Outputs
- spec

## Rules
- Work only from the inputs listed above and the work order in the packet.
- Produce the output as a file in the repo, not as chat text.
- If the inputs are not enough, say what is missing instead of guessing.
- Never approve your own work. Approval belongs to a different station.
- Keep the change small and mapped to a spec scenario where one applies.


## Work order

- id: wo-gh-32
- kind: task
- title: Document the operator credential and permission requirements (GitHub, Cloudflare, vault)
- source: github-issue
- description: Implement the spec in .openspec/specs/operator-requirements/spec.md. Owner's order 2026-11-04: document in this repo the operator credential and permission requirements for running the factory (GitHub, Cloudflare, and the Secure Vault), so they are never forgotten or re-derived by trial and error. Documentation only.

Build, per the spec requirements:

1. Create docs/OPERATOR-REQUIREMENTS.md recording ONLY facts verified in operation, each permission entry stated with the operation that proves it (the call that works with the permission and the observed failure without it). Sections: GitHub, Cloudflare, and placement and care.

GitHub section (fine-grained PAT held in the Secure Vault via the custom.github connector): Contents read and write (file reads, pushes via the Git Database tooling, branch and tree operations). Actions read and write (list workflow runs and jobs, read run outcomes, dispatch and re-fire workflows; without it, 403 on the runs list and logs and operators fall back to empty trigger commits). Issues read and write (create issues and comment run reports; without it, 403 on issue creation and on the workflow's report comment step). Administration read and write (PATCH repository for the homepage and PUT topics; without it, 403 on both, verified repeatedly). Secrets write (PUT Actions secrets, used to load CF_AIG_TOKEN and provider keys per repo), with the standing fact that Actions secrets are write-only: a secret's value can never be read back or copied between repos, so each repo needs its own load. Branch merges go through the merges API. The PAT cannot manage webhooks, labels, or Pages enablement (403s on record). One hard limit with no API at all: the repository social preview image can only be uploaded through the web Settings UI, and no permission changes that.

Credential kind distinctions (same section): a GitHub App client secret is NOT a personal access token and authenticates nothing by itself against the REST API (verified 401 against GitHub, Cloudflare, and the gateway). Do not confuse Developer settings, GitHub Apps, Credentials with Personal access tokens, Fine-grained tokens; reference the distinction only, naming no app and no value. Permissions are granted per repository in the token's Repository access list, under Repository permissions; editing any other credential changes nothing for the vault token.

Cloudflare section (credential in the Secure Vault via the custom.cloudflare connector): the vault credential is a user token carrying API Tokens Edit; it can list and mint account tokens and read account permission groups (415 visible), and cannot list user tokens (403, code 9109). AI Gateway (arananet-ai-gateway) authorization: the gateway accepts account tokens; the verified working shape for the Anthropic route sends the token as x-api-key AND as cf-aig-authorization Bearer, which is what the factory workflows set via ANTHROPIC_API_KEY and ANTHROPIC_CUSTOM_HEADERS; the placeholder shape (x-api-key set to a literal placeholder) returns 401, AiGatewayError code 2009, and already produced one false diagnosis. Per-repo gateway access is delivered as the GitHub Actions secret CF_AIG_TOKEN in each repo that runs stations; a dedicated minted token per repo is the standing pattern, revocable in the Cloudflare panel. Gateway settings on record: authentication on, BYOK-only off, log collection on; inference billed through Unified Billing with credit top-ups by the owner. Wrangler and deploys authenticate with the vault credential fetched in process and passed as an environment token; values are never printed or committed.

Placement and care (closing section): where each credential lives (the Secure Vault connector entries), what breaks without each permission, and the two never-again lessons: probe a credential in the exact shape its consumer uses before declaring it invalid, and check for an existing reservation, ticket or secret before asking the owner for a value.

2. Add a row for docs/OPERATOR-REQUIREMENTS.md to the README Documentation table, in the table's existing style.

3. Add a CHANGELOG Unreleased entry.

HARD CONSTRAINT: no credential value, token id, or secret appears in the document or in any other file this order produces; credentials are referenced by name and purpose only (spec R6, scenario S4).

Guardrails: the builder may only create docs/OPERATOR-REQUIREMENTS.md and edit README.md (Documentation table row only) and CHANGELOG.md (Unreleased entry only). No code changes. Do not create, modify, or delete any file under tests/ (the checks gate protects base ref test files). The review parsing contract, the producer mechanism and the checks gate base ref behavior are frozen. Full suite green. No em dash or en dash characters in any produced file.

GitHub issue: https://github.com/arananet/anvil-factory/issues/32

OPERATOR CORRECTION (round 2). Round 1 never reached a station: intake validation rejected the staged work order with "Invalid surface values: ['docs']. Must be from ['api', 'content', 'data', 'deploy', 'payments', 'security', 'ui']", so the run produced no report. The surface is corrected to 'content' (this is documentation work). Nothing else in this order changes; the guardrails stand.
- risk_hints: 
- status: new

## Upstream steps

- intake: executed
