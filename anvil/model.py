import re
from dataclasses import dataclass, field

KINDS = {"idea", "feature", "bug", "incident", "task"}
VERDICTS = {"pass", "fail", "changes_requested"}

def slugify(text):
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")

@dataclass
class WorkOrder:
    id: str
    kind: str
    title: str
    source: str = "manual"
    description: str = ""
    risk_hints: list = field(default_factory=list)
    status: str = "new"
    def __post_init__(self):
        if self.kind not in KINDS:
            raise ValueError(f"Invalid work order kind: {self.kind}")
    @classmethod
    def from_dict(cls, data):
        return cls(id=data["id"], kind=data["kind"], title=data["title"],
                   source=data.get("source", "manual"), description=data.get("description", ""),
                   risk_hints=list(data.get("risk_hints", [])), status=data.get("status", "new"))
    def to_dict(self):
        return {"id": self.id, "kind": self.kind, "title": self.title, "source": self.source,
                "description": self.description, "risk_hints": list(self.risk_hints), "status": self.status}

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
