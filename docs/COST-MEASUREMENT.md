# Cost Measurement

ANVIL records runtime token usage and computes cost from a sourced price table.
Missing usage stays unknown. A runtime's own dollar estimate is labeled
separately and is not presented as an invoice.

## Consumption controls

New projects include these adjustable starting settings in `anvil.yaml`:

```json
{
  "efficiency": {
    "max_packet_tokens": 12000,
    "max_runtime_turns": 16,
    "tool_output_tokens": 2000,
    "max_agent_calls": 32,
    "max_run_tokens": 250000,
    "require_usage": false
  }
}
```

Packet ceilings apply to every agent station. Initial packet size is a
character-based estimate, distinct from runtime consumption. Mandatory work
order and output contracts are not silently truncated: an oversized packet
stops the run. Backend packets omit interface design context. Stations are
instructed to read relevant ranges, bound command output, reuse upstream work
and keep their handoff concise.

The Claude wrapper passes `max_runtime_turns` to the CLI. `tool_output_tokens`
is still accepted and handed to the runtime as `ANVIL_TOOL_OUTPUT_TOKENS`, but
the supplied Claude wrapper does not apply it; it was the Codex wrapper's
setting, and that runtime was removed (decision 0008).
`max_agent_calls` counts station runtime invocations, including correction
attempts. A runtime invocation may contain multiple model/tool turns.

The runner checks token and call thresholds before starting another agent
station; wrappers check remaining allowance before a correction. Exhaustion
records `budget_exceeded`, retains consumed usage, refreshes the project page
and stops further agent work. These are thresholds between calls, not a
provider billing ceiling: an in-flight call can exceed them.
`require_usage: true` refuses further calls after unknown usage. With `false`,
execution can continue but totals are clearly marked partial.

Measurement does not prove a saving. Compare total usage across all attempts
per owner-accepted change, with the same tests and review quality, before
claiming the factory is cheaper.

## Configuration

Add a `prices` section to your `anvil.yaml`:

```json
{
  "version": 1,
  "prices": {
    "reasoning-strong": {
      "input_per_million": 3.0,
      "output_per_million": 15.0,
      "source": "anthropic-pricing-2024-01",
      "date_recorded": "2024-01-15"
    },
    "fast-builder": {
      "input_per_million": 1.0,
      "output_per_million": 5.0,
      "source": "anthropic-pricing-2024-01",
      "date_recorded": "2024-01-15"
    },
    "review-balanced": {
      "input_per_million": 2.0,
      "output_per_million": 10.0,
      "source": "anthropic-pricing-2024-01",
      "date_recorded": "2024-01-15"
    }
  },
  "stations": {},
  "runtime": {},
  "deploy": {}
}
```

## Required Fields

Every price entry must include:
- `input_per_million`: Price per million input tokens (USD)
- `output_per_million`: Price per million output tokens (USD)
- `source`: Where this price came from (e.g., "anthropic-pricing-2024-01")
- `date_recorded`: When this price was recorded (YYYY-MM-DD format)

The loader rejects any entry missing these fields.
Examples above are illustrative, not current model quotes. Cache usage also
requires `cached_input_per_million` and/or `cache_creation_per_million` when
those categories are nonzero. Missing cache rates leave cost unknown rather
than charging cached tokens at the ordinary input rate.

## How It Works

### Transcript Usage (S1)

The Claude wrapper reads the JSON result's usage. Each attempt writes scalar-only evidence to
`<station>.output.md.usage.json`, including failed calls, corrections and
timeouts. The executor preserves available evidence on errors and never
reuses a previous invocation's usage file. Missing timeout usage stays unknown.

Canonical input includes ordinary input, cache reads and cache creation.
Cached input is not added again to the total. Reasoning is a subset of output.
`token_usage` in each run report sums attempts and includes measurement
coverage and breakdowns by station and executed model. Unknown executed
models remain `unreported`; configured labels are not invented execution
evidence. Archived reports remain in project totals on reruns.

Runtime format reference: [Claude programmatic output](https://code.claude.com/docs/en/headless).

### Gateway Usage (S2)

For HTTP gateway executions, the executor reads the usage object from the gateway response when present (`prompt_tokens` and `completion_tokens`) and attaches it to the step.

### Unmeasured Steps (S3)

A step with no usage source, or an executed model with no price table entry, records:
- `cost`: null
- `cost_record.measured`: false
- `cost_record.reason`: explanation (e.g., "no usage reported" or "no price recorded for model 'xyz'")

### Cost Section (S4)

The run report gains a `cost` section:
```json
{
  "total": 3.5,
  "measured_steps": 2,
  "unmeasured_steps": 6
}
```

Where:
- `total`: Sum of measured steps only (never includes unmeasured)
- `measured_steps`: Count of steps with non-null cost
- `unmeasured_steps`: Count of executed steps with null cost

The swimlane shows the total with coverage:
```
**Cost**: $3.5000 (2 of 8 steps measured)
```

### Measurement and spending policy

Measurement alone does not approve or reject work. The spec, reviewer and
human gates retain their contracts. Separately configured execution limits
can stop a run with `budget_exceeded`; a stopped run does not earn approval.

## Example Step

A step with measured cost:
```json
{
  "station": "builder",
  "status": "executed",
  "cost": 3.5,
  "usage": {
    "input_tokens": 1000000,
    "output_tokens": 500000
  },
  "configured_model": "fast-builder",
  "executed_model": "fast-builder"
}
```

Calculation: `(1M * 1.0 + 500K * 5.0) / 1M = 3.5`

An unmeasured step:
```json
{
  "station": "intake",
  "status": "executed",
  "cost": null,
  "usage": null,
  "cost_record": {
    "measured": false,
    "reason": "no usage reported"
  }
}
```

## Keeping Prices Current

Price tables should be updated when:
- Model pricing changes
- New models are introduced
- You want to track pricing history

Each update should:
1. Add new entries with current prices
2. Update `date_recorded` to today's date
3. Update `source` to reference the pricing announcement

Old entries can be kept for historical runs or removed if no longer used.
