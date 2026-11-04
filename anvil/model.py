import re
from dataclasses import dataclass, field

KINDS = {"idea", "feature", "bug", "incident", "task", "content"}
VERDICTS = {"pass", "fail", "changes_requested"}
INTAKE_OUTCOMES = {"accepted", "rejected", "rescoped", "waiting_info"}
RISK_LEVELS = {"low", "medium", "high"}
SURFACES = {"ui", "security", "data", "payments", "deploy", "content", "api"}

def slugify(text):
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")

def validate_path_component(component, name):
    """Validate that a path component does not contain traversal attempts.

    Rejects components with path separators or parent directory references
    to prevent path traversal attacks (F3).

    SYNC: This function is duplicated in anvil/model.py and tools/claude_station.py.
    Both implementations must remain identical. The wrapper cannot import from anvil.model,
    so the copies must be kept synchronized manually. Any change to validation logic
    in either location must be mirrored to the other.
    See: tests/test_review_producer.py::TestRound3Finding2PathValidationDuplication
    """
    if not component or component == "unknown":
        raise ValueError(f"{name} is unknown or empty")
    # Reject path separators and parent references
    dangerous = ["/", "\\", "..", "~"]
    for pattern in dangerous:
        if pattern in component:
            raise ValueError(f"{name} contains dangerous path component: {pattern}")
    # Reject absolute paths
    if component.startswith("/") or (len(component) > 1 and component[1] == ":"):
        raise ValueError(f"{name} looks like an absolute path")
    return component

class IntakeValidationError(ValueError):
    """Raised when intake_outcome validation fails."""
    pass

class RiskValidationError(ValueError):
    """Raised when risk validation fails."""
    pass

def _validate_intake_outcome(outcome_dict):
    """Validate intake_outcome structure and required fields."""
    if not outcome_dict:
        return  # Empty dict is valid (no intake outcome yet)
    
    if not isinstance(outcome_dict, dict):
        raise IntakeValidationError(f"intake_outcome must be a dict, got {type(outcome_dict).__name__}")
    
    if "outcome" not in outcome_dict:
        raise IntakeValidationError("intake_outcome must have 'outcome' field")
    
    outcome = outcome_dict["outcome"]
    if outcome not in INTAKE_OUTCOMES:
        raise IntakeValidationError(
            f"Invalid outcome value: {outcome}. Must be one of {sorted(INTAKE_OUTCOMES)}"
        )
    
    # Validate required fields based on outcome
    if outcome == "rejected":
        if "reasons" not in outcome_dict:
            raise IntakeValidationError("rejected outcome requires 'reasons' field")
        if not isinstance(outcome_dict["reasons"], list) or not outcome_dict["reasons"]:
            raise IntakeValidationError("rejected outcome 'reasons' must be a non-empty list")
    
    elif outcome == "rescoped":
        if "rescoped_description" not in outcome_dict:
            raise IntakeValidationError("rescoped outcome requires 'rescoped_description' field")
        if not isinstance(outcome_dict["rescoped_description"], str) or not outcome_dict["rescoped_description"].strip():
            raise IntakeValidationError("rescoped outcome 'rescoped_description' must be a non-empty string")
    
    elif outcome == "waiting_info":
        if "questions" not in outcome_dict:
            raise IntakeValidationError("waiting_info outcome requires 'questions' field")
        if not isinstance(outcome_dict["questions"], list) or not outcome_dict["questions"]:
            raise IntakeValidationError("waiting_info outcome 'questions' must be a non-empty list")

def _validate_risk(risk_value):
    """Validate risk field value."""
    if risk_value is None:
        return  # None is valid (no risk rating yet)
    
    if not isinstance(risk_value, str):
        raise RiskValidationError(f"risk must be a string or None, got {type(risk_value).__name__}")
    
    if risk_value not in RISK_LEVELS:
        raise RiskValidationError(
            f"Invalid risk value: {risk_value}. Must be one of {sorted(RISK_LEVELS)} or None"
        )

def _validate_surfaces(surfaces_list):
    """Validate surfaces field values."""
    if not surfaces_list:
        return  # Empty list is valid
    
    if not isinstance(surfaces_list, list):
        raise ValueError(f"surfaces must be a list, got {type(surfaces_list).__name__}")
    
    invalid_surfaces = set(surfaces_list) - SURFACES
    if invalid_surfaces:
        raise ValueError(
            f"Invalid surface values: {sorted(invalid_surfaces)}. Must be from {sorted(SURFACES)}"
        )

@dataclass
class WorkOrder:
    id: str
    kind: str
    title: str
    source: str = "manual"
    description: str = ""
    risk_hints: list = field(default_factory=list)
    status: str = "new"
    intake_outcome: dict = field(default_factory=dict)
    risk: str = None
    surfaces: list = field(default_factory=list)
    knowledge_pack: str = None
    # Quality standard fields for visual deliverables
    anchors: list = field(default_factory=list)
    identity_reference: str = None
    identity_traits: list = field(default_factory=list)
    deliverable_set: list = field(default_factory=list)
    
    def __post_init__(self):
        if self.kind not in KINDS:
            raise ValueError(f"Invalid work order kind: {self.kind}")
        # Validate work order ID to prevent path traversal (F3)
        validate_path_component(self.id, "work_order_id")
        # Validate intake outcome, risk, and surfaces
        _validate_intake_outcome(self.intake_outcome)
        _validate_risk(self.risk)
        _validate_surfaces(self.surfaces)
    
    def __setattr__(self, name, value):
        # Validate fields on assignment to catch runtime modifications
        if name == "intake_outcome":
            _validate_intake_outcome(value)
        elif name == "risk":
            _validate_risk(value)
        elif name == "surfaces":
            _validate_surfaces(value)
        super().__setattr__(name, value)
    
    @classmethod
    def from_dict(cls, data):
        return cls(id=data["id"], kind=data["kind"], title=data["title"],
                   source=data.get("source", "manual"), description=data.get("description", ""),
                   risk_hints=list(data.get("risk_hints", [])), status=data.get("status", "new"),
                   intake_outcome=dict(data.get("intake_outcome", {})),
                   risk=data.get("risk"),
                   surfaces=list(data.get("surfaces", [])),
                   knowledge_pack=data.get("knowledge_pack"),
                   anchors=list(data.get("anchors", [])),
                   identity_reference=data.get("identity_reference"),
                   identity_traits=list(data.get("identity_traits", [])),
                   deliverable_set=list(data.get("deliverable_set", [])))
    def to_dict(self):
        result = {"id": self.id, "kind": self.kind, "title": self.title, "source": self.source,
                "description": self.description, "risk_hints": list(self.risk_hints), "status": self.status}
        if self.intake_outcome:
            result["intake_outcome"] = dict(self.intake_outcome)
        # Always include risk and surfaces fields (even if None or empty)
        result["risk"] = self.risk
        result["surfaces"] = list(self.surfaces) if self.surfaces else []
        if self.knowledge_pack:
            result["knowledge_pack"] = self.knowledge_pack
        # Quality standard fields
        if self.anchors:
            result["anchors"] = list(self.anchors)
        if self.identity_reference:
            result["identity_reference"] = self.identity_reference
        if self.identity_traits:
            result["identity_traits"] = list(self.identity_traits)
        if self.deliverable_set:
            result["deliverable_set"] = list(self.deliverable_set)
        return result

@dataclass
class Review:
    station: str
    verdict: str
    findings: list = field(default_factory=list)
    def __post_init__(self):
        if self.verdict not in VERDICTS:
            raise ValueError(f"Invalid review verdict: {self.verdict}")
    @classmethod
    def from_dict(cls, data):
        return cls(station=data["station"], verdict=data["verdict"], findings=list(data.get("findings", [])))
    def to_dict(self):
        return {"station": self.station, "verdict": self.verdict, "findings": list(self.findings)}
