"""Bounded supervisor: reorganization inside a verified envelope.

The supervisor watches the run record between runs and proposes pipeline
recompositions. It cannot invent roles, cannot edit gates, risk hints or
triage rules (those are deterministic code), and cannot apply anything:
a proposal becomes active only when a human points anvil.json or a run
at it. Deterministic code decides three things the supervisor never
touches:

1. Which stall signals exist (detect_stalls reads report.json files).
2. Whether a proposal is a legal pipeline (the existing validator).
3. Whether it obeys the constitution: intake, approver and triage-human
   must be present, and the reviewer set may grow or reorder but never
   shrink below the pipeline it would replace.
"""

import json
from pathlib import Path

from .executor import ExecutorError
from .pipeline import Pipeline, load_pipeline

REQUIRED_STATIONS = ["intake", "approver", "triage-human"]


def _load_reports(project):
    """All readable run reports, oldest first by (mtime, folder name)."""
    runs_dir = Path(project) / "runs"
    reports = []
    if runs_dir.is_dir():
        for folder in sorted(p for p in runs_dir.iterdir() if p.is_dir()):
            report_file = folder / "report.json"
            if not report_file.exists():
                continue
            try:
                data = json.loads(report_file.read_text(encoding="utf-8"))
            except Exception:
                continue
            if isinstance(data, dict):
                reports.append((folder.name, data, report_file.stat().st_mtime))
    reports.sort(key=lambda item: (item[2], item[0]))
    return reports


def detect_stalls(project):
    """Deterministic stall signals from the run record.

    Each signal: {kind, detail, evidence: [run ids]}.
    """
    reports = _load_reports(project)
    signals = []
    if not reports:
        return signals
    fails = {}
    for run_id, data, _ in reports:
        counted = ((data.get("decision") or {}).get("approver") or {}).get("reviews_counted") or []
        for review in counted:
            if isinstance(review, dict) and review.get("verdict") == "fail" and review.get("station"):
                ids = fails.setdefault(review["station"], [])
                if run_id not in ids:
                    ids.append(run_id)
    for station in sorted(fails):
        ids = fails[station]
        if len(ids) >= 2:
            signals.append({"kind": "reviewer_fail_repeated",
                            "detail": f"Reviewer {station} returned verdict fail in {len(ids)} runs.",
                            "evidence": ids})
    latest_id, latest, _ = reports[-1]
    max_loopbacks = latest.get("max_loopbacks") or 0
    if max_loopbacks and (latest.get("loopbacks") or 0) >= max_loopbacks:
        signals.append({"kind": "loopbacks_exhausted",
                        "detail": (f"Latest run {latest_id} used all {max_loopbacks} loopbacks "
                                   "without resolving the findings."),
                        "evidence": [latest_id]})
    last_three = reports[-3:]
    no_review_ids = [run_id for run_id, data, _ in last_three if data.get("verdict") == "no_reviews"]
    if len(no_review_ids) >= 2:
        signals.append({"kind": "no_reviews_repeated",
                        "detail": (f"{len(no_review_ids)} of the last {len(last_three)} runs "
                                   "ended with verdict no_reviews."),
                        "evidence": no_review_ids})
    if latest.get("deployment_status") == "deployed_unverified":
        signals.append({"kind": "deployed_unverified",
                        "detail": (f"Latest run {latest_id} deployed but verification failed "
                                   "(deployment_status deployed_unverified)."),
                        "evidence": [latest_id]})
    return signals


def default_pipeline_name(project):
    """The project's configured default pipeline, falling back to sdlc-default."""
    config = Path(project) / "anvil.json"
    if config.exists():
        try:
            name = json.loads(config.read_text(encoding="utf-8")).get("pipeline")
        except Exception:
            name = None
        if name:
            return str(name)
    return "sdlc-default"


def _factory_pipelines_dir():
    return Path(__file__).resolve().parent.parent / "pipelines"


def load_base_pipeline(project, name, known_stations):
    """Load the pipeline a proposal would replace: project copy, else factory."""
    for candidate in (Path(project) / "pipelines" / f"{name}.json",
                      _factory_pipelines_dir() / f"{name}.json"):
        if candidate.exists():
            return load_pipeline(candidate, known_stations=known_stations)
    return None


def parse_proposal(text):
    """Return the first JSON object in the text that carries a pipeline, or None."""
    if not text:
        return None
    decoder = json.JSONDecoder()
    for idx, ch in enumerate(text):
        if ch != "{":
            continue
        try:
            obj, _ = decoder.raw_decode(text[idx:])
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and isinstance(obj.get("pipeline"), dict):
            return obj
    return None


def _pipeline_stages(proposal):
    stages = (proposal.get("pipeline") or {}).get("stages")
    return stages if isinstance(stages, list) else []


def validate_proposal(proposal, registry, base_pipeline):
    """Every failed check as a human readable line. Empty list means valid.

    Runs the existing pipeline validator first (structure and catalog
    membership), then the constitution checks. The supervisor cannot
    amend any of this; it lives in code on purpose.
    """
    failures = []
    if not isinstance(proposal, dict):
        return ["proposal is not a JSON object"]
    if not isinstance(proposal.get("pipeline"), dict):
        return ["proposal has no pipeline object"]
    name = str(proposal.get("name") or "proposal")
    pipe = Pipeline(name=name, stages=_pipeline_stages(proposal))
    try:
        pipe.validate(known_stations=set(registry.ids()))
    except ValueError as exc:
        failures.append(f"pipeline validation: {exc}")
    try:
        order = pipe.topological_order()
    except Exception:
        order = []
    for required in REQUIRED_STATIONS:
        if required not in order:
            failures.append(f"constitution: proposal is missing required station {required}")
    if base_pipeline is not None:
        base_reviewers = {s for s in base_pipeline.topological_order() if s.startswith("reviewer")}
        proposed_reviewers = {s for s in order if s.startswith("reviewer")}
        for missing in sorted(base_reviewers - proposed_reviewers):
            failures.append(f"constitution: proposal drops reviewer {missing} "
                            f"that the base pipeline {base_pipeline.name} has")
    return failures


def _supervisor_packet(prompt, project, signals, reports):
    signal_lines = "\n".join(
        f"- {s['kind']}: {s['detail']} (evidence: {', '.join(s['evidence'])})" for s in signals)
    run_lines = "\n".join(
        f"- {run_id}: verdict {data.get('verdict')}, loopbacks {data.get('loopbacks', 0)}/"
        f"{data.get('max_loopbacks', 0)}, deployment {data.get('deployment_status')}"
        for run_id, data, _ in reports) or "- (none)"
    return (f"# Task packet: supervisor\n\n## Station prompt\n\n{prompt}\n\n"
            f"## Stall signals\n\n{signal_lines}\n\n"
            f"## Run record summary\n\n{run_lines}\n\n"
            "## Your task\n\n"
            "Answer with exactly one JSON proposal object: "
            '{"name": "...", "pipeline": {"name": "...", "stages": [...]}, '
            '"rationale": "...", "addresses": "<signal kind>"}\n')


def supervise(project, registry, executor=None):
    """Detect stalls and, when any fire, run the supervisor station.

    Packet mode writes the packet and a proposal work order. Execute mode
    additionally sends the packet to the configured runtime and validates
    the returned proposal. Returns a result dict describing what happened;
    with no signals nothing is written and action is "none".
    """
    project = Path(project)
    signals = detect_stalls(project)
    result = {"signals": signals, "action": "none"}
    if not signals:
        return result
    station = registry.get("supervisor") if "supervisor" in registry else None
    prompt = station.prompt if station is not None and station.prompt else (
        "Station supervisor: propose one bounded pipeline recomposition.")
    reports = _load_reports(project)
    packet_text = _supervisor_packet(prompt, project, signals, reports)
    work_orders = project / "work-orders"
    work_orders.mkdir(parents=True, exist_ok=True)
    packet_path = work_orders / "supervisor.packet.md"
    packet_path.write_text(packet_text, encoding="utf-8")
    first = signals[0]
    work_order = {
        "id": "wo-supervisor-proposal",
        "kind": "task",
        "title": f"Supervisor proposal: address {first['kind']}",
        "source": "supervisor",
        "description": ("Stall signals detected in the run record: "
                        + "; ".join(f"{s['kind']} ({', '.join(s['evidence'])})" for s in signals)
                        + ". See work-orders/supervisor.packet.md."),
        "risk_hints": [],
        "status": "new",
    }
    work_order_path = work_orders / "supervisor-proposal.json"
    work_order_path.write_text(json.dumps(work_order, indent=2) + "\n", encoding="utf-8")
    result.update({"action": "packet", "packet": str(packet_path),
                   "work_order": str(work_order_path)})
    if executor is None:
        return result
    output_path = work_orders / "supervisor.output.md"
    # The command executor prefers a non empty {output} file over stdout.
    # That file is this call's answer file, so clear any stale one from a
    # previous supervise run first, or the old answer would be re-read.
    if output_path.exists():
        output_path.unlink()
    try:
        executed = executor.execute(packet_text, "supervisor", packet_path=packet_path,
                                    output_path=output_path, cwd=project)
        output_text = executed.get("output", "") if isinstance(executed, dict) else str(executed)
    except ExecutorError as exc:
        result.update({"action": "execute_failed", "error": str(exc)})
        return result
    output_path.write_text(output_text, encoding="utf-8")
    proposal = parse_proposal(output_text)
    if proposal is None:
        result.update({"action": "no_proposal", "output": str(output_path)})
        return result
    name = str(proposal.get("name") or "supervisor-proposal")
    base_name = default_pipeline_name(project)
    base = load_base_pipeline(project, base_name, set(registry.ids()))
    failures = validate_proposal(proposal, registry, base)
    proposals_dir = project / "pipelines" / "proposals"
    proposals_dir.mkdir(parents=True, exist_ok=True)
    if failures:
        rejected_path = proposals_dir / f"rejected-{name}.json"
        rejected_path.write_text(json.dumps(proposal, indent=2) + "\n", encoding="utf-8")
        lines = [f"# Rejected supervisor proposal: {name}", "",
                 "This proposal failed validation. It was not accepted, must not "
                 "be used, and nothing was applied.", "",
                 "## Failed checks"]
        lines += [f"- {failure}" for failure in failures]
        lines += ["", "## Proposal as received", "",
                  f"Addresses: {proposal.get('addresses', '')}", "",
                  f"Rationale: {proposal.get('rationale', '')}"]
        rejected_md = proposals_dir / "REJECTED.md"
        rejected_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
        result.update({"action": "rejected", "proposal": str(rejected_path),
                       "rejection": str(rejected_md), "failures": failures})
        return result
    accepted = {"name": name, "stages": _pipeline_stages(proposal)}
    accepted_path = proposals_dir / f"{name}.json"
    accepted_path.write_text(json.dumps(accepted, indent=2) + "\n", encoding="utf-8")
    addressed = str(proposal.get("addresses") or first["kind"])
    evidence = next((s["evidence"] for s in signals if s["kind"] == addressed), first["evidence"])
    lines = [f"# Supervisor proposal: {name}", "",
             "Status: proposed, not applied. Nothing auto applies.",
             "",
             "## Rationale", "", str(proposal.get("rationale") or ""), "",
             "## Signal addressed", "",
             f"{addressed} (evidence runs: {', '.join(evidence)})", "",
             "## Validation", "",
             f"Pipeline validation passed against the station catalog, and the "
             f"constitution checks passed against the base pipeline {base_name}: "
             "intake, approver and triage-human present; the reviewer set covers "
             "every reviewer the base pipeline has; no station outside the catalog.",
             "",
             "## How to apply", "",
             f"Point anvil.json at pipelines/proposals/{name}.json, or run "
             f"`anvil run --pipeline pipelines/proposals/{name}.json`. Until a "
             "human does that, this proposal changes nothing."]
    proposal_md = proposals_dir / "PROPOSAL.md"
    proposal_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    result.update({"action": "accepted", "proposal": str(accepted_path),
                   "proposal_doc": str(proposal_md), "failures": []})
    return result
