import json, time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from .model import WorkOrder, Review, slugify
from .gates import human_gate
from .approver import aggregate, needs_human

@dataclass
class RunReport:
    work_order_id: str
    pipeline: str
    steps: list = field(default_factory=list)
    verdict: str = ""
    human_required: bool = False
    max_loopbacks: int = 2
    loopbacks: int = 0
    def to_dict(self):
        return {"work_order_id": self.work_order_id, "pipeline": self.pipeline,
                "steps": self.steps, "verdict": self.verdict, "human_required": self.human_required,
                "max_loopbacks": self.max_loopbacks, "loopbacks": self.loopbacks}

def _load_reviews(project):
    reviews = []
    findings = []
    rroot = Path(project) / "reviews"
    if rroot.is_dir():
        for f in sorted(rroot.rglob("*.json")):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                reviews.append(Review.from_dict(data))
                findings.extend(data.get("findings", []))
            except Exception:
                pass
    return reviews, findings

def run_pipeline(project_dir, pipeline, work_order, registry=None, max_loopbacks=2):
    project = Path(project_dir)
    if isinstance(work_order, dict):
        work_order = WorkOrder.from_dict(work_order)
    run_dir = project / "runs" / work_order.id
    envelopes_dir = run_dir / "envelopes"
    run_dir.mkdir(parents=True, exist_ok=True)
    envelopes_dir.mkdir(parents=True, exist_ok=True)
    steps = []
    verdict = ""
    loopbacks = 0
    order = pipeline.topological_order()
    reviews, findings = _load_reviews(project)
    for idx, station_id in enumerate(order):
        started = time.perf_counter()
        station = None
        if registry is not None and station_id in registry:
            station = registry.get(station_id)
        kind = station.kind if station else ("deterministic" if station_id in {"intake", "approver", "triage-human"} else "agent")
        status = "completed"
        detail = ""
        artifact = ""
        if station_id == "intake":
            detail = "Work order normalized"
            artifact = str(run_dir / "report.json")
        elif station_id == "approver":
            if reviews:
                verdict = aggregate(reviews)
            else:
                verdict = "no_reviews"
            detail = f"Approver verdict: {verdict}"
            artifact = str(run_dir / "report.json")
        elif station_id == "triage-human":
            hr = needs_human(work_order, verdict) if verdict else (human_gate(work_order) == "required")
            detail = f"Human review: {'required' if hr else 'not_required'}"
        elif kind in {"deterministic", "gate"}:
            detail = "Deterministic step executed"
        else:
            prompt = station.prompt if station and station.prompt else f"Station {station_id}: carry out your role for this work order."
            packet = run_dir / f"{station_id}.packet.md"
            packet.write_text(f"# Task packet: {station_id}\n\n## Station prompt\n\n{prompt}\n\n## Work order\n\n- id: {work_order.id}\n- kind: {work_order.kind}\n- title: {work_order.title}\n- source: {work_order.source}\n- description: {work_order.description}\n- risk_hints: {', '.join(work_order.risk_hints)}\n- status: {work_order.status}\n", encoding="utf-8")
            status = "packet_ready"
            detail = f"Packet written to {packet}"
            artifact = str(packet)
        duration_ms = round((time.perf_counter() - started) * 1000, 3)
        step = {"station": station_id, "status": status, "detail": detail, "duration_ms": duration_ms, "cost": None, "artifacts": [artifact] if artifact else []}
        steps.append(step)
        # Envelope for completed or packet_ready steps
        next_station = order[idx + 1] if idx + 1 < len(order) else None
        envelope = {"schema": "anvil/envelope@1", "from_station": station_id, "to_station": next_station,
                    "work_order_id": work_order.id, "artifact_path": artifact or str(run_dir / "report.json"),
                    "created_at": datetime.now(timezone.utc).isoformat()}
        (envelopes_dir / f"{station_id}.envelope.json").write_text(json.dumps(envelope, indent=2) + "\n", encoding="utf-8")
        # Loopback right after approver when aggregation fails
        if station_id == "approver" and verdict in {"rejected", "changes_requested"} and loopbacks < max_loopbacks:
            loopbacks += 1
            # Spec failures return to spec-writer, implementation failures to builder.
            # Review failures are treated as implementation failures unless a finding names the spec.
            return_to = "spec-writer" if any("spec" in str(f).lower() and "missing" in str(f).lower() for f in findings) else "builder"
            reason = "; ".join(findings) if findings else f"Approver verdict: {verdict}"
            steps.append({"station": station_id, "status": "loopback", "return_to": return_to,
                          "detail": f"Loopback to {return_to}: {reason}", "reason": reason,
                          "duration_ms": 0.0, "cost": None, "artifacts": []})
    if not verdict:
        verdict = "packet_ready"
    human_required = needs_human(work_order, verdict) if verdict in {"approved", "rejected", "changes_requested"} else (human_gate(work_order) == "required")
    report = RunReport(work_order_id=work_order.id, pipeline=pipeline.name, steps=steps, verdict=verdict, human_required=human_required, max_loopbacks=max_loopbacks, loopbacks=loopbacks)
    (run_dir / "report.json").write_text(json.dumps(report.to_dict(), indent=2) + "\n", encoding="utf-8")
    # Swimlane
    lines = ["# Swimlane", "", "Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.", "",
             "| Station | Status | Duration ms | Artifacts | Cost |", "|---|---|---|---|---|"]
    for s in steps:
        arts = ", ".join(s.get("artifacts", [])) or "-"
        lines.append(f"| {s['station']} | {s['status']} | {s.get('duration_ms', 0)} | {arts} | null |")
    (run_dir / "swimlane.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report

run = run_pipeline
