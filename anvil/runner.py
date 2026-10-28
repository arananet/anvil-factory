import json, os, subprocess, time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from .model import WorkOrder, Review
from .gates import human_gate
from .approver import aggregate, needs_human
from .executor import ExecutorError

@dataclass
class RunReport:
    work_order_id: str
    pipeline: str
    steps: list = field(default_factory=list)
    verdict: str = ""
    human_required: bool = False
    max_loopbacks: int = 2
    loopbacks: int = 0
    deployment_status: str = None
    verify_results: list = field(default_factory=list)
    def to_dict(self):
        return {"work_order_id": self.work_order_id, "pipeline": self.pipeline,
                "steps": self.steps, "verdict": self.verdict, "human_required": self.human_required,
                "max_loopbacks": self.max_loopbacks, "loopbacks": self.loopbacks,
                "deployment_status": self.deployment_status, "verify_results": self.verify_results}

def parse_review(text, station_id):
    """Find a review JSON object in executor output and build a Review.

    Station prompts ask reviewers for JSON. Anything that does not parse to
    an object with a valid verdict returns None; the caller records that as
    review_parse_failed and the station contributes no review to the run.
    """
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
        if not isinstance(obj, dict) or "verdict" not in obj:
            continue
        try:
            return Review(station=str(obj.get("station") or station_id),
                          verdict=str(obj["verdict"]),
                          findings=[str(f) for f in obj.get("findings", [])])
        except ValueError:
            return None
    return None

def _run_shell(command, cwd, work_order_id, timeout):
    env = dict(os.environ)
    env["ANVIL_WORK_ORDER_ID"] = work_order_id
    try:
        proc = subprocess.run(command, shell=True, cwd=str(cwd), env=env,
                              capture_output=True, text=True, timeout=timeout)
        return proc.returncode, (proc.stdout or "") + (proc.stderr or "")
    except subprocess.TimeoutExpired:
        return None, f"Timed out after {timeout}s"

def _packet_text(station_id, prompt, work_order, steps):
    upstream = "\n".join(f"- {s['station']}: {s['status']}" for s in steps) or "- (none)"
    return (f"# Task packet: {station_id}\n\n## Station prompt\n\n{prompt}\n\n## Work order\n\n"
            f"- id: {work_order.id}\n- kind: {work_order.kind}\n- title: {work_order.title}\n"
            f"- source: {work_order.source}\n- description: {work_order.description}\n"
            f"- risk_hints: {', '.join(work_order.risk_hints)}\n- status: {work_order.status}\n\n"
            f"## Upstream steps\n\n{upstream}\n")

def run_pipeline(project_dir, pipeline, work_order, registry=None, max_loopbacks=2,
                 executor=None, deploy_cfg=None):
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
    execute_mode = executor is not None
    # Run scoped reviews: only reviews produced during this run feed the
    # approver. Standing project reviews under reviews/<slug>/ are the project
    # record read by `anvil check`, never inputs to a run.
    run_reviews = []
    run_findings = []
    deployment_status = None
    verify_results = []
    human_blocked = None  # decided at the triage step

    def write_envelope(station_id, next_station, artifact, status, extra=None):
        envelope = {"schema": "anvil/envelope@1", "from_station": station_id, "to_station": next_station,
                    "work_order_id": work_order.id, "artifact_path": artifact,
                    "status": status, "created_at": datetime.now(timezone.utc).isoformat()}
        if extra:
            envelope.update(extra)
        (envelopes_dir / f"{station_id}.envelope.json").write_text(json.dumps(envelope, indent=2) + "\n", encoding="utf-8")

    def packet_step(station, station_id):
        prompt = station.prompt if station and station.prompt else f"Station {station_id}: carry out your role for this work order."
        packet = run_dir / f"{station_id}.packet.md"
        packet.write_text(_packet_text(station_id, prompt, work_order, steps), encoding="utf-8")
        return packet

    for idx, station_id in enumerate(order):
        started = time.perf_counter()
        station = None
        if registry is not None and station_id in registry:
            station = registry.get(station_id)
        kind = station.kind if station else ("deterministic" if station_id in {"intake", "approver", "triage-human"} else "agent")
        status = "completed"
        detail = ""
        artifact = ""
        extra_envelope = {}
        step_usage = None
        deferred_verifier = None
        next_station = order[idx + 1] if idx + 1 < len(order) else None
        if station_id == "intake":
            detail = "Work order normalized"
            artifact = str(run_dir / "report.json")
        elif station_id == "approver":
            if run_reviews:
                verdict = aggregate(run_reviews)
            else:
                verdict = "no_reviews"
            detail = f"Approver verdict: {verdict}"
            artifact = str(run_dir / "report.json")
        elif station_id == "triage-human":
            hr = needs_human(work_order, verdict) if verdict else (human_gate(work_order) == "required")
            human_blocked = hr
            detail = f"Human review: {'required' if hr else 'not_required'}"
        elif station_id == "deployer" and execute_mode and deploy_cfg and deploy_cfg.get("command"):
            blocked = human_blocked if human_blocked is not None else needs_human(work_order, verdict)
            if verdict == "approved" and not blocked:
                timeout = int(deploy_cfg.get("timeout_seconds", 600))
                code, out = _run_shell(str(deploy_cfg.get("command", "")), project, work_order.id, timeout)
                out_file = run_dir / "deployer.output.md"
                out_file.write_text(out, encoding="utf-8")
                artifact = str(out_file)
                if code == 0:
                    status = "executed"
                    detail = "Deploy command executed"
                    deployment_status = "deployed_unverified"
                    # Deterministic verification gate, run by the spine before
                    # any later station (for example observer) is emitted.
                    vstarted = time.perf_counter()
                    v_failed = []
                    for vcmd in deploy_cfg.get("verify", []) or []:
                        vcode, vout = _run_shell(str(vcmd), project, work_order.id, timeout)
                        ok = vcode == 0
                        verify_results.append({"command": str(vcmd), "status": "pass" if ok else "fail",
                                               "exit_code": vcode, "output": vout[-2000:]})
                        if not ok:
                            v_failed.append(str(vcmd))
                    if v_failed:
                        findings_file = run_dir / "verify-findings.md"
                        lines = ["# Verify findings", "",
                                 f"Work order: {work_order.id}",
                                 f"Deployment status: {deployment_status}", "",
                                 "The deploy command ran, but verification failed. The deploy is NOT verified.", ""]
                        for r in verify_results:
                            if r["status"] == "fail":
                                lines.append(f"## Failing command: {r['command']}")
                                lines.append("")
                                lines.append("```")
                                lines.append(r["output"])
                                lines.append("```")
                                lines.append("")
                        findings_file.write_text("\n".join(lines), encoding="utf-8")
                    else:
                        deployment_status = "deployed_verified"
                    vstep = {"station": "verifier",
                             "status": "executed" if not v_failed else "failed",
                             "detail": ("Verification passed for all commands" if not v_failed
                                        else f"Verification failed: {', '.join(v_failed)}"),
                             "duration_ms": round((time.perf_counter() - vstarted) * 1000, 3),
                             "cost": None,
                             "artifacts": [str(run_dir / "verify-findings.md")] if v_failed else []}
                    deferred_verifier = vstep
                else:
                    status = "failed"
                    detail = f"Deploy command failed with exit code {code}"
                    deployment_status = "deploy_failed"
            else:
                packet = packet_step(station, station_id)
                status = "packet_ready"
                detail = f"Deploy skipped (verdict: {verdict or 'pending'}, human gate {'blocks' if blocked else 'open'}); packet written to {packet}"
                artifact = str(packet)
        elif kind in {"deterministic", "gate"}:
            detail = "Deterministic step executed"
        elif station_id == "deployer":
            # The deployer never runs through a generic executor: without a
            # deploy config and an approved, unblocked run it stays a packet.
            packet = packet_step(station, station_id)
            status = "packet_ready"
            detail = f"Packet written to {packet}"
            artifact = str(packet)
        elif execute_mode:
            packet = packet_step(station, station_id)
            packet_text = packet.read_text(encoding="utf-8")
            output_file = run_dir / f"{station_id}.output.md"
            try:
                result = executor.execute(packet_text, station_id, packet_path=packet,
                                          output_path=output_file, cwd=project)
                output_text = result.get("output", "") if isinstance(result, dict) else str(result)
                usage = result.get("usage") if isinstance(result, dict) else None
                output_file.write_text(output_text, encoding="utf-8")
                status = "executed"
                detail = f"Executed by {executor.name}; output written to {output_file}"
                artifact = str(output_file)
                extra_envelope = {"executor": executor.name}
                if isinstance(usage, dict):
                    step_usage = usage
                    extra_envelope["usage"] = usage
                    tokens = {k: usage[k] for k in usage if "token" in k}
                    if tokens:
                        extra_envelope["tokens"] = tokens
                if station_id.startswith("reviewer"):
                    review = parse_review(output_text, station_id)
                    if review is not None:
                        run_reviews.append(review)
                        run_findings.extend(review.findings)
                        extra_envelope["review"] = review.to_dict()
                    else:
                        extra_envelope["review_parse_failed"] = True
                        detail += "; review output did not parse as a review JSON"
            except ExecutorError as exc:
                status = "failed"
                detail = f"Executor failed: {exc}"
                artifact = str(packet)
                extra_envelope = {"executor": getattr(executor, "name", "unknown"), "error": str(exc)}
        else:
            packet = packet_step(station, station_id)
            status = "packet_ready"
            detail = f"Packet written to {packet}"
            artifact = str(packet)
        duration_ms = round((time.perf_counter() - started) * 1000, 3)
        step = {"station": station_id, "status": status, "detail": detail, "duration_ms": duration_ms,
                "cost": None, "artifacts": [artifact] if artifact else []}
        if step_usage is not None:
            step["usage"] = step_usage
            if isinstance(step_usage.get("cost"), (int, float)):
                step["cost"] = step_usage["cost"]
        steps.append(step)
        write_envelope(station_id, next_station, artifact or str(run_dir / "report.json"), status, extra_envelope)
        if deferred_verifier is not None:
            steps.append(deferred_verifier)
            write_envelope("verifier", next_station,
                           deferred_verifier["artifacts"][0] if deferred_verifier["artifacts"] else str(run_dir / "report.json"),
                           deferred_verifier["status"])
        # Loopback right after approver when aggregation fails
        if station_id == "approver" and verdict in {"rejected", "changes_requested"} and loopbacks < max_loopbacks:
            loopbacks += 1
            # Spec failures return to spec-writer, implementation failures to builder.
            return_to = "spec-writer" if any("spec" in str(f).lower() and "missing" in str(f).lower() for f in run_findings) else "builder"
            reason = "; ".join(run_findings) if run_findings else f"Approver verdict: {verdict}"
            steps.append({"station": station_id, "status": "loopback", "return_to": return_to,
                          "detail": f"Loopback to {return_to}: {reason}", "reason": reason,
                          "duration_ms": 0.0, "cost": None, "artifacts": []})
    if not verdict:
        verdict = "packet_ready"
    human_required = needs_human(work_order, verdict) if verdict in {"approved", "rejected", "changes_requested", "no_reviews"} else (human_gate(work_order) == "required")
    report = RunReport(work_order_id=work_order.id, pipeline=pipeline.name, steps=steps, verdict=verdict,
                       human_required=human_required, max_loopbacks=max_loopbacks, loopbacks=loopbacks,
                       deployment_status=deployment_status, verify_results=verify_results)
    (run_dir / "report.json").write_text(json.dumps(report.to_dict(), indent=2) + "\n", encoding="utf-8")
    # Swimlane
    lines = ["# Swimlane", "", "Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.", "",
             "| Station | Status | Duration ms | Artifacts | Cost |", "|---|---|---|---|---|"]
    for s in steps:
        arts = ", ".join(s.get("artifacts", [])) or "-"
        cost = s.get("cost")
        lines.append(f"| {s['station']} | {s['status']} | {s.get('duration_ms', 0)} | {arts} | {cost if cost is not None else 'null'} |")
    if deployment_status is not None:
        lines.append("")
        lines.append(f"Deployment: {deployment_status}")
    if verify_results:
        lines.append("")
        lines.append("Verification:")
        for r in verify_results:
            lines.append(f"- {r['status']}: {r['command']}")
    (run_dir / "swimlane.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report

run = run_pipeline
