"""The autonomous line: what lets a work order travel from an issue to an
approved, resumable run without a hand written workflow per order.

Everything here is deterministic and standard library only:

- work_order_from_issue: a GitHub issue becomes a work order (same shape the
  intake worker produces), so one generic workflow serves every order.
- exit_code: a run's outcome as a process exit code, so CI can gate on it.
- record_approval / load_resume: the human gate as a recorded act bound to
  one run, and the state a resumed run re-enters with.
- isolate / commit_run: a run on its own branch in its own git worktree, so
  the checkout the operator is working in is never the tree a station edits.

See .openspec/specs/autonomous-line/spec.md.
"""

import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from .gates import RISK_HINTS
from .model import KINDS, validate_path_component

APPROVAL_FILE = "human-approval.json"

EXIT_OK = 0
EXIT_NOT_APPROVED = 1
EXIT_USAGE = 2
EXIT_HUMAN_GATE = 3
EXIT_INTAKE_STOPPED = 4

# Verdicts a human can approve. "approved" waits on the gate because of a
# risk hint; "human_required" is an otherwise passing run with an uncounted
# reviewer. The override set needs the explicit --override flag: the line
# said no and a human takes responsibility for saying yes.
APPROVABLE = {"approved", "human_required"}
APPROVABLE_WITH_OVERRIDE = {"rejected", "changes_requested", "no_reviews"}
BAD_DEPLOYS = {"deploy_failed", "deployed_unverified", "deployed_and_unhealthy"}
PIPELINE_LABEL = re.compile(r"^pipeline:([a-z0-9][a-z0-9-]*)$")


def _label_names(issue):
    labels = issue.get("labels") or []
    names = []
    for label in labels:
        name = label if isinstance(label, str) else (label or {}).get("name")
        if name:
            names.append(str(name).strip().lower())
    return names


def work_order_from_issue(issue):
    """Map a GitHub issue object to (work_order_dict, pipeline_name_or_None).

    Labels carry the structured part: a label equal to a work order kind sets
    the kind (first match wins, default feature), a label equal to a risk
    hint (bare or as risk:<hint>) sets a risk hint, and pipeline:<name>
    selects the pipeline. The issue body is the description, verbatim; it is
    operator input and reaches stations only through the sanitized packet.
    """
    if not isinstance(issue, dict) or not isinstance(issue.get("number"), int):
        raise ValueError("issue must be an object with an integer number")
    labels = _label_names(issue)
    kind = next((name for name in labels if name in KINDS), "feature")
    hints = []
    for name in labels:
        hint = name[len("risk:"):] if name.startswith("risk:") else name
        if hint in RISK_HINTS and hint not in hints:
            hints.append(hint)
    pipeline = None
    for name in labels:
        match = PIPELINE_LABEL.match(name)
        if match:
            pipeline = match.group(1)
            break
    body = str(issue.get("body") or "")
    url = str(issue.get("html_url") or "")
    description = "\n".join([body, "", f"GitHub issue: {url}"]).strip()
    work_order = {
        "id": f"wo-gh-{issue['number']}",
        "kind": kind,
        "title": str(issue.get("title") or "GitHub issue"),
        "source": "github-issue",
        "description": description,
        "risk_hints": hints,
        "status": "new",
    }
    return work_order, pipeline


def exit_code(report, executed, work_order_status=None):
    """The process exit code for a run report.

    0: the run ended well (approved with the human gate open, a healthy
       deploy, or a packet-only run, which judges nothing).
    1: the line did not approve the work, a step failed, or a deploy went bad.
    3: the work is approved or awaiting a decision, and a human must act
       (anvil approve, then anvil resume).
    4: intake stopped the order (rejected, or waiting for information).
    """
    if not executed:
        return EXIT_OK
    if work_order_status in {"rejected", "waiting_info"}:
        return EXIT_INTAKE_STOPPED
    verdict = report.get("verdict")
    if report.get("deployment_status") in BAD_DEPLOYS:
        return EXIT_NOT_APPROVED
    approved_by_human = ((report.get("decision") or {}).get("human_gate") or {}).get("approval")
    if approved_by_human and not report.get("human_required"):
        return EXIT_OK
    if verdict == "approved":
        return EXIT_HUMAN_GATE if report.get("human_required") else EXIT_OK
    if verdict == "human_required":
        return EXIT_HUMAN_GATE
    if verdict == "packet_ready":
        failed = any(step.get("status") == "failed" for step in report.get("steps") or [])
        return EXIT_NOT_APPROVED if failed else EXIT_OK
    return EXIT_NOT_APPROVED


def _run_dir(project, work_order_id):
    validate_path_component(work_order_id, "work_order_id")
    return Path(project) / "runs" / work_order_id


def _load_report(project, work_order_id):
    path = _run_dir(project, work_order_id) / "report.json"
    if not path.is_file():
        raise ValueError(f"no run report at {path}; run the line first")
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise ValueError(f"run report {path} is not valid JSON: {exc}")
    if not isinstance(report, dict):
        raise ValueError(f"run report {path} is not an object")
    return report


def record_approval(project, work_order_id, approved_by, note="", override=False):
    """Record a human approval for the current run of a work order.

    The approval names the run it approves (run_id), so a rerun of the line
    voids it. Returns the approval record. Raises ValueError when there is
    nothing a human can approve.
    """
    approved_by = str(approved_by or "").strip()
    if not approved_by:
        raise ValueError("an approval needs a name (--by)")
    report = _load_report(project, work_order_id)
    verdict = report.get("verdict")
    status = report.get("deployment_status")
    if status and status != "deploy_failed":
        raise ValueError(f"this run already deployed ({status}); there is nothing left to approve")
    if verdict in APPROVABLE_WITH_OVERRIDE and not override:
        raise ValueError(f"the line's verdict is {verdict}; approving it anyway needs --override, "
                         f"and the override is recorded")
    if verdict not in APPROVABLE and verdict not in APPROVABLE_WITH_OVERRIDE:
        raise ValueError(f"the run ended {verdict}, which is not a decision a human can approve; "
                         f"fix the cause and run the line again")
    record = {
        "schema": "anvil/approval@1",
        "work_order_id": work_order_id,
        "run_id": report.get("run_id"),
        "approver_verdict": verdict,
        "approved_by": approved_by,
        "approved_at": datetime.now(timezone.utc).isoformat(),
        "note": str(note or ""),
        "override": bool(override) and verdict in APPROVABLE_WITH_OVERRIDE,
    }
    path = _run_dir(project, work_order_id) / APPROVAL_FILE
    path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record


def load_resume(project, work_order_id):
    """The state a resumed run re-enters with: {"report", "approval"}.

    Raises ValueError when the run cannot be resumed: no report, already
    deployed, an approval recorded for a different run, or a closed human
    gate with no approval on record.
    """
    report = _load_report(project, work_order_id)
    status = report.get("deployment_status")
    if status and status != "deploy_failed":
        raise ValueError(f"this run already deployed ({status}); nothing to resume")
    approval = None
    path = _run_dir(project, work_order_id) / APPROVAL_FILE
    if path.is_file():
        try:
            approval = json.loads(path.read_text(encoding="utf-8"))
        except ValueError:
            raise ValueError(f"{path} is not valid JSON")
        if not isinstance(approval, dict) or approval.get("schema") != "anvil/approval@1":
            raise ValueError(f"{path} is not an approval record")
        if approval.get("run_id") != report.get("run_id") or approval.get("work_order_id") != work_order_id:
            raise ValueError("the recorded approval is for a different run of this work order; "
                             "approve the current run first")
    verdict = report.get("verdict")
    if approval is None:
        if verdict != "approved":
            raise ValueError(f"the run's verdict is {verdict} and no human approval is recorded; "
                             f"nothing to resume")
        if report.get("human_required"):
            raise ValueError("the human gate is closed and no approval is recorded; "
                             "run anvil approve first")
    return {"report": report, "approval": approval}


def _git(args, cwd, check=True):
    proc = subprocess.run(["git"] + list(args), cwd=str(cwd), capture_output=True, text=True, timeout=120)
    if check and proc.returncode != 0:
        raise ValueError(f"git {' '.join(args)} failed: {(proc.stderr or proc.stdout).strip()[:400]}")
    return proc


def branch_name(work_order_id):
    validate_path_component(work_order_id, "work_order_id")
    return f"anvil/{work_order_id}"


def isolate(project, work_order_id):
    """Give a work order its own branch and worktree; return (worktree, branch).

    The worktree lives beside the project, never inside it. An existing
    branch for the order is reused, so a resumed run continues on the tree
    the first run left; otherwise the branch starts at the project's HEAD.
    Uncommitted changes in the project checkout are not carried over.
    """
    project = Path(project).resolve()
    top = _git(["rev-parse", "--show-toplevel"], project).stdout.strip()
    if Path(top).resolve() != project:
        raise ValueError("--isolate needs the project to be the root of a git repository")
    branch = branch_name(work_order_id)
    worktree = project.parent / ".anvil-worktrees" / project.name / work_order_id
    if worktree.is_dir() and (worktree / ".git").exists():
        current = _git(["rev-parse", "--abbrev-ref", "HEAD"], worktree).stdout.strip()
        if current != branch:
            raise ValueError(f"{worktree} exists on branch {current}, expected {branch}")
        return worktree, branch
    worktree.parent.mkdir(parents=True, exist_ok=True)
    _git(["worktree", "prune"], project, check=False)
    exists = _git(["rev-parse", "--verify", "--quiet", f"refs/heads/{branch}"], project, check=False).returncode == 0
    if exists:
        _git(["worktree", "add", str(worktree), branch], project)
    else:
        _git(["worktree", "add", "-b", branch, str(worktree), "HEAD"], project)
    return worktree, branch


def commit_run(worktree, work_order_id, message):
    """Commit the station changes and the run evidence on the run branch.

    The run directory is force added because projects commonly ignore runs/.
    Returns the commit id, or None when the run changed nothing.
    """
    worktree = Path(worktree)
    _git(["add", "-A"], worktree)
    if (worktree / "runs" / work_order_id).is_dir():
        _git(["add", "-f", str(Path("runs") / work_order_id)], worktree)
    if _git(["diff", "--cached", "--quiet"], worktree, check=False).returncode == 0:
        return None
    identity = []
    if _git(["config", "user.email"], worktree, check=False).returncode != 0:
        identity = ["-c", "user.name=anvil", "-c", "user.email=anvil@localhost"]
    _git(identity + ["commit", "-q", "-m", message], worktree)
    return _git(["rev-parse", "HEAD"], worktree).stdout.strip()
