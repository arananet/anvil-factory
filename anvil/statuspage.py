"""Run status page generator.

Reads every runs/<id>/report.json in a project and renders one self
contained HTML page: inline CSS, no external assets, so the file can be
dropped on Cloudflare Pages, GitHub Pages or any static host unchanged.

The page is a snapshot of the reports on disk at generation time. Nothing is
invented: cost stays null, and missing fields render as a dash. Runs whose
report is missing or unreadable are skipped and the skip is noted in the
page footer.
"""

import html
import json
from datetime import datetime, timezone
from pathlib import Path

CSS = """
:root { color-scheme: dark; }
body { background:#0C0C0C; color:#E8E8E8; font-family:Inter, system-ui, sans-serif; margin:0; padding:32px 20px 64px; }
main { max-width:1080px; margin:0 auto; }
h1 { font-size:28px; letter-spacing:.02em; margin:0 0 4px; }
h1 .accent { color:#FF5C00; }
h2 { font-family:ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size:17px; margin:0 0 6px; }
.mono { font-family:ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
.muted { color:#9A9A9A; }
.snapshot { border-left:3px solid #FF5C00; background:#1E1E1E; padding:10px 14px; margin:18px 0 28px; font-size:14px; }
.run { background:#1E1E1E; border:1px solid #2A2A2A; border-radius:8px; padding:18px 20px; margin:0 0 22px; }
.meta { display:flex; flex-wrap:wrap; gap:8px 22px; font-size:13px; color:#C9C9C9; margin:8px 0 14px; }
.meta b { color:#FFFFFF; font-weight:600; }
.decision { border-left:3px solid #3A3A3A; padding:8px 12px; margin:0 0 14px; font-size:13.5px; }
.decision div { margin:2px 0; }
table { width:100%; border-collapse:collapse; font-size:13px; }
th { text-align:left; font-family:ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-weight:600; color:#9A9A9A; border-bottom:1px solid #3A3A3A; padding:6px 8px; }
td { border-bottom:1px solid #2A2A2A; padding:6px 8px; vertical-align:top; }
.status { font-family:ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; white-space:nowrap; }
.st-ok { color:#FFFFFF; }
.st-failed { color:#FF5C00; }
.st-idle { color:#8A8A8A; }
.artifacts { color:#9A9A9A; word-break:break-all; }
footer { color:#8A8A8A; font-size:13px; margin-top:28px; }
""".strip()

STATUS_CLASS = {"completed": "st-ok", "executed": "st-ok", "approved": "st-ok",
                "failed": "st-failed", "rejected": "st-failed", "deploy_failed": "st-failed",
                "deployed_unverified": "st-failed"}


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


def collect_runs(project):
    """Return (runs, skipped): parsed report dicts and skipped folder names."""
    runs = []
    skipped = []
    runs_dir = Path(project) / "runs"
    if runs_dir.is_dir():
        for folder in sorted(p for p in runs_dir.iterdir() if p.is_dir()):
            report_file = folder / "report.json"
            if not report_file.exists():
                skipped.append(folder.name)
                continue
            try:
                data = json.loads(report_file.read_text(encoding="utf-8"))
                if not isinstance(data, dict) or "work_order_id" not in data:
                    raise ValueError("report has no work_order_id")
                runs.append(data)
            except Exception:
                skipped.append(folder.name)
    runs.sort(key=lambda r: str(r.get("work_order_id", "")))
    return runs, skipped


def render_status_page(project, generated_at=None):
    project = Path(project)
    runs, skipped = collect_runs(project)
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
    if not runs:
        parts.append('<div class="run">No readable run reports found under runs/.</div>')
    for report in runs:
        parts.append('<section class="run">')
        parts.append(f"<h2>{_esc(report.get('work_order_id', '-'))}</h2>")
        parts.append(f'<div>{_dash(report.get("title"))}</div>')
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
        parts.append("<table><thead><tr><th>Station</th><th>Status</th><th>Duration ms</th><th>Cost</th><th>Artifacts</th></tr></thead><tbody>")
        for step in report.get("steps", []):
            artifacts = ", ".join(str(a) for a in step.get("artifacts", [])) or "-"
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
                f"<tr><td class='mono'>{_esc(step.get('station', '-'))}{model_html}</td>"
                f"<td>{_status_span(step.get('status', '-'))}</td>"
                f"<td>{_esc(step.get('duration_ms', '-'))}</td>"
                f"<td>{'null' if cost is None else _esc(cost)}</td>"
                f"<td class='artifacts'>{_esc(artifacts)}</td></tr>")
        parts.append("</tbody></table>")
        verify = report.get("verify_results") or []
        if verify:
            items = "".join(f"<li>{_status_span(v.get('status'))} <span class='mono'>{_esc(v.get('command', ''))}</span></li>" for v in verify)
            parts.append(f'<div class="meta"><span>verification:</span></div><ul>{items}</ul>')
        parts.append("</section>")
    parts.append("<footer>Generated by ANVIL from runs/*/report.json. Cost is null unless a runtime reported it; ANVIL never invents a number.")
    if skipped:
        parts.append(f"<br>Skipped run folders with a missing or unreadable report.json: {_esc(', '.join(skipped))}.")
    parts.append("</footer>")
    parts.append("</main></body></html>")
    return "\n".join(parts) + "\n", {"runs": len(runs), "skipped": skipped}


def generate_status_page(project, out_dir=None):
    project = Path(project)
    out = Path(out_dir) if out_dir else project / "status"
    out.mkdir(parents=True, exist_ok=True)
    page, summary = render_status_page(project)
    target = out / "index.html"
    target.write_text(page, encoding="utf-8")
    summary["path"] = str(target)
    return summary
