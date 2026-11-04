# Cost Measurement

ANVIL measures and prices token usage when reported by runtimes. It never estimates: usage the runtime actually reported gets summed and priced from a labeled price table; usage nobody reported stays unmeasured and is recorded as unmeasured.

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

## How It Works

### Transcript Usage (S1)

For stations executed by a runtime that leaves session transcripts with token usage, the executor sums the usage attributable to the step's execution window and attaches it to the step.

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

### No Impact on Verdicts

Cost measurement never changes a verdict. The approver, the gates, and the human gate read nothing from the cost section. High costs never fail a run.

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
