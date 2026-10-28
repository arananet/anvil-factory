"""Verified project memory: the brain gate.

The brain is memory that later stations trust as context. Agent written
learnings are therefore gated like code. A learning reaches the verified
store (brain/learnings.md) only when deterministic code can verify its
provenance against the run record on disk:

- the cited run report runs/<run-id>/report.json exists,
- the cited artifact exists,
- the evidence claim matches the report: "verdict <v>" requires the report
  verdict to be <v>, and "verify pass" requires a verify_results entry
  with status pass.

Proposals wait in brain/inbox/, quarantined: they are listed by
check-brain but are never station context and never fail the check.
Promotion is the only way in, and demotion is recorded as a decision, not
done silently. This is the factory's answer to benign memory
contamination: an early, wrong, agent written "fact" must not acquire
authority just because it was written down first.
"""

import json
import re
from pathlib import Path

from .model import slugify

LEARNINGS_HEADER = """# Learnings

Verified learnings for this project. An entry belongs here only after the
memory gate checked its provenance against the run record: the cited run
report exists, the cited artifact exists, and the evidence matches what
the report says. Proposed learnings wait in brain/inbox/ (quarantined)
and are never station context until `anvil promote-learning` verifies
them. `anvil check-brain` re-verifies every entry below.
"""

ENTRY_RE = re.compile(r"^## (L-\d+):\s*(.+?)\s*$")
PROVENANCE_RE = re.compile(r"^Provenance:\s*run\s+(\S+),\s*artifact\s+(\S+),\s*evidence\s+(.+?)\s*$")
DEMOTED_LINE = "Status: demoted"


def learnings_path(project):
    return Path(project) / "brain" / "learnings.md"


def inbox_dir(project):
    return Path(project) / "brain" / "inbox"


def ensure_brain_memory(project):
    """Create brain/learnings.md and brain/inbox/ when missing.

    Never overwrites an existing learnings.md. Returns the relative paths
    that were created (empty list when everything already existed).
    """
    project = Path(project)
    created = []
    target = learnings_path(project)
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(LEARNINGS_HEADER, encoding="utf-8")
        created.append("brain/learnings.md")
    inbox = inbox_dir(project)
    if not inbox.is_dir():
        inbox.mkdir(parents=True, exist_ok=True)
        created.append("brain/inbox/")
    return created


def parse_learnings(project):
    """Parse brain/learnings.md into entry dicts.

    Each entry: {id, claim, run, artifact, evidence, demoted, start, end}
    where start and end are line indexes of the entry block, and the
    provenance fields are None when the entry carries no provenance line.
    """
    path = learnings_path(project)
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    entries = []
    current = None
    for idx, line in enumerate(lines):
        m = ENTRY_RE.match(line)
        if m:
            if current is not None:
                current["end"] = idx
                entries.append(current)
            current = {"id": m.group(1), "claim": m.group(2), "run": None,
                       "artifact": None, "evidence": None, "demoted": False,
                       "start": idx, "end": len(lines)}
            continue
        if current is None:
            continue
        pm = PROVENANCE_RE.match(line)
        if pm and current["run"] is None:
            current["run"] = pm.group(1)
            current["artifact"] = pm.group(2)
            current["evidence"] = pm.group(3)
        if line.strip() == DEMOTED_LINE:
            current["demoted"] = True
    if current is not None:
        entries.append(current)
    return entries


def validate_provenance(project, run_id, artifact, evidence):
    """Check one provenance claim against the run record.

    Returns (ok, reason). The reason names exactly what failed, so a
    refusal is auditable instead of a bare no.
    """
    project = Path(project)
    if not run_id or not artifact or not evidence:
        return (False, "provenance is incomplete: run, artifact and evidence are all required")
    report_rel = f"runs/{run_id}/report.json"
    report_path = project / "runs" / run_id / "report.json"
    if not report_path.exists():
        return (False, f"run report not found: {report_rel}")
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except Exception:
        return (False, f"run report is unreadable: {report_rel}")
    artifact_path = Path(artifact)
    if not artifact_path.is_absolute():
        artifact_path = project / artifact_path
    if not artifact_path.exists():
        return (False, f"artifact not found: {artifact}")
    ev = str(evidence).strip()
    if ev.startswith("verdict "):
        wanted = ev[len("verdict "):].strip()
        actual = report.get("verdict")
        if actual != wanted:
            return (False, f"evidence says verdict {wanted} but run {run_id} report verdict is {actual}")
        return (True, "")
    if ev == "verify pass":
        results = report.get("verify_results") or []
        if not any(isinstance(v, dict) and v.get("status") == "pass" for v in results):
            return (False, f"evidence says verify pass but run {run_id} report has no passing verification")
        return (True, "")
    return (False, f"unsupported evidence kind: {evidence!r} (expected 'verdict <verdict>' or 'verify pass')")


def check_brain(project):
    """Re-verify the verified store. Inbox items are listed, never errors."""
    project = Path(project)
    entries = parse_learnings(project)
    problems = []
    checked = []
    for entry in entries:
        label = entry["id"]
        if entry["run"] is None:
            problems.append(f"{label}: missing or unreadable provenance line")
            checked.append({"id": label, "ok": False})
            continue
        ok, reason = validate_provenance(project, entry["run"], entry["artifact"], entry["evidence"])
        if not ok:
            problems.append(f"{label}: {reason}")
        checked.append({"id": label, "ok": ok})
    quarantined = []
    inbox = inbox_dir(project)
    if inbox.is_dir():
        quarantined = sorted(p.name for p in inbox.iterdir() if p.is_file())
    return {"ok": not problems, "entries": checked, "problems": problems,
            "quarantined": quarantined}


def propose_learning(project, claim, source_run, artifact, evidence):
    """Write one quarantined proposal to brain/inbox/. Returns its file name."""
    project = Path(project)
    ensure_brain_memory(project)
    base = slugify(claim)[:48].strip("-") or "learning"
    inbox = inbox_dir(project)
    name = f"{base}.md"
    counter = 2
    while (inbox / name).exists():
        name = f"{base}-{counter}.md"
        counter += 1
    text = (f"Claim: {claim}\nSource-Run: {source_run}\n"
            f"Artifact: {artifact}\nEvidence: {evidence}\n")
    (inbox / name).write_text(text, encoding="utf-8")
    return name


def parse_proposal(path):
    fields = {"claim": "", "source_run": "", "artifact": "", "evidence": ""}
    keys = {"Claim": "claim", "Source-Run": "source_run", "Artifact": "artifact", "Evidence": "evidence"}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        if key.strip() in keys:
            fields[keys[key.strip()]] = value.strip()
    return fields


def promote_learning(project, inbox_name):
    """Verify one inbox proposal and, only if it passes, file it as verified.

    Returns the new entry id (for example "L-3"). Raises ValueError with
    the specific refusal reason; on refusal nothing changes on disk.
    """
    project = Path(project)
    name = str(inbox_name)
    candidate = Path(name)
    if not candidate.is_absolute():
        candidate = inbox_dir(project) / name
    if not candidate.exists() and not candidate.suffix:
        candidate = inbox_dir(project) / f"{name}.md"
    if not candidate.exists():
        raise ValueError(f"inbox proposal not found: {inbox_name}")
    fields = parse_proposal(candidate)
    if not fields["claim"]:
        raise ValueError("proposal has no Claim")
    ok, reason = validate_provenance(project, fields["source_run"], fields["artifact"], fields["evidence"])
    if not ok:
        raise ValueError(reason)
    entries = parse_learnings(project)
    numbers = [int(e["id"].split("-", 1)[1]) for e in entries if e["id"].split("-", 1)[1].isdigit()]
    entry_id = f"L-{(max(numbers) + 1) if numbers else 1}"
    target = learnings_path(project)
    if not target.exists():
        ensure_brain_memory(project)
    block = (f"\n## {entry_id}: {fields['claim']}\n"
             f"Provenance: run {fields['source_run']}, artifact {fields['artifact']}, evidence {fields['evidence']}\n")
    text = target.read_text(encoding="utf-8")
    if text and not text.endswith("\n"):
        text += "\n"
    target.write_text(text + block, encoding="utf-8")
    candidate.unlink()
    return entry_id


def _next_decision_number(decisions_dir):
    numbers = []
    if decisions_dir.is_dir():
        for f in decisions_dir.iterdir():
            m = re.match(r"^(\d{4})-", f.name)
            if m:
                numbers.append(int(m.group(1)))
    return (max(numbers) + 1) if numbers else 1


def demote_learning(project, entry_id, reason):
    """Mark an entry demoted and record the decision. Returns the record path."""
    project = Path(project)
    target = learnings_path(project)
    if not target.exists():
        raise ValueError(f"no verified learnings store at {target}")
    entries = parse_learnings(project)
    entry = next((e for e in entries if e["id"] == entry_id), None)
    if entry is None:
        raise ValueError(f"learning entry not found: {entry_id}")
    if entry["demoted"]:
        raise ValueError(f"{entry_id} is already demoted")
    lines = target.read_text(encoding="utf-8").splitlines()
    # Insert the marker right after the provenance line when there is one,
    # else directly under the heading.
    insert_at = entry["start"] + 1
    for idx in range(entry["start"], entry["end"]):
        if PROVENANCE_RE.match(lines[idx]):
            insert_at = idx + 1
            break
    lines.insert(insert_at, DEMOTED_LINE)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    decisions_dir = project / "brain" / "decisions"
    decisions_dir.mkdir(parents=True, exist_ok=True)
    number = _next_decision_number(decisions_dir)
    record = decisions_dir / f"{number:04d}-demote-{entry_id.lower()}.md"
    record.write_text(
        f"# Decision {number:04d}: Demote learning {entry_id}\n\n"
        "Status: accepted\n\n"
        "## Decision\n"
        f"Learning {entry_id} (\"{entry['claim']}\") is demoted. It stays in "
        "brain/learnings.md with a demoted marker and stops being station context.\n\n"
        "## Why\n"
        f"{reason}\n",
        encoding="utf-8")
    return str(record.relative_to(project))


def verified_learnings(project):
    """The only learnings a station may ever see: verified and not demoted."""
    return [e for e in parse_learnings(project) if not e["demoted"]]


def packet_learnings_section(project):
    """Render the packet's Verified learnings section, or "" when empty."""
    entries = verified_learnings(project)
    if not entries:
        return ""
    lines = ["## Verified learnings", ""]
    for e in entries:
        lines.append(f"- {e['id']}: {e['claim']} "
                     f"(provenance: run {e['run']}, artifact {e['artifact']}, evidence {e['evidence']})")
    return "\n".join(lines)
