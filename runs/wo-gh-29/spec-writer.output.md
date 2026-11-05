I revised `.openspec/specs/model-migration/spec.md` to cover the round 2 and round 3 findings. I didn't run the test suite. The file has no em or en dashes.

- **R3 (changed):** Handing the configured model to the runtime is now separate from recording it. `executed_model` comes only from runtime self-report, and is null when the runtime reports none. The dispatch wrapper self-reports what it actually dispatched. Every executor class accepts the model hand-off.
- **R6 (changed):** Price entries for the three new models are allowed only with a verifiable source and a current date. Otherwise the models stay unpriced and their steps record measured false. No invented or backdated sources.
- **R10 (new):** The runner resolves every label to a concrete model when it computes the step's effective model, using one total map:
  - `review-balanced`, `review-strong`, `writing-strong`, `fast-reader`, `media-gen` and `default` resolve to `claude-sonnet-5-5`.
  - `fast-builder` and `reasoning-strong` resolve to `claude-opus-5-5`.
  - Concrete models pass through unchanged.
  - The dispatcher still fails loudly on unknown values, and routing's tier vocabulary doesn't change.
- **R11 (new):** The OpenAI runtime builds its endpoint from `ANTHROPIC_BASE_URL`, or from `ANVIL_GATEWAY_OPENAI_URL` when set. It authenticates with `CF_AIG_TOKEN` and uses the bare id `gpt-6.1-sol`. It fails only when the gateway environment is absent, and it never prints the values.
- **Scenarios (new, S8 to S11):**
  - S8 covers the tier map and the concrete `configured_model` for routed reviewers.
  - S9 covers the OpenAI runtime's gateway-only configuration.
  - S10 covers the agent-execution S8 provenance tests passing unmodified.
  - S11 covers the price table containing no unsourced entries.
{"model": "claude-sonnet-5-5"}
