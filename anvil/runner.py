import json, os, shlex, subprocess, time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from .model import WorkOrder, Review
from .config import default_model, load_anvil_config
from .brain import packet_learnings_section
from .design import packet_design_section, load_design_system
from .capture import capture_breakpoints, packet_rendered_evidence_section
from .gates import human_gate, checks_gate, resolve_base_ref_config, _run_shell
from .approver import aggregate, needs_human, aggregate_explained, needs_human_explained, matched_risk_hints, RISK_SCAN_ORDER
from .executor import ExecutorError
from .routing import route_reviewers, write_routing_record, render_routing_section, routing_swimlane_summary
from .cost import load_price_table, calculate_cost, build_cost_section
from .knowledge import (
    load_knowledge_pack,
    packet_knowledge_section,
    get_project_product_type,
    get_design_model_from_routing,
    KnowledgeValidationError,
)
from .quality import (
    packet_quality_charter_section,
    packet_anchor_section,
    is_visual_run,
)

def _sanitize_control_chars(text):
    """Sanitize control characters from text to prevent injection.

    Removes or replaces control characters that could be used for
    injection attacks (F3).
    """
    if not isinstance(text, str):
        return str(text)
    # Remove control characters (except tab and newline which are safe in markdown)
    import re
    # Keep \t (tab) and \n (newline), remove other control chars
    sanitized = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    return sanitized

def _escape_markdown(text):
    """Escape markdown special characters to prevent content injection.

    Escapes characters that could be used to inject markdown formatting,
    links, or other content into generated reports.
    """
    if not isinstance(text, str):
        return str(text)
    # Escape markdown special characters
    special_chars = ['\\', '`', '*', '_', '{', '}', '[', ']', '(', ')', '#', '+', '-', '.', '!', '|', '<', '>']
    result = text
    for char in special_chars:
        result = result.replace(char, '\\' + char)
    return result

@dataclass
class RunReport:
    work_order_id: str
    pipeline: str
    title: str = ""
    kind: str = ""
    steps: list = field(default_factory=list)
    verdict: str = ""
    human_required: bool = False
    max_loopbacks: int = 2
    loopbacks: int = 0
    deployment_status: str = None
    verify_results: list = field(default_factory=list)
    risk_hints: list = field(default_factory=list)
    decision: dict = field(default_factory=dict)
    warnings: list = field(default_factory=list)
    base_ref: str = None
    evidence: list = field(default_factory=list)
    def to_dict(self):
        # Build cost section from steps
        measured_steps = [s for s in self.steps if s.get("cost") is not None]
        executed_steps = [s for s in self.steps if s.get("status") == "executed"]
        unmeasured_steps = [s for s in executed_steps if s.get("cost") is None]
        cost_total = sum(s["cost"] for s in measured_steps)
        cost_section = {
            "total": cost_total,
            "measured_steps": len(measured_steps),
            "unmeasured_steps": len(unmeasured_steps)
        }

        return {"work_order_id": self.work_order_id, "pipeline": self.pipeline,
                "title": self.title, "kind": self.kind,
                "steps": self.steps, "verdict": self.verdict, "human_required": self.human_required,
                "max_loopbacks": self.max_loopbacks, "loopbacks": self.loopbacks,
                "deployment_status": self.deployment_status, "verify_results": self.verify_results,
                "risk_hints": self.risk_hints, "decision": self.decision, "warnings": self.warnings,
                "base_ref": self.base_ref, "evidence": self.evidence, "cost": cost_section}

def parse_review(text, station_id):
    """Parse exactly one review JSON object from the authoritative channel.

    The review file must parse as exactly one JSON object (surrounding
    whitespace and one surrounding markdown code fence allowed) with station
    equal to the step station id, verdict one of pass, fail, changes_requested,
    and findings a list of strings. Anything else returns None; the caller
    records that as review_parse_failed and the station contributes no review.
    """
    if not text:
        return None

    # Strip whitespace and optional markdown code fence
    content = text.strip()
    if content.startswith("```json") or content.startswith("```"):
        lines = content.splitlines()
        # Remove first line (opening fence)
        lines = lines[1:]
        # Remove last line if it's a closing fence
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        content = "\n".join(lines).strip()

    # Parse as exactly one JSON object
    try:
        obj = json.loads(content)
    except json.JSONDecodeError:
        return None

    if not isinstance(obj, dict):
        return None
    if "verdict" not in obj or "station" not in obj:
        return None
    if obj["station"] != station_id:
        return None
    if obj["verdict"] not in {"pass", "fail", "changes_requested"}:
        return None

    try:
        return Review(station=str(obj["station"]),
                      verdict=str(obj["verdict"]),
                      findings=[str(f) for f in obj.get("findings", [])])
    except ValueError:
        return None

def _reported_model(text):
    """A model name counts only when the runtime output itself reports one.

    Scans the output for a JSON object with a string "model" field. Anything
    else returns None: ANVIL never guesses which model a runtime used.
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
        if isinstance(obj, dict) and isinstance(obj.get("model"), str) and obj["model"]:
            return obj["model"]
    return None

def _executor_provenance(executor, output_text=""):
    """Return (executor_object, executed_model) for an attempted execution.

    The http executor runs the model named in its config, so that model is
    the executed model and the detail is the endpoint host. A command
    executor is an opaque local process: the detail is the template's first
    token and the executed model is known only when the runtime output
    reports one itself.
    """
    kind = getattr(executor, "kind", "unknown")
    if kind == "http":
        endpoint = getattr(executor, "endpoint", "")
        detail = urlparse(endpoint).hostname or endpoint
        return {"kind": "http", "detail": detail}, (getattr(executor, "model", "") or None)
    if kind == "command":
        template = getattr(executor, "template", "")
        try:
            tokens = shlex.split(template)
        except ValueError:
            tokens = template.split()
        detail = tokens[0] if tokens else ""
        return {"kind": "command", "detail": detail}, _reported_model(output_text)
    return {"kind": str(kind), "detail": getattr(executor, "name", str(kind))}, None


def _snapshot_working_tree(project_dir):
    """Capture current state of working tree files.

    Args:
        project_dir: Path to project directory

    Returns:
        Dict mapping relative file paths to their content hash (or None for deleted/new).
    """
    project_path = Path(project_dir)
    snapshot = {}

    for p in project_path.rglob("*"):
        if p.is_file() and ".git" not in p.parts and "runs" not in p.parts:
            try:
                rel_path = str(p.relative_to(project_path))
                # Use file modification time as a simple hash
                snapshot[rel_path] = p.stat().st_mtime
            except (ValueError, OSError):
                pass

    return snapshot


def _compute_delta(before_snapshot, after_snapshot):
    """Compute the delta between two working tree snapshots.

    Args:
        before_snapshot: Dict from _snapshot_working_tree (before state)
        after_snapshot: Dict from _snapshot_working_tree (after state)

    Returns:
        Set of file paths that were added, modified, or deleted.
    """
    delta = set()

    # Files added or modified
    for file_path, mtime in after_snapshot.items():
        if file_path not in before_snapshot or before_snapshot[file_path] != mtime:
            delta.add(file_path)

    # Files deleted
    for file_path in before_snapshot:
        if file_path not in after_snapshot:
            delta.add(file_path)

    return delta


def _get_changed_files(project_dir, initial_files=None, work_output_dirs=None, base_ref=None):
    """Get list of changed files relative to base ref.

    Uses git to detect changes. If git is not available and initial_files
    snapshot is provided, compares current state against the snapshot to find
    new or deleted files.

    Args:
        project_dir: Path to project directory
        initial_files: Set of initial files for fallback comparison
        work_output_dirs: Set of directories where new files are always considered changed
        base_ref: Git ref to compare against (if None, compares against HEAD for uncommitted)

    Returns a set of file paths relative to project root.
    """
    project_path = Path(project_dir)

    # Try git first
    try:
        # Check if this is a git repo
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            # Get changed files from git
            if base_ref:
                # Compare current HEAD against base ref to get all changes on the work branch
                result = subprocess.run(
                    ["git", "diff", "--name-only", f"{base_ref}...HEAD"],
                    cwd=str(project_dir),
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            else:
                # No base ref, just get uncommitted changes
                result = subprocess.run(
                    ["git", "diff", "--name-only", "HEAD"],
                    cwd=str(project_dir),
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            files = {line.strip() for line in result.stdout.split('\n') if line.strip()}

            # Also get untracked files
            result2 = subprocess.run(
                ["git", "ls-files", "--others", "--exclude-standard"],
                cwd=str(project_dir),
                capture_output=True,
                text=True,
                timeout=10
            )
            if result2.returncode == 0:
                files.update({line.strip() for line in result2.stdout.split('\n') if line.strip()})

            # If we have a base_ref, also include uncommitted changes
            if base_ref:
                result3 = subprocess.run(
                    ["git", "diff", "--name-only"],
                    cwd=str(project_dir),
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result3.returncode == 0:
                    files.update({line.strip() for line in result3.stdout.split('\n') if line.strip()})

            return files
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass

    # Fallback: compare against initial snapshot
    if initial_files is not None:
        current_files = set()
        for p in project_path.rglob("*"):
            if p.is_file() and ".git" not in p.parts and "runs" not in p.parts:
                try:
                    rel_path = p.relative_to(project_path)
                    current_files.add(str(rel_path))
                except ValueError:
                    pass

        # Files that are NEW or were DELETED
        new_files = current_files - initial_files
        deleted_files = initial_files - current_files
        changed = new_files | deleted_files

        # Also treat files in work output directories as changed
        # (e.g., tests/ is for test files created during work)
        if work_output_dirs:
            for file_path in current_files:
                # Check if file is in a work output directory
                for work_dir in work_output_dirs:
                    if file_path.startswith(work_dir + "/") or file_path.startswith(work_dir + "\\"):
                        changed.add(file_path)
                        break

        return changed

    # No git and no snapshot: can't determine changes
    return set()


def _packet_text(station_id, prompt, work_order, steps, learnings_section="", design_section="", rendered_evidence_section="", knowledge_section="", quality_charter_section="", anchor_section=""):
    upstream = "\n".join(f"- {s['station']}: {s['status']}" for s in steps) or "- (none)"
    # Use rescoped description if intake rescoped the work
    description = work_order.description
    if work_order.intake_outcome.get("outcome") == "rescoped" and work_order.intake_outcome.get("rescoped_description"):
        description = work_order.intake_outcome["rescoped_description"]
    # Sanitize work order controlled strings (F3: control character sanitization)
    safe_title = _sanitize_control_chars(work_order.title)
    safe_description = _sanitize_control_chars(description)
    safe_source = _sanitize_control_chars(work_order.source)
    safe_risk_hints = ', '.join(_sanitize_control_chars(hint) for hint in work_order.risk_hints)
    text = (f"# Task packet: {station_id}\n\n## Station prompt\n\n{prompt}\n\n## Work order\n\n"
            f"- id: {work_order.id}\n- kind: {work_order.kind}\n- title: {safe_title}\n"
            f"- source: {safe_source}\n- description: {safe_description}\n"
            f"- risk_hints: {safe_risk_hints}\n- status: {work_order.status}\n\n"
            f"## Upstream steps\n\n{upstream}\n")
    if learnings_section:
        text += f"\n{learnings_section}\n"
    if design_section:
        text += f"\n{design_section}\n"
    if knowledge_section:
        text += f"\n{knowledge_section}\n"
    if quality_charter_section:
        text += f"\n{quality_charter_section}\n"
    if anchor_section:
        text += f"\n{anchor_section}\n"
    if rendered_evidence_section:
        text += f"\n{rendered_evidence_section}\n"
    # Reviewer stations have a specific output contract
    if station_id.startswith("reviewer"):
        text += (f"\n## Output contract\n\n"
                f"Your complete answer is exactly one review JSON object written to "
                f"runs/{work_order.id}/{station_id}.review.json. The free output transcript "
                f"stays as provenance and is never parsed for a review.\n")
    return text

def run_pipeline(project_dir, pipeline, work_order, registry=None, max_loopbacks=2,
                 executor=None, deploy_cfg=None, base_ref=None):
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

    # Load price table for cost measurement
    config = load_anvil_config(project / "anvil.yaml")
    try:
        price_table = load_price_table(config)
    except ValueError as e:
        # Price table validation failed - log warning but continue
        price_table = {}
        print(f"Warning: {e}")
    # Run scoped reviews: only reviews produced during this run feed the
    # approver. Standing project reviews under reviews/<slug>/ are the project
    # record read by `anvil check`, never inputs to a run.
    run_reviews = []
    run_findings = []
    deployment_status = None
    verify_results = []
    human_blocked = None  # decided at the triage step
    # Decision record: the approver entry is filled at the approver step from
    # the reviews counted there; the human gate entry is filled at the end
    # from the final verdict. Both rule sentences are generated from the
    # same values the code acted on.
    reviews_expected = [sid for sid in order if sid.startswith("reviewer")]
    decision_approver = None
    # Verified learnings are computed once per run: only non demoted entries
    # from brain/learnings.md, never inbox proposals (see anvil/brain.py).
    learnings_section = packet_learnings_section(project)

    # Load knowledge pack if provided in work order (S7, S8, S9)
    knowledge_pack = None
    pack_load_error = None
    if hasattr(work_order, 'knowledge_pack') and work_order.knowledge_pack:
        try:
            knowledge_pack = load_knowledge_pack(Path(work_order.knowledge_pack))
        except (FileNotFoundError, KnowledgeValidationError) as e:
            pack_load_error = str(e)
            # Pack loading failure stops the run at intake (S9)

    # Routing record: will be populated after intake
    routing_record = None

    # Evidence list: will be populated with screenshots from capture
    evidence_list = []

    # Snapshot base ref configuration for checks gate (S4)
    # Configuration is resolved from the base ref through git where a repo is
    # present, never from the working tree file (which may have been modified by
    # the builder). The working tree fallback is only for projects with no git repo.
    base_ref_config = resolve_base_ref_config(project, base_ref)

    # Snapshot initial files at run start for non-git changed file tracking
    # Directories where new files are always considered "changed" (spec S3)
    # These are work output directories that start empty in a fresh project
    work_output_dirs = {"tests", "reviews"}

    initial_files = set()
    for p in project.rglob("*"):
        if p.is_file() and ".git" not in p.parts and "runs" not in p.parts:
            try:
                rel_path = p.relative_to(project)
                initial_files.add(str(rel_path))
            except ValueError:
                pass

    # Track gate state
    gate_failed = False

    # Track builder delta for protected path checking (Loopback round 2)
    # Each builder attempt is judged on its own delta
    builder_attempt = 0
    builder_delta = set()
    builder_snapshot_before = None

    # Check for design system and prepare warnings
    warnings = []
    has_design_system = load_design_system(project) is not None
    interface_stations = {"builder", "writer", "media-producer", "brief-writer", "reviewer-design"}
    pipeline_has_interface_stations = any(sid in interface_stations for sid in order)

    if pipeline_has_interface_stations and not has_design_system:
        warnings.append("Missing design system: This pipeline includes interface-producing stations, "
                       "but the project has no design/DESIGN.md. Define the design system to enable "
                       "design review.")

    # S2: Add warning for visual runs with no reference anchors
    if is_visual_run(work_order):
        ref_dir = project / "design" / "reference"
        anchors = getattr(work_order, "anchors", [])
        if not anchors and not ref_dir.exists():
            warnings.append("No reference anchors: This visual run has no reference anchors. "
                          "The review will proceed under the charter floor alone.")

    def write_envelope(station_id, next_station, artifact, status, extra=None):
        envelope = {"schema": "anvil/envelope@1", "from_station": station_id, "to_station": next_station,
                    "work_order_id": work_order.id, "artifact_path": artifact,
                    "status": status, "created_at": datetime.now(timezone.utc).isoformat()}
        if extra:
            envelope.update(extra)
        (envelopes_dir / f"{station_id}.envelope.json").write_text(json.dumps(envelope, indent=2) + "\n", encoding="utf-8")

    def packet_step(station, station_id):
        prompt = station.prompt if station and station.prompt else f"Station {station_id}: carry out your role for this work order."
        design_section = packet_design_section(project, station_id)
        rendered_evidence_section = packet_rendered_evidence_section(project, work_order.id, station_id)
        # S3: Design knowledge section for design stations (computed once per run)
        knowledge_section = packet_knowledge_section(project, station_id, knowledge_pack)
        # Quality charter and anchor sections for visual runs
        quality_charter_section = packet_quality_charter_section(project, station_id, work_order)
        anchor_section = packet_anchor_section(project, station_id, work_order)
        packet = run_dir / f"{station_id}.packet.md"
        packet.write_text(_packet_text(station_id, prompt, work_order, steps, learnings_section, design_section, rendered_evidence_section, knowledge_section, quality_charter_section, anchor_section), encoding="utf-8")
        return packet

    for idx, station_id in enumerate(order):
        started = time.perf_counter()

        # S9: Pack loading failure stops the run at intake
        if station_id == "intake" and pack_load_error:
            steps.append({"station": station_id, "status": "failed", "elapsed": 0,
                        "model": "", "usage": {}, "cost": None,
                        "error": f"Knowledge pack loading failed: {pack_load_error}"})
            verdict = "failed"
            break

        station = None
        if registry is not None and station_id in registry:
            station = registry.get(station_id)
        kind = station.kind if station else ("deterministic" if station_id in {"intake", "approver", "triage-human"} else "agent")
        # Model provenance: the configured label is a fact of configuration,
        # recorded in every mode. Executed fields stay null until a runtime
        # actually runs the station (agent-execution S8).
        configured_model = station.model if station is not None and station.model else default_model(station_id)
        # Apply routing model overrides if routing selected a specific model for this station
        if routing_record and station_id in routing_record.selected_models:
            configured_model = routing_record.selected_models[station_id]
        # Apply guided designation: guided design stations use the design model from routing policy
        # For the builder, only apply guided model when working on UI surface
        if station and station.guided:
            if station_id == "builder" and "ui" not in work_order.surfaces:
                pass  # Builder not on UI surface, keep configured model
            else:
                configured_model = get_design_model_from_routing()
        step_executor = None
        step_executed_model = None
        status = "completed"
        detail = ""
        artifact = ""
        extra_envelope = {}
        step_usage = None
        deferred_verifier = None
        deferred_pre_deploy_gate = None
        next_station = order[idx + 1] if idx + 1 < len(order) else None
        terminal_outcome = False  # Track if intake outcome is terminal
        if station_id == "intake":
            # In execute mode, parse intake output for outcomes
            if execute_mode:
                packet = packet_step(station, station_id)
                packet_text = packet.read_text(encoding="utf-8")
                output_file = run_dir / f"{station_id}.output.md"
                try:
                    result = executor.execute(packet_text, station_id, packet_path=packet,
                                              output_path=output_file, cwd=project)
                    output_text = result.get("output", "") if isinstance(result, dict) else str(result)
                    usage = result.get("usage") if isinstance(result, dict) else None
                    output_file.write_text(output_text, encoding="utf-8")
                    step_executor, step_executed_model = _executor_provenance(executor, output_text)
                    if isinstance(usage, dict):
                        step_usage = usage

                    # Parse intake output for intake_outcome, risk, surfaces
                    intake_data = {}
                    decoder = json.JSONDecoder()
                    for idx, ch in enumerate(output_text):
                        if ch != "{":
                            continue
                        try:
                            obj, _ = decoder.raw_decode(output_text[idx:])
                            if isinstance(obj, dict):
                                intake_data = obj
                                break
                        except json.JSONDecodeError:
                            continue

                    # Update work order with intake outcome
                    if "intake_outcome" in intake_data:
                        work_order.intake_outcome = intake_data["intake_outcome"]
                        outcome = work_order.intake_outcome.get("outcome")

                        # Update work order status based on outcome
                        if outcome == "rejected":
                            work_order.status = "rejected"
                            terminal_outcome = True
                        elif outcome == "waiting_info":
                            work_order.status = "waiting_info"
                            terminal_outcome = True

                    # Update risk and surfaces
                    if "risk" in intake_data:
                        work_order.risk = intake_data["risk"]
                    if "surfaces" in intake_data:
                        work_order.surfaces = intake_data["surfaces"]

                    # Save work order
                    wo_dir = project / "work_orders"
                    wo_dir.mkdir(parents=True, exist_ok=True)
                    wo_file = wo_dir / f"{work_order.id}.json"
                    wo_file.write_text(json.dumps(work_order.to_dict(), indent=2) + "\n", encoding="utf-8")

                    # Run routing after intake to determine reviewer selection
                    # Get all reviewer stations from the pipeline
                    pipeline_reviewers = [sid for sid in order if sid.startswith("reviewer")]
                    if pipeline_reviewers:
                        routing_record = route_reviewers(work_order, pipeline_reviewers, project)
                        write_routing_record(run_dir, routing_record)
                        # Update reviews_expected to only include selected reviewers
                        reviews_expected = routing_record.selected_reviewers

                    status = "executed"
                    detail = f"Executed by {executor.name}; outcome: {work_order.intake_outcome.get('outcome', 'unknown')}"
                    artifact = str(output_file)
                except ExecutorError as exc:
                    status = "failed"
                    detail = f"Executor failed: {exc}"
                    artifact = str(packet)
                    step_executor, step_executed_model = _executor_provenance(executor)
            else:
                detail = "Work order normalized"
                artifact = str(run_dir / "report.json")
        elif station_id == "approver":
            if run_reviews:
                verdict, verdict_rule, counted = aggregate_explained(run_reviews)
            else:
                verdict = "no_reviews"
                verdict_rule = ("No reviews were produced in this run, so the verdict is no_reviews; "
                                "standing project reviews are never counted.")
                counted = []
            # When execution was attempted, state the review counts
            # This is especially important when routing reduced the panel (S5)
            counted_len = len(counted)
            expected_len = len(reviews_expected)
            if execute_mode:
                if counted_len < expected_len:
                    verdict_rule += f" (Counted {counted_len} reviews, expected {expected_len}.)"
                elif routing_record and routing_record.routed_out:
                    # When routing reduced the panel, mention the expected count after routing
                    verdict_rule += f" (Expected {expected_len} reviews after routing.)"
            decision_approver = {"reviews_counted": counted,
                                 "reviews_expected": list(reviews_expected),
                                 "rule": verdict_rule}
            detail = f"Approver verdict: {verdict}"
            artifact = str(run_dir / "report.json")
        elif station_id == "checks-gate":
            # Determine phase: pre-review or pre-deploy
            # Pre-review: right after builder
            # Pre-deploy: after approver/triage and before deployer/publisher
            builder_idx = order.index("builder") if "builder" in order else -1
            approver_idx = order.index("approver") if "approver" in order else -1
            if builder_idx >= 0 and idx > builder_idx and (approver_idx < 0 or idx < approver_idx):
                phase = "pre-review"
            else:
                phase = "pre-deploy"

            # Loopback round 2: Use builder delta for protected path checking
            # The gate judges only the builder station's changes for the current attempt
            if phase == "pre-review" and builder_delta:
                gate_changed_files = builder_delta
                gate_basis = "builder_delta"
                gate_attempt = builder_attempt
            else:
                # For pre-deploy or when builder delta not available, use cumulative changes
                gate_changed_files = _get_changed_files(project, initial_files, work_output_dirs, base_ref)
                gate_basis = "cumulative_changes" if phase == "pre-deploy" else "builder_delta"
                gate_attempt = builder_attempt if phase == "pre-review" else None

            # Run the gate
            gate_result = checks_gate(phase, base_ref_config, gate_changed_files, project, work_order.id,
                                     base_ref=base_ref, basis=gate_basis, attempt=gate_attempt)
            status = gate_result["status"]
            detail = gate_result["detail"]

            # Write gate output
            gate_output_file = run_dir / f"{station_id}.{phase}.output.md"
            gate_output_file.write_text(gate_result["output"], encoding="utf-8")
            artifact = str(gate_output_file)

            # Record gate results in the step
            extra_envelope = {
                "phase": gate_result["phase"],
                "commands": gate_result["commands"],
                "exit_codes": gate_result["exit_codes"],
                "protected_paths": gate_result["protected_paths"],
                "protected_path_verdict": gate_result["protected_path_verdict"],
                "protected_path_findings": gate_result["protected_path_findings"],
                "observed_additions": gate_result.get("observed_additions", []),
                "basis": gate_result.get("basis", ""),
                "gate_verdict": gate_result["gate_verdict"]
            }

            # If gate failed and we're in pre-review phase, trigger loopback (S2)
            if gate_result["gate_verdict"] == "fail" and phase == "pre-review":
                gate_failed = True
                # Skip reviewers by marking that we should loop back
            # If gate failed in pre-deploy phase, block deployment (S5)
            elif gate_result["gate_verdict"] == "fail" and phase == "pre-deploy":
                verdict = "gate_failed"
                detail += "; deployment blocked by gate failure"
        elif station_id == "triage-human":
            hr = needs_human(work_order, verdict) if verdict else (human_gate(work_order) == "required")
            human_blocked = hr
            detail = f"Human review: {'required' if hr else 'not_required'}"
        elif station_id == "deployer" and execute_mode and deploy_cfg and deploy_cfg.get("command"):
            blocked = human_blocked if human_blocked is not None else needs_human(work_order, verdict)
            # Run pre-deploy checks gate (S5) - only if pre-review gate didn't fail
            deferred_pre_deploy_gate = None
            if verdict == "approved" and not blocked and not gate_failed:
                gate_started = time.perf_counter()
                # Use builder delta for pre-deploy as well (same basis as pre-review)
                if builder_delta:
                    gate_changed_files = builder_delta
                else:
                    gate_changed_files = _get_changed_files(project, initial_files, work_output_dirs, base_ref)
                gate_result = checks_gate("pre-deploy", base_ref_config, gate_changed_files, project, work_order.id,
                                         base_ref=base_ref, basis="builder_delta", attempt=builder_attempt)

                gate_output_file = run_dir / "checks-gate.pre-deploy.output.md"
                gate_output_file.write_text(gate_result["output"], encoding="utf-8")

                gate_step = {
                    "station": "checks-gate",
                    "status": gate_result["status"],
                    "detail": gate_result["detail"],
                    "duration_ms": round((time.perf_counter() - gate_started) * 1000, 3),
                    "cost": None,
                    "artifacts": [str(gate_output_file)],
                    "configured_model": None,
                    "executed_model": None,
                    "executor": None,
                    "phase": gate_result["phase"],
                    "commands": gate_result["commands"],
                    "exit_codes": gate_result["exit_codes"],
                    "protected_paths": gate_result["protected_paths"],
                    "protected_path_verdict": gate_result["protected_path_verdict"],
                    "protected_path_findings": gate_result["protected_path_findings"],
                    "observed_additions": gate_result.get("observed_additions", []),
                    "basis": gate_result.get("basis", ""),
                    "gate_verdict": gate_result["gate_verdict"]
                }
                deferred_pre_deploy_gate = gate_step

                # If pre-deploy gate fails, block deployment (S5)
                if gate_result["gate_verdict"] == "fail":
                    verdict = "gate_failed"
                    blocked = True

            if verdict == "approved" and not blocked and verdict != "gate_failed":
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
                             "configured_model": None, "executed_model": None, "executor": None,
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
            # Skip reviewers if gate failed (S2)
            if gate_failed and station_id.startswith("reviewer"):
                status = "skipped"
                detail = "Skipped due to gate failure"
                packet = packet_step(station, station_id)
                artifact = str(packet)
            # Skip reviewers that were routed out
            elif station_id.startswith("reviewer") and routing_record and station_id not in routing_record.selected_reviewers:
                status = "routed_out"
                routed_reason = next((r["reason"] for r in routing_record.routed_out if r["reviewer"] == station_id), "Not in selected panel")
                detail = f"Routed out: {routed_reason}"
                packet = packet_step(station, station_id)
                artifact = str(packet)
            else:
                # Capture builder delta (Loopback round 2)
                if station_id == "builder":
                    builder_attempt += 1
                    builder_snapshot_before = _snapshot_working_tree(project)

                packet = packet_step(station, station_id)
                packet_text = packet.read_text(encoding="utf-8")
                output_file = run_dir / f"{station_id}.output.md"

                # For reviewer stations, remove any pre-existing review file before execution (S3)
                if station_id.startswith("reviewer"):
                    review_file = run_dir / f"{station_id}.review.json"
                    try:
                        review_file.unlink()
                    except FileNotFoundError:
                        pass

                try:
                    result = executor.execute(packet_text, station_id, packet_path=packet,
                                              output_path=output_file, cwd=project)
                    output_text = result.get("output", "") if isinstance(result, dict) else str(result)
                    usage = result.get("usage") if isinstance(result, dict) else None
                    output_file.write_text(output_text, encoding="utf-8")
                    status = "executed"
                    detail = f"Executed by {executor.name}; output written to {output_file}"
                    artifact = str(output_file)
                    step_executor, step_executed_model = _executor_provenance(executor, output_text)
                    extra_envelope = {}
                    if isinstance(usage, dict):
                        step_usage = usage
                        extra_envelope["usage"] = usage
                        tokens = {k: usage[k] for k in usage if "token" in k}
                        if tokens:
                            extra_envelope["tokens"] = tokens
                    if station_id.startswith("reviewer"):
                        # S2: Read review from the file the reviewer wrote, never from stdout
                        review_file = run_dir / f"{station_id}.review.json"
                        review = None
                        review_file_text = None

                        # Check if correction metadata exists
                        correction_meta_path = run_dir / f"{station_id}.correction.json"
                        if correction_meta_path.exists():
                            extra_envelope["correction_used"] = True

                        if review_file.exists():
                            try:
                                review_file_text = review_file.read_text(encoding="utf-8")
                                review = parse_review(review_file_text, station_id)
                            except Exception as e:
                                # File exists but couldn't be read or parsed
                                review = None

                        # Special handling for reviewer-design when no design system exists
                        if station_id == "reviewer-design" and not has_design_system:
                            review = Review(
                                station="reviewer-design",
                                verdict="changes_requested",
                                findings=["No design system exists for this project. The project must define "
                                         "design/DESIGN.md and design/tokens.json before interface output can be "
                                         "reviewed against design standards."]
                            )
                        elif review is not None:
                            # Valid review parsed from file
                            pass
                        elif review_file.exists():
                            # File exists but failed to parse (S3)
                            extra_envelope["review_parse_failed"] = True
                            detail += "; review file exists but did not parse as valid review JSON"
                        else:
                            # File does not exist (S3)
                            extra_envelope["review_file_missing"] = True
                            detail += "; review file was not written by the station"

                        if review is not None:
                            run_reviews.append(review)
                            run_findings.extend(review.findings)
                            extra_envelope["review"] = review.to_dict()

                    # Track builder delta for protected path checking (Loopback round 2)
                    if station_id == "builder" and builder_snapshot_before is not None:
                        # Capture working tree state after builder execution
                        builder_snapshot_after = _snapshot_working_tree(project)
                        # Compute delta: files added, modified, or deleted by this builder attempt
                        builder_delta = _compute_delta(builder_snapshot_before, builder_snapshot_after)
                except ExecutorError as exc:
                    status = "failed"
                    detail = f"Executor failed: {exc}"
                    artifact = str(packet)
                    step_executor, step_executed_model = _executor_provenance(executor)
                    extra_envelope = {"error": str(exc)}
        else:
            packet = packet_step(station, station_id)
            status = "packet_ready"
            detail = f"Packet written to {packet}"
            artifact = str(packet)
        duration_ms = round((time.perf_counter() - started) * 1000, 3)
        step = {"station": station_id, "status": status, "detail": detail, "duration_ms": duration_ms,
                "cost": None, "artifacts": [artifact] if artifact else [],
                "configured_model": configured_model, "executed_model": step_executed_model,
                "executor": step_executor}
        if step_usage is not None:
            step["usage"] = step_usage
            # Calculate cost from usage and price table
            # Use executed model if available, otherwise configured model
            cost_model = step_executed_model or configured_model
            cost_record = calculate_cost(step_usage, cost_model, price_table)
            step["cost"] = cost_record["cost"]
            # Optionally include detailed cost record
            if not cost_record["measured"]:
                step["cost_record"] = {
                    "measured": cost_record["measured"],
                    "reason": cost_record["reason"]
                }
        # Add extra fields from checks-gate to the step itself
        if station_id == "checks-gate" and extra_envelope:
            for key in ["phase", "commands", "exit_codes", "protected_paths",
                       "protected_path_verdict", "protected_path_findings", "gate_verdict"]:
                if key in extra_envelope:
                    step[key] = extra_envelope[key]
        steps.append(step)
        env_extra = dict(extra_envelope)
        env_extra["configured_model"] = configured_model
        if step_executor is not None:
            env_extra["executor"] = step_executor
            env_extra["executed_model"] = step_executed_model
        write_envelope(station_id, next_station, artifact or str(run_dir / "report.json"), status, env_extra)

        # Capture screenshots after builder completes successfully (S1)
        if station_id == "builder" and status == "executed" and execute_mode:
            evidence_dir = run_dir / "evidence"
            capture_result = capture_breakpoints(project, evidence_dir)

            # Record capture result in the report
            if capture_result["success"]:
                # Store capture metadata for later use in report
                for capture in capture_result["captures"]:
                    # Add to evidence list with relative path
                    rel_path = Path(capture["path"]).relative_to(project)
                    evidence_list.append({
                        "type": "screenshot",
                        "breakpoint": capture["breakpoint"],
                        "path": str(rel_path),
                        "width": capture["width"],
                        "height": capture["height"]
                    })
            else:
                # Record failure reason for reviewer-design
                # This will be picked up when building reviewer-design's packet
                capture_failure_file = run_dir / "capture_failure.txt"
                capture_failure_file.write_text(capture_result["error"], encoding="utf-8")

        # Stop pipeline if intake outcome is terminal (rejected or waiting_info)
        if station_id == "intake" and terminal_outcome:
            break

        # Insert pre-deploy gate before deployer (S5)
        if deferred_pre_deploy_gate is not None:
            steps.append(deferred_pre_deploy_gate)
            write_envelope("checks-gate", station_id,
                           deferred_pre_deploy_gate["artifacts"][0] if deferred_pre_deploy_gate["artifacts"] else str(run_dir / "report.json"),
                           deferred_pre_deploy_gate["status"],
                           {k: v for k, v in deferred_pre_deploy_gate.items()
                            if k in ["phase", "commands", "exit_codes", "protected_paths",
                                   "protected_path_verdict", "protected_path_findings", "gate_verdict"]})
        if deferred_verifier is not None:
            steps.append(deferred_verifier)
            write_envelope("verifier", next_station,
                           deferred_verifier["artifacts"][0] if deferred_verifier["artifacts"] else str(run_dir / "report.json"),
                           deferred_verifier["status"], {"configured_model": None})
        # Loopback after checks-gate failure (S2)
        if station_id == "checks-gate" and gate_failed and loopbacks < max_loopbacks:
            loopbacks += 1
            return_to = "builder"
            reason = f"Gate failure: {'; '.join(extra_envelope.get('protected_path_findings', [])[:3])}" if extra_envelope.get('protected_path_findings') else "Gate checks failed"
            steps.append({"station": "loopback", "status": "loopback", "return_to": return_to,
                          "detail": f"Loopback to {return_to}: {reason}", "reason": reason,
                          "duration_ms": 0.0, "cost": None, "artifacts": [],
                          "configured_model": None, "executed_model": None, "executor": None,
                          "feedback": extra_envelope.get("output", ""),
                          "from_station": "checks-gate"})
        # Loopback right after approver when aggregation fails
        elif station_id == "approver" and verdict in {"rejected", "changes_requested"} and loopbacks < max_loopbacks:
            loopbacks += 1
            # Spec failures return to spec-writer, implementation failures to builder.
            return_to = "spec-writer" if any("spec" in str(f).lower() and "missing" in str(f).lower() for f in run_findings) else "builder"
            reason = "; ".join(run_findings) if run_findings else f"Approver verdict: {verdict}"
            steps.append({"station": station_id, "status": "loopback", "return_to": return_to,
                          "detail": f"Loopback to {return_to}: {reason}", "reason": reason,
                          "duration_ms": 0.0, "cost": None, "artifacts": [],
                          "configured_model": None, "executed_model": None, "executor": None})
    if not verdict:
        verdict = "packet_ready"
    if decision_approver is None:
        # A pipeline without an approver step aggregates nothing; say so
        # instead of inventing a verdict explanation.
        decision_approver = {"reviews_counted": [{"station": r.station, "verdict": r.verdict} for r in run_reviews],
                             "reviews_expected": list(reviews_expected),
                             "rule": "The pipeline has no approver step, so no reviews were aggregated into a verdict."}
    if verdict in {"approved", "rejected", "changes_requested", "no_reviews"}:
        human_required, human_rule, hints_matched = needs_human_explained(work_order, verdict)
    else:
        # No approver verdict exists, so the gate looks at risk hints only,
        # exactly as human_gate does.
        hints_matched = matched_risk_hints(work_order)
        human_required = bool(hints_matched)
        if hints_matched:
            quoted = ", ".join(f"'{h}'" for h in hints_matched)
            noun = "risk hint" if len(hints_matched) == 1 else "risk hints"
            human_rule = (f"No approver verdict was produced by this pipeline, and the work order carries "
                          f"the {noun} {quoted}, so a human is required.")
        else:
            scanned = ", ".join(RISK_SCAN_ORDER)
            human_rule = (f"No approver verdict was produced by this pipeline and no risk hints matched "
                          f"(scanned: {scanned}), so no human is required.")
    decision = {"approver": decision_approver,
                "human_gate": {"required": human_required, "rule": human_rule, "hints_matched": hints_matched}}
    report = RunReport(work_order_id=work_order.id, pipeline=pipeline.name, steps=steps, verdict=verdict,
                       title=work_order.title, kind=work_order.kind,
                       human_required=human_required, max_loopbacks=max_loopbacks, loopbacks=loopbacks,
                       deployment_status=deployment_status, verify_results=verify_results,
                       risk_hints=list(work_order.risk_hints or []), decision=decision, warnings=warnings,
                       base_ref=base_ref, evidence=evidence_list)
    (run_dir / "report.json").write_text(json.dumps(report.to_dict(), indent=2) + "\n", encoding="utf-8")
    # Swimlane
    lines = ["# Swimlane", ""]

    # Add intake outcome summary if present
    if work_order.intake_outcome:
        outcome = work_order.intake_outcome.get("outcome")
        if outcome == "rejected":
            lines.append("**Status**: rejected at intake")
            lines.append("")
        elif outcome == "waiting_info":
            lines.append("**Status**: waiting for information")
            lines.append("")

    # Add routing summary if present
    if routing_record:
        lines.append(routing_swimlane_summary(routing_record))
        lines.append("")

    # Add cost summary
    report_dict = report.to_dict()
    cost_section = report_dict["cost"]
    total_steps = cost_section["measured_steps"] + cost_section["unmeasured_steps"]
    if cost_section["measured_steps"] > 0:
        lines.append(f"**Cost**: ${cost_section['total']:.4f} ({cost_section['measured_steps']} of {total_steps} steps measured)")
    else:
        lines.append(f"**Cost**: No measured steps ({total_steps} executed steps)")
    lines.append("")
    lines.append("| Station | Status | Duration ms | Artifacts | Cost |")
    lines.append("|---|---|---|---|---|")
    for s in steps:
        arts = ", ".join(s.get("artifacts", [])) or "-"
        cost = s.get("cost")
        lines.append(f"| {s['station']} | {s['status']} | {s.get('duration_ms', 0)} | {arts} | {cost if cost is not None else 'null'} |")
    lines.append("")
    lines.append("## Decision")
    lines.append("")
    lines.append(f"- Approver: {decision['approver']['rule']}")
    lines.append(f"- Human gate: {decision['human_gate']['rule']}")
    if deployment_status is not None:
        lines.append("")
        lines.append(f"Deployment: {deployment_status}")
    if verify_results:
        lines.append("")
        lines.append("Verification:")
        for r in verify_results:
            lines.append(f"- {r['status']}: {r['command']}")
    (run_dir / "swimlane.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Render report.md
    report_lines = ["# Run Report", "", f"Work Order: {work_order.id}", f"Title: {work_order.title}",
                    f"Kind: {work_order.kind}", f"Status: {work_order.status}", ""]

    # Include intake outcome if present
    if work_order.intake_outcome:
        outcome = work_order.intake_outcome.get("outcome", "unknown")
        report_lines.append("## Intake Outcome")
        report_lines.append("")
        report_lines.append(f"Outcome: {outcome}")
        report_lines.append("")

        if outcome == "rejected":
            report_lines.append("This work order was rejected at intake.")
            report_lines.append("")
            if "reasons" in work_order.intake_outcome:
                report_lines.append("### Reasons")
                report_lines.append("")
                for reason in work_order.intake_outcome["reasons"]:
                    report_lines.append(f"- {_escape_markdown(reason)}")
                report_lines.append("")
        elif outcome == "waiting_info":
            report_lines.append("This work order is waiting for additional information.")
            report_lines.append("")
            if "questions" in work_order.intake_outcome:
                report_lines.append("### Questions")
                report_lines.append("")
                for question in work_order.intake_outcome["questions"]:
                    report_lines.append(f"- {_escape_markdown(question)}")
                report_lines.append("")
        elif outcome == "rescoped":
            report_lines.append("This work order was rescoped at intake.")
            report_lines.append("")
            if "rescoped_description" in work_order.intake_outcome:
                report_lines.append("### Rescoped Description")
                report_lines.append("")
                report_lines.append("```")
                report_lines.append(work_order.intake_outcome["rescoped_description"])
                report_lines.append("```")
                report_lines.append("")
            if "reasons" in work_order.intake_outcome:
                report_lines.append("### Rescope Reasons")
                report_lines.append("")
                for reason in work_order.intake_outcome["reasons"]:
                    report_lines.append(f"- {_escape_markdown(reason)}")
                report_lines.append("")

    # Include risk and surfaces
    if work_order.risk:
        report_lines.append(f"Risk: {work_order.risk}")
        report_lines.append("")
    if work_order.surfaces:
        report_lines.append(f"Surfaces: {', '.join(work_order.surfaces)}")
        report_lines.append("")

    # Include routing section if present
    if routing_record:
        report_lines.append(render_routing_section(routing_record))

    # S7: Record operator-supplied knowledge pack
    if knowledge_pack:
        report_lines.append("## Operator Supplied Inputs")
        report_lines.append("")
        report_lines.append("**Knowledge Pack**:")
        report_lines.append(f"- Name: {knowledge_pack['name']}")
        report_lines.append(f"- Product types covered: {', '.join(knowledge_pack['product_types'])}")
        report_lines.append(f"- Data files: {', '.join(knowledge_pack['files'])}")
        report_lines.append("")

    # Include verdict
    report_lines.append(f"## Verdict")
    report_lines.append("")
    report_lines.append(f"Verdict: {verdict}")
    report_lines.append("")

    # Include approver decision rule if present
    if decision and "approver" in decision and "rule" in decision["approver"]:
        report_lines.append(decision["approver"]["rule"])
        report_lines.append("")

    # Include steps
    report_lines.append("## Steps")
    report_lines.append("")
    for s in steps:
        report_lines.append(f"- {s['station']}: {s['status']}")
    report_lines.append("")

    (run_dir / "report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    return report

run = run_pipeline
