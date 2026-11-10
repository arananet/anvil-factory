"""Cost measurement for pipeline runs.

Measures and prices token usage when reported by runtimes. Never estimates:
usage the runtime actually reported gets summed and priced from a labeled
price table; usage nobody reported stays unmeasured and is recorded as
unmeasured.

Price table format in anvil.yaml:
{
  "prices": {
    "model-name": {
      "input_per_million": 1.0,
      "output_per_million": 5.0,
      "source": "anthropic-pricing-2024-01",
      "date_recorded": "2024-01-15"
    }
  }
}
"""
import math
from .telemetry import normalize_usage


def validate_price_table(price_table):
    """Validate that all price table entries have required fields.

    Args:
        price_table: Dict mapping model names to price entries

    Returns:
        List of validation errors (empty if valid)
    """
    if not isinstance(price_table, dict):
        return ["Price table must be a dict"]

    errors = []
    for model_name, entry in price_table.items():
        if not isinstance(entry, dict):
            errors.append(f"Price entry for '{model_name}' must be a dict")
            continue

        # Check required fields
        required = ["input_per_million", "output_per_million", "source", "date_recorded"]
        for field in required:
            if field not in entry:
                errors.append(f"Price entry for '{model_name}' missing required field '{field}'")

        # Validate numeric fields
        for field in ("input_per_million", "output_per_million", "cached_input_per_million", "cache_creation_per_million"):
            if field in entry:
                value = entry[field]
                if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
                    errors.append(f"Price entry for '{model_name}' field '{field}' must be finite and nonnegative")

    return errors


def load_price_table(config):
    """Load and validate price table from configuration.

    Args:
        config: Configuration dict from anvil.yaml

    Returns:
        Validated price table dict, or empty dict if not configured

    Raises:
        ValueError: If price table is present but invalid
    """
    if not isinstance(config, dict):
        return {}

    price_table = config.get("prices", {})
    if not price_table:
        return {}

    errors = validate_price_table(price_table)
    if errors:
        raise ValueError(f"Invalid price table: {'; '.join(errors)}")

    return price_table


def calculate_cost(usage, model, price_table):
    """Calculate cost from usage and model price.

    Args:
        usage: Dict with token usage from executor
        model: Model name to look up in price table
        price_table: Dict mapping model names to prices

    Returns:
        Dict with:
        - cost: float amount (or None if unmeasured)
        - measured: bool
        - reason: str explaining why unmeasured (if applicable)
        - usage: dict with normalized token counts
        - model: str model name
    """
    normalized = normalize_usage(usage)
    if normalized is None:
        return {
            "cost": None,
            "measured": False,
            "reason": "no usage reported",
            "usage": None,
            "model": model
        }

    # Normalize usage keys - support both transcript format (input_tokens/output_tokens)
    # and gateway format (prompt_tokens/completion_tokens)
    input_tokens = normalized["input_tokens"]
    output_tokens = normalized["output_tokens"]

    # If both are 0 or None, but usage dict exists, it's measured as 0 cost
    if input_tokens == 0 and output_tokens == 0:
        return {
            "cost": 0.0,
            "measured": True,
            "reason": None,
            "usage": {"input_tokens": 0, "output_tokens": 0},
            "model": model
        }

    # Look up model price
    if not model or model not in price_table:
        return {
            "cost": None,
            "measured": False,
            "reason": f"no price recorded for model '{model}'" if model else "no model specified",
            "usage": {"input_tokens": input_tokens, "output_tokens": output_tokens},
            "model": model
        }

    price_entry = price_table[model]
    cached = normalized["cached_input_tokens"]
    created = normalized["cache_creation_input_tokens"]
    for count, rate in ((cached, "cached_input_per_million"), (created, "cache_creation_per_million")):
        if count and rate not in price_entry:
            return {"cost": None, "measured": False, "reason": f"no {rate} recorded for model '{model}'",
                    "usage": normalized, "model": model}
    input_price = price_entry["input_per_million"]
    output_price = price_entry["output_per_million"]

    # Calculate cost: (tokens * price_per_million) / 1_000_000
    cost = ((input_tokens - cached - created) * input_price + output_tokens * output_price
            + cached * price_entry.get("cached_input_per_million", 0)
            + created * price_entry.get("cache_creation_per_million", 0)) / 1_000_000

    return {
        "cost": cost,
        "measured": True,
        "reason": None,
        "usage": {"input_tokens": input_tokens, "output_tokens": output_tokens},
        "model": model
    }


def build_cost_section(steps):
    """Build cost section from steps.

    Args:
        steps: List of step dicts with cost field

    Returns:
        Dict with:
        - total: sum of measured step costs
        - measured_steps: count of steps with non-null cost
        - unmeasured_steps: count of executed steps with null cost
    """
    measured_steps = [s for s in steps if s.get("cost") is not None]
    # Count unmeasured as executed steps with null cost
    executed_steps = [s for s in steps if s.get("status") == "executed"]
    unmeasured_steps = [s for s in executed_steps if s.get("cost") is None]

    total = sum(s["cost"] for s in measured_steps)

    return {
        "total": total,
        "measured_steps": len(measured_steps),
        "unmeasured_steps": len(unmeasured_steps)
    }
