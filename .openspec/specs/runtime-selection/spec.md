# Runtime Selection: Claude Code through the gateway, or GitHub Copilot CLI

Status: implemented
Slug: runtime-selection

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose
The factory reached its models one way: Claude Code in print mode through the Cloudflare AI Gateway, paid through the gateway credential. The owner wants a second way to reach the same Anthropic models, GitHub Copilot CLI with the GitHub account, chosen by one variable, with the first way unchanged and still the default.

This is one station contract over two runtimes, not two contracts: station permissions, the review file check and its one correction, the usage ledger and the model provenance rules are the wrapper's and stay the same whichever runtime is selected. Decision 0008 stands: Anthropic models only.

Provenance: owner-authored work outside the line (decision 0006, record 0010).

## Requirements

- R1, one variable. ANVIL_RUNTIME selects the runtime: claude-gateway (the default when unset) or copilot. An unknown value fails the station before any model call, naming the accepted values. runtime.provider in anvil.yaml sets a project's default; the variable wins over it.
- R2, the Copilot command. A station runs as `copilot -p <packet> --model <model>` in the project tree, non-interactive, silent, with the built-in MCP servers disabled and the credential variables withheld from the shell commands the agent runs. A producing station is allowed every tool. Any other station is allowed to read, to run commands, and to write only inside its own run directory; nothing allows it to edit the tree it judges.
- R3, model names. Factory model names are mapped to Copilot's by writing the trailing version with a dot (claude-opus-5-5 to claude-opus-5.5). ANVIL_COPILOT_MODELS, or runtime.copilot_models in anvil.yaml, states names explicitly and wins over the rule. The run report keeps the factory name.
- R4, same station contract. Under copilot a reviewer's review file is validated and corrected once exactly as under the gateway, a missing CLI or a failing run fails the station loudly, and no credential is printed.
- R5, usage. Token usage is read from the file Copilot writes with --usage-output-file: the per model breakdown, summed once. A missing or unfamiliar file leaves usage unknown; it is never guessed. The raw statistics file is kept beside the station output.
- R6, the workflow follows the variable. anvil-line.yml reads the repository variable ANVIL_RUNTIME, installs only that runtime's CLI, and the smoke test probes that runtime. The copilot runtime takes its credential from the secret COPILOT_GITHUB_TOKEN.

Guardrails: Python standard library only. The copilot runtime has no turn limit equivalent to max_runtime_turns; ANVIL_COPILOT_MAX_AI_CREDITS caps a station's session instead when set.

## Scenarios

### Scenario: One variable chooses the runtime
- S1: Given ANVIL_RUNTIME unset, then the runtime is claude-gateway; given copilot, then copilot; given an unknown value, then the station fails before any model call.
- S2: Given the copilot runtime, when the command is built for a producing station and for a reviewer, then the producer is allowed every tool and the reviewer only read, shell and writes inside its run directory, and the model name is Copilot's.

### Scenario: Stations keep their contract
- S3: Given the copilot runtime, when the dispatcher runs a builder and a reviewer whose first review file is malformed, then the builder's change lands in the project tree, the reviewer is corrected once and its review is valid, and a failing or missing CLI fails the station.
- S4: Given the usage statistics file, then tokens are read from the per model breakdown and counted once; given no file or an unfamiliar one, then usage is unknown.

### Scenario: Configuration
- S5: Given runtime.provider in anvil.yaml, then stations get that runtime; given the variable as well, then the variable wins.
- S6: Given the workflow and the smoke test, then both act on the runtime the variable names.
