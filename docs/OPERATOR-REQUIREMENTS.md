# Operator credential and permission requirements

This document records the credentials an operator needs to run the factory and
the permissions each one must carry. Every fact here was verified in operation.
Each permission entry names the operation that proves it: the call that works
with the permission, and the failure observed without it.

Credentials are referenced by name and purpose only. No credential value, token
id, or secret appears in this document, and none may ever be added to it.

The factory depends on two stored credentials, both held in the Secure Vault
and reached through connector entries:

| Credential | Vault connector | Purpose |
|---|---|---|
| GitHub fine-grained personal access token | custom.github | Repository operations: contents, workflows, issues, settings, Actions secrets |
| Cloudflare user token | custom.cloudflare | Minting account tokens, AI Gateway access, Wrangler and deploys |

## GitHub

The GitHub credential is a fine-grained personal access token (PAT) held in the
Secure Vault via the custom.github connector.

### Repository permissions

| Permission | Operations it enables | Observed failure without it |
|---|---|---|
| Contents: read and write | File reads, pushes via the Git Database tooling, branch and tree operations | No isolated failure on record (granted from the start); every file and push operation depends on it |
| Actions: read and write | List workflow runs and jobs, read run outcomes, dispatch and re-fire workflows | 403 on the runs list and on logs; operators fall back to empty trigger commits to start runs |
| Issues: read and write | Create issues, comment run reports | 403 on issue creation and on the workflow's report comment step |
| Administration: read and write | PATCH repository (for the homepage), PUT topics | 403 on both, verified repeatedly |
| Secrets: write | PUT Actions secrets, used to load CF_AIG_TOKEN and provider keys per repo | No isolated failure on record; the PUT is the only way to load a secret, and values cannot be copied between repos |

Standing facts:

- **Actions secrets are write-only.** A secret's value can never be read back
  or copied between repos. Each repo that needs a secret needs its own load.
- **Branch merges go through the merges API.**
- **What the PAT cannot do.** It cannot manage webhooks, labels, or Pages
  enablement. These are 403s on record.
- **One hard limit with no API at all.** The repository social preview image
  can only be uploaded through the web Settings UI. No permission changes that;
  it is an owner step in the browser.

### Credential kind distinctions

- **A GitHub App client secret is not a personal access token.** It
  authenticates nothing by itself against the REST API. This was verified with
  a 401 against GitHub, against Cloudflare, and against the gateway. It cannot
  serve as the factory's GitHub credential.
- **Do not confuse the settings areas.** Developer settings, GitHub Apps,
  Credentials is a different mechanism from Personal access tokens,
  Fine-grained tokens. The vault credential lives in the second.
- **Where permissions are granted.** Permissions are granted per repository:
  the repo must be in the token's Repository access list, and the permission is
  set under Repository permissions. Editing any other credential changes
  nothing for the vault token.

## Cloudflare

The Cloudflare credential is held in the Secure Vault via the custom.cloudflare
connector.

### The vault credential

| Capability | Proving operation | Observed result |
|---|---|---|
| User token carrying API Tokens Edit | List and mint account tokens | Works |
| Read account permission groups | List permission groups | Works, 415 visible |
| List user tokens | List user tokens | 403, code 9109 (not available to this token) |

### AI Gateway authorization

The gateway is arananet-ai-gateway. It accepts account tokens.

- **Verified working shape (Anthropic route).** The token is sent as
  x-api-key AND as cf-aig-authorization Bearer. This is what the factory
  workflows set through ANTHROPIC_API_KEY (the x-api-key value) and
  ANTHROPIC_CUSTOM_HEADERS (the cf-aig-authorization header).
- **Placeholder shape: do not use it to judge a credential.** Setting x-api-key
  to a literal placeholder returns 401, AiGatewayError code 2009, even when the
  token itself is valid. This shape already produced one false diagnosis that a
  working credential was invalid.

### Per-repo gateway access

- Each repo that runs stations receives gateway access as the GitHub Actions
  secret CF_AIG_TOKEN.
- The standing pattern is a dedicated minted token per repo, minted with the
  vault credential and revocable in the Cloudflare panel.
- Because Actions secrets are write-only (see GitHub above), a new repo gets its
  own load via PUT Actions secrets; it cannot copy the value from another repo.

### Gateway settings on record

- Authentication: on
- BYOK-only: off
- Log collection: on
- Inference is billed through Unified Billing, with credit top-ups by the owner.

### Wrangler and deploys

Wrangler and deploys authenticate with the vault credential fetched in process
and passed as an environment token. Values are never printed and never
committed.

## Placement and care

### Where each credential lives

| Credential | Lives in | Delivered to consumers as |
|---|---|---|
| GitHub fine-grained PAT | Secure Vault, custom.github connector | Fetched in process by operator tooling |
| Cloudflare user token | Secure Vault, custom.cloudflare connector | Fetched in process; environment token for Wrangler and deploys |
| Per-repo gateway token | Minted with the Cloudflare vault credential | GitHub Actions secret CF_AIG_TOKEN in each repo that runs stations |

### What breaks without each permission

| Missing | What breaks |
|---|---|
| GitHub Contents | File reads, pushes, branch and tree operations |
| GitHub Actions | Runs list, logs, run outcomes, dispatch and re-fire (403); operators resort to empty trigger commits |
| GitHub Issues | Issue creation and the workflow's report comment step (403) |
| GitHub Administration | Homepage PATCH and topics PUT (403) |
| GitHub Secrets | Loading CF_AIG_TOKEN and provider keys into a repo |
| Cloudflare API Tokens Edit | Minting per-repo gateway tokens |
| CF_AIG_TOKEN in a repo | Station execution through the gateway in that repo |

### Never-again lessons

1. **Probe in the exact shape the consumer uses.** A credential is only
   declared invalid after a probe in the exact shape its consumer uses. The
   placeholder-shape probe already produced one false diagnosis.
2. **Check before asking.** Check for an existing reservation, ticket, or
   secret before asking the owner for a value. The values the factory needs
   are already held in, or mintable through, the vault connectors.
