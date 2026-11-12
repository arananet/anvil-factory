#!/usr/bin/env python3
"""Render the issue comment for a run of the anvil-line workflow.

Usage: line_comment.py <report.json> <exit_code> [run_url] [branch]

Reads only the run report, never station output, and prints markdown. The
next step a human can take is derived from the exit code of the CLI
(anvil/line.py exit_code), so the comment and the job outcome agree.
"""

import json
import sys
from pathlib import Path

NEXT = {
    0: "The line approved this work and no human gate is closed. The pull request is ready for review.",
    1: "The line did not approve this work. Read the findings in the run report, fix the cause, and "
       "relabel the issue with `anvil` to run the line again.",
    3: "A human decision is needed. A maintainer can comment `/anvil approve` on this issue to record "
       "the approval and resume the line (`/anvil approve --override` when the line's verdict was not "
       "approved; the override is recorded).",
    4: "Intake stopped this order. Update the issue with the missing information and relabel it with "
       "`anvil`.",
}


def cell(value):
    return str(value if value is not None else "").replace("|", "\\|").replace("\n", " ")[:160]


def render(report, code, run_url="", branch=""):
    decision = report.get("decision") or {}
    lines = [
        "## ANVIL line report", "",
        f"- Work order: {cell(report.get('work_order_id'))}",
        f"- Pipeline: {cell(report.get('pipeline'))}",
        f"- Verdict: {cell(report.get('verdict'))}",
        f"- Loopbacks used: {report.get('loopbacks', 0)} of {report.get('max_loopbacks', 0)}",
        f"- Human review required: {report.get('human_required')}",
        f"- Deployment status: {cell(report.get('deployment_status'))}",
    ]
    previews = [s for s in report.get("steps") or [] if s.get("station") == "preview" and s.get("url")]
    if previews:
        last = previews[-1]
        lines.append(f"- Preview: {cell(last['url'])}" + ("" if last.get("status") == "completed" else " (deploy failed)"))
    if branch:
        lines.append(f"- Branch: `{cell(branch)}`")
    if run_url:
        lines.append(f"- Workflow run: {run_url}")
    lines += ["", "Decision record:",
              f"- Approver: {cell((decision.get('approver') or {}).get('rule'))[:160]}",
              f"- Human gate: {cell((decision.get('human_gate') or {}).get('rule'))[:160]}",
              "", "| Station | Status | Attempt | Model |", "|---|---|---|---|"]
    for step in report.get("steps") or []:
        lines.append(f"| {cell(step.get('station'))} | {cell(step.get('status'))} | "
                     f"{step.get('attempt', 1)} | {cell(step.get('executed_model') or step.get('configured_model'))} |")
    warnings = report.get("warnings") or []
    if warnings:
        lines += ["", "Warnings:"] + [f"- {cell(w)}" for w in warnings]
    lines += ["", NEXT.get(code, NEXT[1])]
    return "\n".join(lines) + "\n"


def main(argv):
    if len(argv) < 3:
        print(__doc__, file=sys.stderr)
        return 2
    path = Path(argv[1])
    code = int(argv[2])
    if not path.is_file():
        print("## ANVIL line report\n\nThe run produced no report.json, so there is no verdict to report."
              + (f" See the workflow run: {argv[3]}" if len(argv) > 3 else "") + "\n")
        return 0
    report = json.loads(path.read_text(encoding="utf-8"))
    print(render(report, code, argv[3] if len(argv) > 3 else "", argv[4] if len(argv) > 4 else ""), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
