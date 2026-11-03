"""
Risk and surface routing for reviewer selection and model assignment.

This module implements the routing capability that selects which reviewers run
and which models are used based on work order risk level and surfaces.

Spec: .openspec/specs/risk-routing/spec.md
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set


# Model policy ceiling: defines the maximum model that can be assigned to each station kind
# Routing may reduce below this ceiling but never exceed it
MODEL_POLICY = {
    "reviewer": "review-balanced",  # Standard reviewer model
    "reviewer-strong": "review-strong",  # Strong model for security reviews
    "builder": "fast-builder",  # Builder model
    "builder-strong": "reasoning-strong",  # Strong builder model
    "writer": "writing-strong",  # Writer model
    "designer": "media-gen",  # Design/UI model
}

# Model hierarchy for ceiling validation (lower index = cheaper/weaker)
MODEL_HIERARCHY = [
    "fast-reader",
    "review-cheap",
    "review-balanced",
    "fast-builder",
    "writing-strong",
    "reasoning-strong",
    "review-strong",
    "media-gen",
]


@dataclass
class RoutingRecord:
    """Record of routing decisions for a run."""
    selected_reviewers: List[str] = field(default_factory=list)
    routed_out: List[Dict[str, str]] = field(default_factory=list)
    selected_models: Dict[str, str] = field(default_factory=dict)
    reason: str = ""

    def to_dict(self):
        return {
            "selected_reviewers": list(self.selected_reviewers),
            "routed_out": list(self.routed_out),
            "selected_models": dict(self.selected_models),
            "reason": self.reason,
        }


class RoutingConfigError(Exception):
    """Raised when routing configuration violates model policy ceiling."""
    pass


def _model_rank(model_name: str) -> int:
    """Return the rank of a model in the hierarchy (lower = cheaper/weaker)."""
    try:
        return MODEL_HIERARCHY.index(model_name)
    except ValueError:
        # Unknown models are treated as highest rank (most expensive)
        return len(MODEL_HIERARCHY)


def validate_model_assignment(station_kind: str, assigned_model: str, policy_model: str):
    """Validate that assigned model does not exceed policy ceiling.

    Args:
        station_kind: The kind of station (e.g., "reviewer-spec")
        assigned_model: The model being assigned
        policy_model: The policy ceiling model

    Raises:
        RoutingConfigError: If assigned model exceeds policy ceiling
    """
    assigned_rank = _model_rank(assigned_model)
    policy_rank = _model_rank(policy_model)

    if assigned_rank > policy_rank:
        raise RoutingConfigError(
            f"Station '{station_kind}' configured with model '{assigned_model}' "
            f"exceeds policy ceiling '{policy_model}' for reviewer stations"
        )


def load_routing_config(project_dir: Path) -> Dict:
    """Load routing configuration from project.

    Loads factory defaults and applies project overrides if present.

    Args:
        project_dir: Path to project directory

    Returns:
        Routing configuration dict
    """
    # Factory default routing configuration
    default_config = {
        "reduced_panel_reviewers": ["reviewer-spec", "reviewer-tests"],
        "full_panel_reviewers": [
            "reviewer-spec",
            "reviewer-security",
            "reviewer-tests",
            "reviewer-architecture",
            "reviewer-design"
        ],
        "models": {
            "reduced": "review-cheap",  # Cheaper model for reduced panel
            "standard": "review-balanced",  # Standard reviewer model
            "strong": "review-strong",  # Strong model for security
        },
        "policy_ceilings": {
            "reviewer": "review-balanced",
            "reviewer-security": "review-strong",
        }
    }

    # Try to load project overrides
    project_config_path = project_dir / ".anvil" / "routing.json"
    if project_config_path.exists():
        try:
            project_config = json.loads(project_config_path.read_text(encoding="utf-8"))
            # Merge with defaults
            if isinstance(project_config, dict):
                default_config.update(project_config)
        except (json.JSONDecodeError, OSError):
            pass

    return default_config


def route_reviewers(
    work_order,
    pipeline_reviewers: List[str],
    project_dir: Path
) -> RoutingRecord:
    """Route reviewer selection and model assignment based on risk and surfaces.

    Implements the routing rules from the spec:
    - Low risk + no UI + no security -> reduced panel at cheaper model
    - Security surface -> always keep reviewer-security at strong model
    - UI surface -> keep reviewer-design when present
    - Medium risk -> full panel at policy models
    - High risk -> full panel at policy models (no reduction)
    - Null risk -> full panel at policy models (default for unrated)

    Args:
        work_order: WorkOrder with risk and surfaces fields
        pipeline_reviewers: List of reviewer station IDs from pipeline
        project_dir: Path to project directory

    Returns:
        RoutingRecord with selected reviewers, models, and reasons
    """
    config = load_routing_config(project_dir)

    risk = work_order.risk
    surfaces = set(work_order.surfaces or [])

    # Start with empty selections
    selected = set()
    routed_out = []
    models = {}
    reasons = []

    # Available reviewers from the pipeline
    available_reviewers = set(pipeline_reviewers)

    # Get configured reviewer sets
    reduced_panel = set(config["reduced_panel_reviewers"])
    full_panel = set(config["full_panel_reviewers"])

    # Apply routing rules
    if risk is None:
        # S3: Null risk -> full panel at policy models (default for unrated)
        selected = available_reviewers & full_panel
        for reviewer in selected:
            if reviewer == "reviewer-security":
                models[reviewer] = config["models"]["strong"]
            else:
                models[reviewer] = config["models"]["standard"]
        reasons.append("Default applied: work is unrated, using full panel at policy models")

    elif risk == "low" and "ui" not in surfaces and "security" not in surfaces:
        # S1: Low risk + no UI + no security -> reduced panel at cheaper model
        selected = available_reviewers & reduced_panel
        for reviewer in selected:
            models[reviewer] = config["models"]["reduced"]
        reasons.append("Low risk with no UI and no security surface: reduced panel at cheaper model")

        # Record routed out reviewers
        for reviewer in available_reviewers - selected:
            routed_out.append({
                "reviewer": reviewer,
                "reason": "Routed out by low risk rule (not in reduced panel)"
            })

    elif risk == "low" and ("ui" in surfaces or "security" in surfaces):
        # Low risk with UI or security -> start with reduced panel, then add required reviewers
        selected = available_reviewers & reduced_panel
        for reviewer in selected:
            models[reviewer] = config["models"]["reduced"]

        # S2: Security surface -> always keep reviewer-security at strong model
        if "security" in surfaces and "reviewer-security" in available_reviewers:
            selected.add("reviewer-security")
            models["reviewer-security"] = config["models"]["strong"]

        # S3: UI surface -> keep reviewer-design when present
        if "ui" in surfaces and "reviewer-design" in available_reviewers:
            selected.add("reviewer-design")
            models["reviewer-design"] = config["models"]["standard"]

        rule_parts = ["Low risk"]
        if "security" in surfaces:
            rule_parts.append("security surface keeps reviewer-security")
        if "ui" in surfaces:
            rule_parts.append("UI surface keeps reviewer-design")
        reasons.append("; ".join(rule_parts))

        # Record routed out reviewers
        for reviewer in available_reviewers - selected:
            routed_out.append({
                "reviewer": reviewer,
                "reason": "Routed out by low risk rule with surface exceptions"
            })

    elif risk == "medium":
        # S3: Medium risk -> full panel at policy models
        selected = available_reviewers & full_panel
        for reviewer in selected:
            if reviewer == "reviewer-security":
                models[reviewer] = config["models"]["strong"]
            else:
                models[reviewer] = config["models"]["standard"]
        reasons.append("Medium risk: full panel at policy models")

    elif risk == "high":
        # S3: High risk -> full panel at policy models (explicit no reduction)
        selected = available_reviewers & full_panel
        for reviewer in selected:
            if reviewer == "reviewer-security":
                models[reviewer] = config["models"]["strong"]
            else:
                models[reviewer] = config["models"]["standard"]
        reasons.append("High risk: full panel at policy models, no reduction applied")

    else:
        # Unknown risk level -> default to full panel
        selected = available_reviewers & full_panel
        for reviewer in selected:
            if reviewer == "reviewer-security":
                models[reviewer] = config["models"]["strong"]
            else:
                models[reviewer] = config["models"]["standard"]
        reasons.append(f"Unknown risk level '{risk}': defaulting to full panel at policy models")

    # S2: Always ensure security reviewer is at strong model if selected
    if "security" in surfaces and "reviewer-security" in selected:
        models["reviewer-security"] = config["models"]["strong"]
        if not any("security" in r for r in reasons):
            reasons.append("Security surface: reviewer-security at strong model")

    # Create routing record - preserve pipeline order
    selected_in_order = [r for r in pipeline_reviewers if r in selected]

    record = RoutingRecord(
        selected_reviewers=selected_in_order,
        routed_out=routed_out,
        selected_models=models,
        reason="; ".join(reasons)
    )

    return record


def write_routing_record(run_dir: Path, record: RoutingRecord):
    """Write routing record to run directory.

    Args:
        run_dir: Path to run directory
        record: RoutingRecord to write
    """
    routing_file = run_dir / "routing.json"
    routing_file.write_text(json.dumps(record.to_dict(), indent=2) + "\n", encoding="utf-8")


def render_routing_section(record: RoutingRecord) -> str:
    """Render routing section for report.md.

    Args:
        record: RoutingRecord to render

    Returns:
        Markdown text for routing section
    """
    lines = ["## Routing", ""]

    # Reason
    lines.append(f"**Decision**: {record.reason}")
    lines.append("")

    # Selected reviewers
    lines.append(f"**Selected reviewers** ({len(record.selected_reviewers)}):")
    for reviewer in record.selected_reviewers:
        model = record.selected_models.get(reviewer, "default")
        lines.append(f"- {reviewer} (model: {model})")
    lines.append("")

    # Routed out reviewers
    if record.routed_out:
        lines.append(f"**Routed out** ({len(record.routed_out)}):")
        for entry in record.routed_out:
            lines.append(f"- {entry['reviewer']}: {entry['reason']}")
        lines.append("")

    return "\n".join(lines)


def routing_swimlane_summary(record: RoutingRecord) -> str:
    """Generate one-line routing summary for swimlane.

    Args:
        record: RoutingRecord to summarize

    Returns:
        One-line summary string
    """
    panel_size = len(record.selected_reviewers)
    routed_out_count = len(record.routed_out)

    if routed_out_count > 0:
        return f"Routing: {panel_size} reviewers (reduced panel, {routed_out_count} routed out)"
    else:
        return f"Routing: {panel_size} reviewers (full panel)"
