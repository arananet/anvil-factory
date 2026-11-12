"""Runtime token evidence, without prompts, credentials or inferred free calls."""
import json
import math
import os
from pathlib import Path

TOKEN_FIELDS = ("input_tokens", "output_tokens", "cached_input_tokens",
                "cache_creation_input_tokens", "reasoning_tokens", "total_tokens")
DEFAULT_EFFICIENCY = {"max_packet_tokens": 12000, "max_runtime_turns": 16,
                      "tool_output_tokens": 2000, "max_agent_calls": 32,
                      "max_run_tokens": 250000, "require_usage": False}
EFFICIENCY_NOTE = (
    "\n## Consumption discipline\n\n"
    "Read the spec and the relevant upstream artifacts first. Search before opening files; "
    "read only the relevant ranges. Bound command output and summarize long test logs with "
    "failures and a path to the full log. Run focused checks while editing and the required "
    "project checks at handoff. Reuse valid upstream work. Keep the final handoff concise, "
    "with changed files, evidence and unresolved issues. Preserve the required output contract.\n"
)


def normalize_usage(usage, provider=None):
    """Canonical input includes cache; reasoning is a subset of output."""
    if not isinstance(usage, dict):
        return None
    input_key = "input_tokens" if "input_tokens" in usage else "prompt_tokens"
    output_key = "output_tokens" if "output_tokens" in usage else "completion_tokens"
    if input_key not in usage or output_key not in usage:
        return None
    details = usage.get("input_tokens_details") or usage.get("prompt_tokens_details") or {}
    output_details = usage.get("output_tokens_details") or usage.get("completion_tokens_details") or {}
    if not isinstance(details, dict) or not isinstance(output_details, dict):
        return None
    counts = {
        "input_tokens": usage[input_key], "output_tokens": usage[output_key],
        "cached_input_tokens": usage.get("cached_input_tokens", usage.get("cache_read_input_tokens", details.get("cached_tokens", 0))),
        "cache_creation_input_tokens": usage.get("cache_creation_input_tokens", 0),
        "reasoning_tokens": usage.get("reasoning_tokens", usage.get("reasoning_output_tokens", output_details.get("reasoning_tokens", 0))),
    }
    if any(isinstance(v, bool) or not isinstance(v, int) or v < 0 for v in counts.values()):
        return None
    if not usage.get("input_tokens_includes_cache") and (
            provider == "claude" or "cache_read_input_tokens" in usage or
            ("cache_creation_input_tokens" in usage and "cached_input_tokens" not in usage)):
        counts["input_tokens"] += counts["cached_input_tokens"] + counts["cache_creation_input_tokens"]
    if (counts["cached_input_tokens"] + counts["cache_creation_input_tokens"] > counts["input_tokens"]
            or counts["reasoning_tokens"] > counts["output_tokens"]):
        return None
    counts["total_tokens"] = counts["input_tokens"] + counts["output_tokens"]
    counts["input_tokens_includes_cache"] = True
    return counts


def sum_usage(items):
    measured = [u for item in items if (u := normalize_usage(item)) is not None]
    if not measured:
        return None
    result = {key: sum(u[key] for u in measured) for key in TOKEN_FIELDS}
    result["input_tokens_includes_cache"] = True
    return result


def parse_runtime_output(raw, provider):
    """Read provider envelopes, keeping free text separate from usage evidence."""
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8", errors="replace")
    raw = raw or ""
    result = {"output": raw, "usage": None, "runtime_cost_estimate_usd": None, "turns": None,
              "usage_complete": False}
    if provider == "claude":
        try:
            data = json.loads(raw)
        except (ValueError, TypeError):
            return result
        if not isinstance(data, dict) or data.get("type") != "result":
            return result
        result["output"] = str(data.get("result") or "")
        result["usage"] = normalize_usage(data.get("usage"), "claude")
        result["usage_complete"] = result["usage"] is not None
        cost = data.get("total_cost_usd")
        if isinstance(cost, (int, float)) and not isinstance(cost, bool) and math.isfinite(cost) and cost >= 0:
            result["runtime_cost_estimate_usd"] = cost
        turns = data.get("num_turns")
        if isinstance(turns, int) and not isinstance(turns, bool) and turns >= 0:
            result["turns"] = turns
        result["is_error"] = bool(data.get("is_error"))
        return result
    if provider == "copilot":
        # Envelope built by tools/copilot_runtime.py from the reply and the
        # usage statistics file; Copilot reports no turn count.
        try:
            data = json.loads(raw)
        except (ValueError, TypeError):
            return result
        if not isinstance(data, dict) or data.get("type") != "copilot_result":
            return result
        result["output"] = str(data.get("result") or "")
        result["usage"] = normalize_usage(data.get("usage"))
        result["usage_complete"] = result["usage"] is not None
        return result
    messages, usages, events = [], [], 0
    for line in raw.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if not isinstance(event, dict) or "type" not in event:
            continue
        events += 1
        if event["type"] in {"turn.completed", "turn.failed"}:
            usages.append(normalize_usage(event.get("usage")))
        item = event.get("item") or {}
        if event["type"] == "item.completed" and isinstance(item, dict) and item.get("type") == "agent_message":
            messages.append(str(item.get("text") or ""))
    if events:
        result["output"] = "\n".join(messages)
        result["usage"] = sum_usage(usages)
        result["turns"] = len(usages)
        result["usage_complete"] = bool(usages) and all(u is not None for u in usages)
    return result


class UsageRecorder:
    """One invocation ledger, persisted after every completed/failed attempt."""
    def __init__(self, path=None):
        path = path or os.environ.get("ANVIL_USAGE_PATH")
        self.path = Path(path) if path else None
        self.attempts = []

    def record(self, raw, provider, status, duration_ms, model):
        parsed = parse_runtime_output(raw, provider)
        if parsed.get("is_error"):
            status = "failed"
        self.attempts.append({
            "attempt": len(self.attempts) + 1, "status": status,
            "runtime": provider, "configured_model": model,
            "duration_ms": round(duration_ms, 3), "usage": parsed["usage"],
            "runtime_cost_estimate_usd": parsed["runtime_cost_estimate_usd"],
            "turns": parsed["turns"],
            "usage_complete": parsed["usage_complete"],
        })
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            data = self.summary()
            temporary = self.path.with_suffix(self.path.suffix + ".tmp")
            temporary.write_text(json.dumps(data, allow_nan=False, indent=2) + "\n", encoding="utf-8")
            temporary.replace(self.path)
        return parsed

    def summary(self):
        unknown = sum(not a["usage_complete"] for a in self.attempts)
        return {"schema": "anvil/usage@1", "attempts": self.attempts,
                "usage": sum_usage(a["usage"] for a in self.attempts),
                "measured_attempts": len(self.attempts) - unknown,
                "unmeasured_attempts": unknown, "complete": not unknown}

    def within_budget(self):
        cap = os.environ.get("ANVIL_MAX_STATION_TOKENS")
        usage = self.summary()["usage"]
        return not cap or usage is None or usage["total_tokens"] < int(cap)


def summarize_steps(steps):
    """Count attempts rather than successful handoffs; omit deterministic work."""
    calls = []
    deterministic = {"approver", "triage-human", "checks-gate", "verifier", "health-check", "loopback"}
    for step in steps:
        if step.get("attempts"):
            for attempt in step["attempts"]:
                calls.append(dict(attempt, station=step.get("station"),
                                  model=step.get("executed_model") or attempt.get("model") or "unreported"))
        elif (step.get("status") in {"executed", "failed"}
              and (step.get("executor") or step.get("usage") is not None or
                   (step.get("status") == "executed" and step.get("station") not in deterministic))):
            calls.append({"station": step.get("station"), "usage": step.get("usage"),
                          "usage_complete": step.get("usage_complete", True),
                          "model": step.get("executed_model") or "unreported"})
    totals = sum_usage(c.get("usage") for c in calls)
    measured = sum(normalize_usage(c.get("usage")) is not None and c.get("usage_complete", True) for c in calls)
    result = {key: totals[key] if totals else None for key in TOKEN_FIELDS}
    if not calls:
        result = dict.fromkeys(TOKEN_FIELDS, 0)
    result.update({"measured_calls": measured, "unmeasured_calls": len(calls) - measured,
                   "calls": len(calls), "retries": sum(max(0, len(s.get("attempts") or []) - 1) for s in steps),
                   "complete": measured == len(calls), "by_station": {}, "by_model": {}})
    for field, source in (("by_station", "station"), ("by_model", "model")):
        for call in calls:
            label = str(call.get(source) or "unreported")
            group = result[field].setdefault(label, {"calls": 0, "measured_calls": 0, "total_tokens": None})
            group["calls"] += 1
            usage = normalize_usage(call.get("usage"))
            if usage is not None:
                group["measured_calls"] += bool(call.get("usage_complete", True))
                group["total_tokens"] = (group["total_tokens"] or 0) + usage["total_tokens"]
    return result


def efficiency_config(config):
    value = config.get("efficiency") or {}
    if not isinstance(value, dict):
        raise ValueError("efficiency must be an object")
    for key in DEFAULT_EFFICIENCY:
        if key == "require_usage":
            if key in value and not isinstance(value[key], bool):
                raise ValueError("efficiency.require_usage must be boolean")
        elif key in value and (isinstance(value[key], bool) or not isinstance(value[key], int) or value[key] <= 0):
            raise ValueError(f"efficiency.{key} must be a positive integer")
    return value


def budget_reason(steps, limits):
    usage = summarize_steps(steps)
    if limits.get("max_agent_calls") and usage["calls"] >= limits["max_agent_calls"]:
        return "Agent call limit reached"
    if limits.get("max_run_tokens") and (usage["total_tokens"] or 0) >= limits["max_run_tokens"]:
        return "Run token threshold reached (checked between calls)"
    if limits.get("require_usage") and usage["unmeasured_calls"]:
        return "Usage required: a previous call did not report token usage"
    return None


def public_report(report):
    """A usage snapshot suitable for publishing; omit free text and paths."""
    result = {key: report[key] for key in ("work_order_id", "run_id", "title", "pipeline", "kind", "verdict",
                                          "human_required", "deployment_status", "loopbacks") if key in report}
    steps = []
    for raw in report.get("steps") or []:
        step = {key: raw[key] for key in ("station", "status", "duration_ms", "configured_model", "usage_complete",
                                          "executed_model", "measured_tokens", "budget", "budget_action", "cost") if key in raw}
        if raw.get("executor"):
            executor = raw["executor"]
            step["executor"] = {"kind": executor.get("kind", "unreported")} if isinstance(executor, dict) else "unreported"
        step["usage"] = normalize_usage(raw.get("usage"))
        if raw.get("attempts"):
            step["attempts"] = []
            for raw_attempt in raw["attempts"]:
                attempt = {key: raw_attempt[key] for key in ("attempt", "status", "runtime", "configured_model",
                                                              "duration_ms", "turns", "usage_complete",
                                                              "runtime_cost_estimate_usd") if key in raw_attempt}
                attempt["usage"] = normalize_usage(raw_attempt.get("usage"))
                step["attempts"].append(attempt)
        steps.append(step)
    result["steps"] = steps
    result["token_usage"] = summarize_steps(steps)
    return result
