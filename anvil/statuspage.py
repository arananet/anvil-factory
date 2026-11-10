"""Run status page generator.

Reads every runs/<id>/report.json in a project and renders one self
contained HTML page: inline CSS, no external assets, so the file can be
dropped on Cloudflare Pages, GitHub Pages or any static host unchanged.

The page is a snapshot of the reports on disk at generation time. Nothing is
invented: missing usage is unknown and unpriced cost stays null. Runs whose
report is missing or unreadable are skipped and the skip is noted in the
page footer.

The page includes a lifecycle board showing each work order's progression
through stages: SPEC, BUILD, REVIEW, APPROVED, MERGED. Stages are derived
from evidence in the run reports and merge records. Intake states (PARKED,
REJECTED) and NEEDS HUMAN flags are also shown when applicable.
"""

import html
import json
import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from .telemetry import normalize_usage, summarize_steps, public_report

# Lifecycle stage vocabulary in order
LIFECYCLE_STAGES = ["SPEC", "BUILD", "REVIEW", "APPROVED", "MERGED"]

CSS = """
:root {
  color-scheme: dark;
  --space-4: 4px;
  --space-8: 8px;
  --space-12: 12px;
  --space-16: 16px;
  --space-20: 20px;
  --space-24: 24px;
  --space-32: 32px;
  --space-48: 48px;
  --space-64: 64px;
}
body { background:#0C0C0C; color:#E8E8E8; font-family:Inter, system-ui, sans-serif; margin:0; padding:var(--space-32) var(--space-20) var(--space-64); }
main { max-width:1080px; margin:0 auto; }
h1 { font-size:28px; letter-spacing:.02em; margin:0 0 var(--space-4); }
h1 .accent { color:#FF5C00; }
h2 { font-family:ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size:17px; margin:0 0 var(--space-8); }
.mono { font-family:ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
.muted { color:#9A9A9A; }
.snapshot { border-left:3px solid #FF5C00; background:#1E1E1E; padding:var(--space-12) var(--space-16); margin:var(--space-20) 0 var(--space-32); font-size:14px; }
.run { background:#1E1E1E; border:1px solid #2A2A2A; border-radius:var(--space-8); padding:var(--space-20); margin:0 0 var(--space-24); }
.meta { display:flex; flex-wrap:wrap; gap:var(--space-8) var(--space-24); font-size:13px; color:#C9C9C9; margin:var(--space-8) 0 var(--space-16); }
.meta b { color:#FFFFFF; font-weight:600; }
.decision { border-left:3px solid #3A3A3A; padding:var(--space-8) var(--space-12); margin:0 0 var(--space-16); font-size:13.5px; }
.decision div { margin:var(--space-4) 0; }
.table-container { overflow-x: auto; margin:0 0 var(--space-16); -webkit-overflow-scrolling: touch; }
table { width:100%; border-collapse:collapse; font-size:13px; }
th { text-align:left; font-family:ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-weight:600; color:#9A9A9A; border-bottom:1px solid #3A3A3A; padding:var(--space-8); }
td { border-bottom:1px solid #2A2A2A; padding:var(--space-8); vertical-align:top; }
.status { font-family:ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; white-space:nowrap; }
.st-ok { color:#FFFFFF; }
.st-failed { color:#FF5C00; }
.st-idle { color:#8A8A8A; }
.artifacts { color:#9A9A9A; word-break:break-all; }
@media (max-width: 768px) {
  th, td { padding:var(--space-4) var(--space-8); font-size:12px; }
  th:nth-child(4), td:nth-child(4), th:nth-child(5), td:nth-child(5) { display:none; }
}
.lifecycle-board { background:#1E1E1E; border:1px solid #2A2A2A; border-radius:var(--space-8); padding:var(--space-20); margin:0 0 var(--space-32); }
.board-title { font-size:20px; margin:0 0 var(--space-8); color:#FFFFFF; }
.board-description { font-size:13px; color:#9A9A9A; margin:0 0 var(--space-20); }
.board-row { background:#0C0C0C; border:1px solid #2A2A2A; border-radius:var(--space-8); padding:var(--space-16); margin:0 0 var(--space-12); }
.board-row:last-child { margin-bottom:0; }
.board-row-header { margin:0 0 var(--space-12); }
.board-wo-id { font-family:ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size:15px; font-weight:600; margin:0 0 var(--space-4); color:#FFFFFF; text-decoration:none; }
.board-wo-id:hover { text-decoration:underline; }
.board-wo-title { font-size:14px; color:#C9C9C9; }
.board-stages { display:flex; flex-wrap:wrap; gap:var(--space-8); align-items:center; margin:0 0 var(--space-8); }
.board-stage { font-family:ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size:12px; padding:var(--space-4) var(--space-12); border-radius:var(--space-4); background:#2A2A2A; color:#8A8A8A; white-space:nowrap; }
.board-stage.stage-reached { background:#3A3A3A; color:#C9C9C9; }
.board-stage.stage-current { background:#FF5C00; color:#FFFFFF; font-weight:600; }
.board-badge { display:inline-block; font-family:ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size:11px; font-weight:700; padding:var(--space-4) var(--space-8); border-radius:var(--space-4); text-transform:uppercase; letter-spacing:.03em; }
.board-badge.needs-human { background:#FFD700; color:#0C0C0C; }
.board-intake-state { font-family:ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size:13px; font-weight:600; padding:var(--space-8) var(--space-12); border-radius:var(--space-4); display:inline-block; }
.board-intake-state.state-parked { background:#5A5A2A; color:#FFD700; }
.board-intake-state.state-rejected { background:#5A2A2A; color:#FF5C00; }
footer { color:#8A8A8A; font-size:13px; margin-top:var(--space-32); }
@media (max-width: 400px) {
  .board-stages { gap:var(--space-4); }
  .board-stage { font-size:11px; padding:var(--space-4) var(--space-8); }
}
""".strip()

CSS += """
* { box-sizing:border-box; }
body { overflow-wrap:anywhere; }
a { color:#E8E8E8; text-underline-offset:3px; }
a:focus-visible, summary:focus-visible { outline:2px solid #FF5C00; outline-offset:4px; }
.usage-panel { border-top:2px solid #FF5C00; background:#1E1E1E; padding:var(--space-20); margin:0 0 var(--space-24); border-radius:var(--space-8); }
.usage-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(130px,1fr)); gap:var(--space-16); margin:var(--space-16) 0; }
.usage-grid dt { color:#B8B8B8; font-size:12px; margin-bottom:var(--space-4); }
.usage-grid dd { margin:0; font-family:ui-monospace,monospace; font-size:20px; color:#FFFFFF; }
.usage-note { color:#B8B8B8; font-size:13px; line-height:1.6; margin:var(--space-8) 0; }
.usage-details { margin-top:var(--space-8); font-family:system-ui,sans-serif; font-size:12px; }
.usage-details summary { cursor:pointer; min-height:28px; color:#E8E8E8; }
.usage-details .usage-grid { grid-template-columns:repeat(2,minmax(100px,1fr)); }
.usage-details dd { font-size:14px; }
.usage-attempt { padding:var(--space-8) 0; border-top:1px solid #3A3A3A; }
.project-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(min(100%,250px),1fr)); gap:var(--space-16); margin:var(--space-16) 0 var(--space-32); }
.project-card { background:#1E1E1E; border:1px solid #3A3A3A; border-radius:var(--space-8); padding:var(--space-20); }
.project-card h3 { margin-top:0; }
"""

STATUS_CLASS = {"completed": "st-ok", "executed": "st-ok", "approved": "st-ok",
                "failed": "st-failed", "rejected": "st-failed", "deploy_failed": "st-failed",
                "deployed_unverified": "st-failed", "budget_exceeded": "st-failed"}


def _number(value):
    return "Unknown" if value is None else f"{value:,}"


def _usage_metrics(usage):
    total_label = "Measured subtotal" if usage.get("complete") is False and usage.get("total_tokens") is not None else "Total tokens"
    fields = ((total_label, "total_tokens"), ("Input tokens", "input_tokens"),
              ("Output tokens", "output_tokens"), ("Cached input", "cached_input_tokens"),
              ("Cache creation", "cache_creation_input_tokens"), ("Reasoning tokens", "reasoning_tokens"))
    return '<dl class="usage-grid">' + "".join(
        f"<div><dt>{label}</dt><dd>{_number(usage.get(key))}</dd></div>" for label, key in fields) + "</dl>"


def _usage_panel(steps, title="Token consumption"):
    usage = summarize_steps(steps)
    coverage = f"{usage['measured_calls']} of {usage['calls']} agent calls measured"
    state = "Complete measurement" if usage["complete"] else "Partial measurement"
    note = "No agent calls recorded yet." if not usage["calls"] else "Reported totals include retries and failed calls with usage evidence."
    if usage["total_tokens"] is None:
        state = "Usage unavailable"
        note = f"{usage['unmeasured_calls']} calls have unknown usage. Totals will appear when runtimes report consumption. Unrecorded historical usage cannot be reconstructed."
    elif not usage["complete"]:
        note += f" {usage['unmeasured_calls']} calls have unknown usage; this is a measured subtotal."
    breakdown = ['<details class="usage-details"><summary>Usage by model and station</summary>']
    for heading, key in (("Model", "by_model"), ("Station", "by_station")):
        if usage[key]:
            breakdown.append(f'<div class="table-container"><table><thead><tr><th>{heading}</th><th>Tokens</th><th>Calls measured</th></tr></thead><tbody>')
            for label, group in usage[key].items():
                breakdown.append(f'<tr><td>{_esc(label)}</td><td>{_number(group["total_tokens"])}</td><td>{group["measured_calls"]}/{group["calls"]}</td></tr>')
            breakdown.append('</tbody></table></div>')
    breakdown.append('</details>')
    metrics = _usage_metrics(usage)
    if usage["total_tokens"] is None:
        metrics = ('<dl class="usage-grid"><div><dt>Total tokens</dt><dd>Unknown</dd></div>'
                   f'<div><dt>Measured calls</dt><dd>{usage["measured_calls"]}/{usage["calls"]}</dd></div></dl>'
                   '<details class="usage-details"><summary>Input, output and cache details</summary>' + metrics + '</details>')
    breakdown.insert(-1, '<p class="usage-note">Cached input is part of input; reasoning is part of output. Each agent call is one station runtime invocation and may include multiple model/tool turns.</p>')
    return (f'<section class="usage-panel" aria-label="{_esc(title)}"><h2>{_esc(title)}</h2>'
            f'<p class="usage-note">{state} · {coverage} · {usage["retries"]} recorded retries</p>'
            + metrics + f'<p class="usage-note">{note}</p>' + "".join(breakdown) + '</section>')


def _step_usage(step):
    if not summarize_steps([step])["calls"]:
        return ""
    usage = normalize_usage(step.get("usage"))
    attempts = step.get("attempts") or []
    if usage is None and not attempts and step.get("status") not in {"executed", "failed"}:
        return ""
    partial = any(normalize_usage(a.get("usage")) is None or not a.get("usage_complete", True) for a in attempts)
    label = _number(usage["total_tokens"] if usage else None) + " tokens"
    if partial:
        label += " (partial)"
    parts = [f'<details class="usage-details"><summary>{label}</summary>']
    parts.append(_usage_metrics(usage or {}))
    if step.get("measured_tokens"):
        parts.append(f'<p class="usage-note">Initial packet estimate: {_number(step["measured_tokens"])} tokens. This is not runtime consumption.</p>')
    for index, attempt in enumerate(attempts, 1):
        parts.append(f'<div class="usage-attempt"><b>Attempt {index}</b> · {_esc(attempt.get("status", "unknown"))}')
        if attempt.get("runtime"):
            parts.append(f' · {_esc(attempt["runtime"])}')
        if attempt.get("turns") is not None:
            parts.append(f' · {_esc(attempt["turns"])} runtime turns')
        parts.append(_usage_metrics(normalize_usage(attempt.get("usage")) or {}))
        if attempt.get("runtime_cost_estimate_usd") is not None:
            parts.append(f'<p class="usage-note">Runtime cost estimate: ${_esc(attempt["runtime_cost_estimate_usd"])} (not an invoice)</p>')
        parts.append('</div>')
    parts.append('</details>')
    return "".join(parts)


def _project_name(project):
    try:
        return str(json.loads((Path(project) / "anvil.json").read_text(encoding="utf-8")).get("project", Path(project).name))
    except (OSError, ValueError, AttributeError):
        return Path(project).name


def _portfolio_entries(projects):
    entries, seen = [], set()
    used_slugs = set()
    for project in projects or []:
        root = Path(project).resolve()
        if root in seen:
            continue
        seen.add(root)
        if not root.is_dir():
            raise ValueError(f"Status project directory does not exist: {root}")
        base = re.sub(r"[^a-z0-9_-]+", "-", root.name.lower()).strip("-")[:64] or "project"
        slug, suffix = base, 1
        while slug in used_slugs:
            suffix += 1
            slug = f"{base}-{suffix}"
        used_slugs.add(slug)
        runs, _ = collect_runs(root, include_history=True)
        entries.append({"name": _project_name(root), "page": f"projects/{slug}/index.html",
                        "runs": len(runs), "token_usage": summarize_steps([s for r in runs for s in r.get("steps", [])]),
                        "root": root})
    return entries


def _esc(value):
    return html.escape(str(value), quote=True)


def _dash(value):
    if value is None or value == "":
        return "-"
    return _esc(value)


def _status_span(value):
    cls = STATUS_CLASS.get(str(value), "st-idle")
    return f'<span class="status {cls}">{_esc(value)}</span>'


def _derived_decision(report):
    """Minimal explanation for a report that predates decision recording.

    Derived only from fields the old record actually carries (verdict,
    human_required, executed reviewer steps) and labeled as derived on the
    page, so nobody mistakes it for the runner's own words.
    """
    verdict = report.get("verdict", "-")
    steps = report.get("steps", []) or []
    executed_reviewers = [s for s in steps
                          if str(s.get("station", "")).startswith("reviewer")
                          and s.get("status") == "executed"]
    if verdict == "no_reviews":
        approver = "Approver: no reviewer step produced a counted review in this run, so the verdict is no_reviews."
    elif executed_reviewers:
        approver = f"Approver: verdict {verdict} from the reviews produced by the executed reviewer steps in this run."
    else:
        approver = f"Approver: verdict {verdict} is on record, but this report does not itemize the reviews behind it."
    if report.get("human_required"):
        human = f"Human gate: a human was required for this run (verdict {verdict})."
    else:
        human = f"Human gate: no human was required for this run (verdict {verdict})."
    return approver, human


def _decision_block(report):
    decision = report.get("decision")
    if isinstance(decision, dict):
        approver = decision.get("approver") or {}
        human_gate = decision.get("human_gate") or {}
        if approver.get("rule"):
            return ('<div class="decision">'
                    f"<div><span class='mono muted'>approver:</span> {_esc(approver['rule'])}</div>"
                    f"<div><span class='mono muted'>human gate:</span> {_esc(human_gate.get('rule', '-'))}</div>"
                    "</div>")
    approver_text, human_text = _derived_decision(report)
    return ('<div class="decision">'
            "<div class='mono muted'>decision, derived from the run record:</div>"
            f"<div>{_esc(approver_text)}</div>"
            f"<div>{_esc(human_text)}</div>"
            "</div>")


def collect_runs(project, include_history=False):
    """Return (runs, skipped): parsed report dicts and skipped folder names."""
    runs = []
    skipped = []
    seen = set()
    runs_dir = Path(project) / "runs"
    if runs_dir.is_dir():
        for folder in sorted(p for p in runs_dir.iterdir() if p.is_dir()):
            files = [folder / "report.json"]
            if include_history:
                files += sorted((folder / "history").glob("*.json"))
            for report_file in files:
                try:
                    data = json.loads(report_file.read_text(encoding="utf-8"))
                    if not isinstance(data, dict) or "work_order_id" not in data:
                        raise ValueError("report has no work_order_id")
                    key = str(data.get("run_id") or hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest())
                    if key in seen:
                        continue
                    seen.add(key)
                    if report_file.parent.name == "history":
                        data = dict(data, _archived=True, _record=report_file.stem)
                    runs.append(data)
                except (OSError, ValueError, TypeError):
                    skipped.append(str(report_file.relative_to(runs_dir)) if report_file.parent.name == "history" else folder.name)
    runs.sort(key=lambda r: str(r.get("work_order_id", "")))
    exports = Path(project) / "report_exports.json"
    if exports.is_file():
        try:
            payload = json.loads(exports.read_text(encoding="utf-8"))
            if payload.get("schema") != "anvil/project-reports@1":
                raise ValueError("unsupported report export")
            for data in payload["reports"]:
                key = str(data.get("run_id") or hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest())
                if key not in seen:
                    seen.add(key)
                    runs.append(data)
        except (OSError, ValueError, TypeError, KeyError, AttributeError):
            skipped.append("report_exports.json")
    runs.sort(key=lambda r: str(r.get("work_order_id", "")))
    return runs, skipped


def load_merge_records(project):
    """Load merge records from merge_records/ folder.

    Returns dict mapping work_order_id to merge record (dict with 'merged' bool).
    """
    merge_records = {}
    merge_dir = Path(project) / "merge_records"
    if merge_dir.is_dir():
        for record_file in merge_dir.glob("*.json"):
            try:
                data = json.loads(record_file.read_text(encoding="utf-8"))
                if isinstance(data, dict) and "work_order_id" in data:
                    merge_records[data["work_order_id"]] = data
            except Exception:
                pass
    return merge_records


def derive_lifecycle_stage(report, merge_records):
    """Derive lifecycle stage and state from a run report.

    Returns dict with:
        - stages_reached: list of stages reached (subset of LIFECYCLE_STAGES)
        - current_stage: the furthest stage reached, or None
        - needs_human: bool, True if decision.human_gate.required is True
        - intake_state: "PARKED" if verdict is waiting_info, "REJECTED" if rejected, else None

    Stages are derived from evidence:
        - SPEC: spec-writer step executed
        - BUILD: builder step executed
        - REVIEW: at least one reviewer-* step executed
        - APPROVED: verdict is "approved"
        - MERGED: work order has a merge record with merged=True

    Intake states override stage progression when present.
    """
    verdict = report.get("verdict")
    steps = report.get("steps", []) or []
    work_order_id = report.get("work_order_id", "")

    # Check for intake states first
    intake_state = None
    if verdict == "waiting_info":
        intake_state = "PARKED"
    elif verdict == "rejected":
        intake_state = "REJECTED"

    # If in intake state, skip stage progression
    if intake_state:
        return {
            "stages_reached": [],
            "current_stage": None,
            "needs_human": False,
            "intake_state": intake_state,
        }

    # Derive stages from evidence
    stages_reached = []

    # SPEC: spec-writer step executed
    if any(s.get("station") == "spec-writer" and s.get("status") == "executed" for s in steps):
        stages_reached.append("SPEC")

    # BUILD: builder step executed
    if any(s.get("station") == "builder" and s.get("status") == "executed" for s in steps):
        stages_reached.append("BUILD")

    # REVIEW: at least one reviewer-* step executed
    if any(str(s.get("station", "")).startswith("reviewer") and s.get("status") == "executed" for s in steps):
        stages_reached.append("REVIEW")

    # APPROVED: verdict is "approved"
    if verdict == "approved":
        stages_reached.append("APPROVED")

    # MERGED: merge record exists with merged=True
    merge_record = merge_records.get(work_order_id)
    if merge_record and merge_record.get("merged"):
        stages_reached.append("MERGED")

    # Current stage is the furthest reached
    current_stage = None
    for stage in reversed(LIFECYCLE_STAGES):
        if stage in stages_reached:
            current_stage = stage
            break

    # Check for needs_human flag
    needs_human = False
    decision = report.get("decision")
    if isinstance(decision, dict):
        human_gate = decision.get("human_gate", {})
        needs_human = human_gate.get("required", False)
    # Fallback to top-level human_required for older reports
    if not needs_human:
        needs_human = report.get("human_required", False)

    return {
        "stages_reached": stages_reached,
        "current_stage": current_stage,
        "needs_human": needs_human,
        "intake_state": None,
    }


def render_lifecycle_board(runs, merge_records):
    """Render the lifecycle board HTML showing stage progression for all work orders.

    Returns HTML string with one row per work order showing:
        - Work order ID and title
        - Stage progression (all stages with reached ones marked, current highlighted)
        - NEEDS HUMAN badge when applicable
        - Intake state (PARKED, REJECTED) when applicable
    """
    if not runs:
        return ""

    parts = ['<section class="lifecycle-board">']
    parts.append('<h2 class="board-title">Lifecycle Board</h2>')
    parts.append('<div class="board-description">Stage progression for each work order. Stages: SPEC → BUILD → REVIEW → APPROVED → MERGED.</div>')

    for report in runs:
        work_order_id = report.get("work_order_id", "-")
        title = report.get("title", "")

        stage_info = derive_lifecycle_stage(report, merge_records)

        parts.append(f'<div class="board-row">')
        parts.append(f'<div class="board-row-header">')
        parts.append(f'<h3 class="board-wo-id"><a href="#{_esc(work_order_id)}-detail" class="board-wo-id">{_esc(work_order_id)}</a></h3>')
        parts.append(f'<div class="board-wo-title">{_dash(title)}</div>')
        parts.append('</div>')

        # Show intake state if present
        if stage_info["intake_state"]:
            parts.append(f'<div class="board-intake-state state-{stage_info["intake_state"].lower()}">{stage_info["intake_state"]}</div>')
        else:
            # Show stage progression
            parts.append('<div class="board-stages">')
            for stage in LIFECYCLE_STAGES:
                reached = stage in stage_info["stages_reached"]
                is_current = stage == stage_info["current_stage"]
                classes = ["board-stage"]
                if reached:
                    classes.append("stage-reached")
                if is_current:
                    classes.append("stage-current")
                parts.append(f'<span class="{" ".join(classes)}">{stage}</span>')
            parts.append('</div>')

            # Show NEEDS HUMAN badge if applicable
            if stage_info["needs_human"]:
                parts.append('<div class="board-badge needs-human">NEEDS HUMAN</div>')

        parts.append('</div>')  # board-row

    parts.append('</section>')
    return "\n".join(parts)


def render_status_page(project, generated_at=None, projects=None):
    project = Path(project)
    runs, skipped = collect_runs(project, include_history=True)
    portfolio = [entry for entry in _portfolio_entries(projects) if entry["root"] != project.resolve()]
    all_steps = [s for r in runs for s in r.get("steps", [])]
    usage_summary = summarize_steps(all_steps)
    portfolio_steps = all_steps + [step for entry in portfolio
                                  for report in collect_runs(entry["root"], include_history=True)[0]
                                  for step in report.get("steps", [])]
    merge_records = load_merge_records(project)
    generated = generated_at or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    name = project.name
    anvil_json = project / "anvil.json"
    if anvil_json.exists():
        try:
            name = json.loads(anvil_json.read_text(encoding="utf-8")).get("project", name)
        except Exception:
            pass
    parts = ["<!DOCTYPE html>", '<html lang="en">', "<head>", '<meta charset="utf-8">',
             '<meta name="viewport" content="width=device-width, initial-scale=1">',
             f"<title>ANVIL run status: {_esc(name)}</title>",
             f"<style>{CSS}</style>", "</head>", "<body>", "<main>",
             f'<h1>ANVIL <span class="accent">run status</span></h1>',
             f'<div class="muted mono">project: {_esc(name)}</div>',
             f'<div class="snapshot">Snapshot generated from the run reports on disk at {_esc(generated)}. '
             "This page is a snapshot, not a live feed. Regenerate it with "
             '<span class="mono">anvil status-page &lt;project&gt;</span>.</div>']
    parts.append(_usage_panel(portfolio_steps, "Factory and project token consumption") if portfolio
                 else _usage_panel(all_steps, "Project token consumption"))
    exports = project / "report_exports.json"
    if exports.is_file():
        try:
            metadata = json.loads(exports.read_text(encoding="utf-8"))
            repository = metadata.get("repository", "")
            if re.fullmatch(r"[\w.-]+/[\w.-]+", repository):
                parts.append(f'<p class="usage-note">Reports imported from <a href="https://github.com/{_esc(repository)}">{_esc(repository)}</a> '
                             f'at {_esc(metadata.get("imported_at", "unknown time"))}. Refresh to include newer runs.</p>')
        except (OSError, ValueError, TypeError):
            pass
    parts.append('<p class="usage-note"><a href="usage.json">Download usage summary (JSON)</a></p>')
    if portfolio:
        parts.append('<section aria-label="Projects"><h2>Projects</h2><div class="project-grid">')
        parts.append(f'<article class="project-card"><h3><a href="#factory-runs">{_esc(name)}</a></h3>'
                     f'<p>{_number(usage_summary["total_tokens"])} tokens · {len(runs)} runs</p>'
                     f'<p class="usage-note">{usage_summary["measured_calls"]}/{usage_summary["calls"]} calls measured; '
                     f'{usage_summary["unmeasured_calls"]} unknown.</p></article>')
        for entry in portfolio:
            usage = entry["token_usage"]
            parts.append(f'<article class="project-card"><h3><a href="{_esc(entry["page"])}">{_esc(entry["name"])}</a></h3>'
                         f'<p>{_number(usage["total_tokens"])} tokens · {entry["runs"]} runs</p>'
                         f'<p class="usage-note">{usage["measured_calls"]}/{usage["calls"]} calls measured; {usage["unmeasured_calls"]} unknown.</p></article>')
        parts.append('</div></section>')
        parts.append('<h2 id="factory-runs">Factory runs</h2>')
    if not runs:
        parts.append('<div class="run">No readable run reports found under runs/.</div>')
    else:
        # Render lifecycle board
        parts.append(render_lifecycle_board([r for r in runs if not r.get("_archived")], merge_records))
    for report in runs:
        work_order_id = report.get('work_order_id', '-')
        anchor = work_order_id + ("-" + report["_record"] if report.get("_archived") else "")
        parts.append(f'<section class="run" id="{_esc(anchor)}-detail">')
        parts.append(f"<h2>{_esc(work_order_id)}</h2>")
        parts.append(f'<div>{_dash(report.get("title"))}</div>')
        if report.get("_archived"):
            parts.append('<p class="usage-note">Earlier run, preserved in the project consumption total.</p>')
        deployment = report.get("deployment_status")
        meta = [
            ("pipeline", _dash(report.get("pipeline"))),
            ("verdict", _status_span(report.get("verdict", "-"))),
            ("human review required", _esc(report.get("human_required", "-"))),
            ("deployment", _status_span(deployment) if deployment else "-"),
            ("loopbacks", _esc(report.get("loopbacks", "-"))),
        ]
        parts.append('<div class="meta">' + "".join(f"<span>{k}: <b>{v}</b></span>" for k, v in meta) + "</div>")
        parts.append(_decision_block(report))
        parts.append(_usage_panel(report.get("steps", []), "Run token consumption"))
        efficiency = report.get("efficiency") or {}
        if efficiency.get("limits"):
            caps = efficiency["limits"]
            parts.append(f'<p class="usage-note">Run threshold: {_number(caps.get("max_run_tokens"))} tokens; '
                         f'agent-call limit: {_number(caps.get("max_agent_calls"))}. '
                         'Checked between calls; a running call may exceed the threshold.</p>')
        for stopped in (s for s in report.get("steps", []) if s.get("status") == "budget_exceeded"):
            parts.append(f'<p class="usage-note">Stopped before {_esc(stopped.get("station"))}: {_esc(stopped.get("detail"))}</p>')
        parts.append('<div class="table-container">')
        parts.append("<table><thead><tr><th>Station</th><th>Status</th><th>Duration ms</th><th>Cost</th><th>Artifacts</th></tr></thead><tbody>")
        for step in report.get("steps", []):
            artifact_names = []
            for artifact in step.get("artifacts", []):
                path = Path(str(artifact))
                if path.is_absolute():
                    try:
                        path = path.relative_to(project.resolve())
                    except ValueError:
                        path = Path(path.name)
                artifact_names.append(str(path))
            artifacts = ", ".join(artifact_names) or "-"
            cost = step.get("cost")
            executed_model = step.get("executed_model")
            configured_model = step.get("configured_model")
            if executed_model:
                model_html = f"<div class='muted'>model: {_esc(executed_model)}</div>"
            elif configured_model:
                model_html = f"<div class='muted'>configured: {_esc(configured_model)}</div>"
            else:
                model_html = ""
            parts.append(
                f"<tr><td class='mono'>{_esc(step.get('station', '-'))}{model_html}{_step_usage(step)}</td>"
                f"<td>{_status_span(step.get('status', '-'))}</td>"
                f"<td>{_esc(step.get('duration_ms', '-'))}</td>"
                f"<td>{'null' if cost is None else _esc(cost)}</td>"
                f"<td class='artifacts'>{_esc(artifacts)}</td></tr>")
        parts.append("</tbody></table>")
        parts.append("</div>")  # table-container
        verify = report.get("verify_results") or []
        if verify:
            items = "".join(f"<li>{_status_span(v.get('status'))} <span class='mono'>{_esc(v.get('command', ''))}</span></li>" for v in verify)
            parts.append(f'<div class="meta"><span>verification:</span></div><ul>{items}</ul>')
        # Health results (post-deploy-health)
        health = report.get("health")
        if health and isinstance(health, dict):
            outcome = health.get("outcome", "unknown")
            parts.append('<div class="meta"><span>health verification:</span></div>')
            parts.append(f'<div class="decision"><div><span class="mono muted">outcome:</span> {_status_span(outcome)}</div>')
            if health.get("health_reason"):
                parts.append(f'<div><span class="mono muted">reason:</span> {_esc(health["health_reason"])}</div>')
            if health.get("route_results"):
                parts.append('<div class="table-container">')
                parts.append('<table><thead><tr><th>Route</th><th>Expected</th><th>Observed</th><th>Latency ms</th></tr></thead><tbody>')
                for route in health["route_results"]:
                    route_path = _esc(route.get("route", "-"))
                    expected = _esc(route.get("expected_status", "-"))
                    observed = _esc(route.get("observed_status", route.get("error", "-")))
                    latency = _esc(route.get("latency_ms", "-"))
                    parts.append(f"<tr><td>{route_path}</td><td>{expected}</td><td>{observed}</td><td>{latency}</td></tr>")
                parts.append('</tbody></table>')
                parts.append('</div>')  # table-container
            parts.append('</div>')  # decision
        parts.append("</section>")
    parts.append("<footer>Generated by ANVIL from run reports. Missing token usage stays unknown. Cost is null without reported usage and sourced prices; runtime cost estimates are labeled separately.")
    if skipped:
        parts.append(f"<br>Skipped run folders with a missing or unreadable report.json: {_esc(', '.join(skipped))}.")
    parts.append("</footer>")
    parts.append("</main></body></html>")
    return "\n".join(parts) + "\n", {"runs": len(runs), "skipped": skipped,
                                          "token_usage": usage_summary, "portfolio_token_usage": summarize_steps(portfolio_steps),
                                          "generated_at": generated,
                                          "projects": [{k: v for k, v in e.items() if k != "root"} for e in portfolio]}


def generate_status_page(project, out_dir=None, projects=None):
    project = Path(project)
    out = Path(out_dir) if out_dir else project / "status"
    out.mkdir(parents=True, exist_ok=True)
    if projects is None:
        from .config import load_anvil_config
        roots = load_anvil_config(project / "anvil.yaml").get("status_projects") or []
        projects = [project / root for root in roots]
    entries = _portfolio_entries(projects)
    page, summary = render_status_page(project, projects=projects)
    target = out / "index.html"
    target.write_text(page, encoding="utf-8")
    (out / "usage.json").write_text(json.dumps({"project": _project_name(project),
                                               "generated_at": summary["generated_at"],
                                               "token_usage": summary["token_usage"],
                                               "portfolio_token_usage": summary["portfolio_token_usage"],
                                               "runs": [public_report(r) for r in collect_runs(project, include_history=True)[0]],
                                               "projects": summary["projects"]}, indent=2) + "\n", encoding="utf-8")
    for entry in entries:
        generate_status_page(entry["root"], out / entry["page"].rsplit("/", 1)[0], projects=[])
    summary["path"] = str(target)
    return summary
