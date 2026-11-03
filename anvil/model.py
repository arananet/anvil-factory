import re
from dataclasses import dataclass, field

KINDS = {"idea", "feature", "bug", "incident", "task", "content"}
VERDICTS = {"pass", "fail", "changes_requested"}

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

@dataclass
class WorkOrder:
    id: str
    kind: str
    title: str
    source: str = "manual"
    description: str = ""
    risk_hints: list = field(default_factory=list)
    status: str = "new"
    spec_path: str = ""
    evidence_images: list = field(default_factory=list)
    def __post_init__(self):
        if self.kind not in KINDS:
            raise ValueError(f"Invalid work order kind: {self.kind}")
        # Validate work order ID to prevent path traversal (F3)
        validate_path_component(self.id, "work_order_id")
    @classmethod
    def from_dict(cls, data):
        return cls(id=data["id"], kind=data["kind"], title=data["title"],
                   source=data.get("source", "manual"), description=data.get("description", ""),
                   risk_hints=list(data.get("risk_hints", [])), status=data.get("status", "new"),
                   spec_path=data.get("spec_path", ""), evidence_images=list(data.get("evidence_images", [])))
    def to_dict(self):
        return {"id": self.id, "kind": self.kind, "title": self.title, "source": self.source,
                "description": self.description, "risk_hints": list(self.risk_hints), "status": self.status,
                "spec_path": self.spec_path, "evidence_images": list(self.evidence_images)}

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
