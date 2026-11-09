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
    # Practice skills R2: the practices base must be well formed and free of
    # active topic and scope conflicts. An absent base adds nothing.
    practice_entries, practice_problems = check_practices(project)
    problems.extend(practice_problems)
    return {"ok": not problems, "entries": checked, "problems": problems,
            "quarantined": quarantined,
            "practices": {"active": sum(1 for e in practice_entries if e["status"] == "active"),
                          "superseded": sum(1 for e in practice_entries if e["status"] == "superseded")}}


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

def packet_learnings_section_limited(project, max_chars):
    """S1 trim rule 3: Render learnings section limited to most recent entries that fit.

    Limits to the most recent learnings entries that fit within max_chars budget.
    Returns "" when empty or when even one entry exceeds the budget.
    """
    entries = verified_learnings(project)
    if not entries:
        return ""

    lines = ["## Verified learnings", ""]
    base_size = len("\n".join(lines))

    # Add entries in reverse order (most recent first) until budget is hit
    included = []
    current_size = base_size

    for e in reversed(entries):
        entry_line = (f"- {e['id']}: {e['claim']} "
                     f"(provenance: run {e['run']}, artifact {e['artifact']}, evidence {e['evidence']})")
        entry_size = len(entry_line) + 1  # +1 for newline

        if current_size + entry_size <= max_chars:
            included.insert(0, entry_line)  # Keep original order
            current_size += entry_size
        else:
            break

    if not included:
        return ""

    lines.extend(included)
    return "\n".join(lines)


# Practice skills base (spec: .openspec/specs/practice-skills/spec.md).
#
# A quarantined, provenance checked set of development best practices with
# explicit scope. Proposals wait in brain/inbox/ like learning proposals;
# promotion is the only way into brain/practices.md and runs the
# consistency check (R2). Resolution (R3) is plain deterministic code: no
# model takes part in deciding which practice reaches which station.
#
# Coordination note (R8): the scoped learnings work (issue 33) had not
# merged when this was written, so scope matching lives here
# (_scope_overlaps, _scope_matches) rather than in a shared helper.

PRACTICES_HEADER = """# Practices

Promoted practices for this project. An entry reaches this file only
through `anvil promote-practice`, which verifies its provenance and
refuses a second active rule for one topic in an overlapping scope.
Proposals wait in brain/inbox/ (quarantined) until promoted.
`anvil check-brain` validates every entry below.
"""

PRACTICE_HEAD_RE = re.compile(r"^## (P-\d+)(?::\s*(.*?))?\s*$")
PRACTICE_FIELDS = ("Topic", "Rule", "Languages", "Surfaces", "Stations",
                   "Enforcement", "Source", "Status")
PRACTICE_REQUIRED = ("Topic", "Rule", "Enforcement", "Source", "Status")
PRACTICE_ENFORCEMENTS = ("prompt", "gate")
PRACTICE_STATUSES = ("active", "superseded")
SCOPE_DIMENSIONS = ("languages", "surfaces", "stations")
DECISION_SOURCE_RE = re.compile(r"^decision\s+(\S+)\s*$")
RUN_SOURCE_RE = re.compile(r"^run\s+(\S+),\s*artifact\s+(\S+),\s*evidence\s+(.+?)\s*$")


def practices_path(project):
    return Path(project) / "brain" / "practices.md"


def _one_line(value):
    return " ".join(str(value or "").split())


def _scope_list(value):
    """Normalize a scope dimension to a sorted, lowercased, unique list."""
    if value is None:
        return []
    if isinstance(value, str):
        value = value.split(",")
    return sorted({_one_line(v).lower() for v in value if _one_line(v)})


def _scope_overlaps(a, b):
    """R2: two scopes overlap when every dimension shares a value or is unrestricted."""
    for dim in SCOPE_DIMENSIONS:
        va, vb = a.get(dim) or [], b.get(dim) or []
        if va and vb and not set(va) & set(vb):
            return False
    return True


def _scope_matches(practice, signals):
    """R3: conjunctive across dimensions, disjunctive within, empty unrestricted."""
    for dim in SCOPE_DIMENSIONS:
        wanted = practice.get(dim) or []
        if wanted and not set(wanted) & set(signals.get(dim) or []):
            return False
    return True


def _read_practices(project):
    """Parse brain/practices.md. Returns (entries, problems).

    Every heading that starts with "## " opens an entry; an entry that is
    not "## P-<n>: <topic>" with all required, valid fields is a problem.
    Only well formed entries are returned.
    """
    path = practices_path(project)
    if not path.exists():
        return [], []
    lines = path.read_text(encoding="utf-8").splitlines()
    blocks = []
    current = None
    for idx, line in enumerate(lines):
        if line.startswith("## "):
            if current is not None:
                current["end"] = idx
                blocks.append(current)
            current = {"heading": line, "fields": {}, "start": idx, "end": len(lines)}
            continue
        if current is None or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        if key in PRACTICE_FIELDS or key == "Supersedes":
            current["fields"].setdefault(key, value.strip())
    if current is not None:
        blocks.append(current)
    entries, problems, seen = [], [], set()
    for block in blocks:
        m = PRACTICE_HEAD_RE.match(block["heading"])
        if not m:
            problems.append(f"practices: malformed heading {block['heading']!r} (expected '## P-<n>: <topic>')")
            continue
        pid = m.group(1)
        f = block["fields"]
        missing = [k for k in PRACTICE_REQUIRED if not f.get(k)]
        if missing:
            problems.append(f"practices: {pid} is malformed, missing {', '.join(missing)}")
            continue
        enforcement = f["Enforcement"].lower()
        status = f["Status"].lower()
        if enforcement not in PRACTICE_ENFORCEMENTS:
            problems.append(f"practices: {pid} has invalid Enforcement {f['Enforcement']!r} (expected prompt or gate)")
            continue
        if status not in PRACTICE_STATUSES:
            problems.append(f"practices: {pid} has invalid Status {f['Status']!r} (expected active or superseded)")
            continue
        if pid in seen:
            problems.append(f"practices: duplicate id {pid}")
            continue
        seen.add(pid)
        entry = {"id": pid, "topic": f["Topic"], "rule": f["Rule"],
                 "enforcement": enforcement,
                 "languages": _scope_list(f.get("Languages", "")),
                 "surfaces": _scope_list(f.get("Surfaces", "")),
                 "stations": _scope_list(f.get("Stations", "")),
                 "source": f["Source"], "status": status,
                 "start": block["start"], "end": block["end"]}
        if f.get("Supersedes"):
            entry["supersedes"] = f["Supersedes"]
        entries.append(entry)
    return entries, problems


def _public_practice(entry):
    return {k: v for k, v in entry.items() if k not in ("start", "end")}


def parse_practices(project):
    """The well formed entries of brain/practices.md, in file order."""
    return [_public_practice(e) for e in _read_practices(project)[0]]


def _practice_sort_key(pid):
    tail = pid.split("-", 1)[1]
    return int(tail) if tail.isdigit() else 0


def practice_conflicts(entries):
    """Pairs of active practices with one topic and overlapping scope."""
    active = [e for e in entries if e["status"] == "active"]
    found = []
    for i, a in enumerate(active):
        for b in active[i + 1:]:
            if a["topic"] == b["topic"] and _scope_overlaps(a, b):
                found.append(f"practices: {a['id']} and {b['id']} are both active on topic "
                             f"{a['topic']} with overlapping scope")
    return found


def check_practices(project):
    """R2: validate the practices base. An absent base passes."""
    entries, problems = _read_practices(project)
    return entries, problems + practice_conflicts(entries)


def validate_practice_source(project, source):
    """R2: provenance to the learnings standard, or an owner decision record."""
    project = Path(project)
    source = _one_line(source)
    if not source:
        return (False, "practice has no Source")
    dm = DECISION_SOURCE_RE.match(source)
    if dm:
        rel = dm.group(1)
        decisions = (project / "brain" / "decisions").resolve()
        target = (project / rel).resolve()
        if decisions not in target.parents:
            return (False, f"decision source must be under brain/decisions/: {rel}")
        if not target.is_file():
            return (False, f"decision record not found: {rel}")
        return (True, "")
    rm = RUN_SOURCE_RE.match(source)
    if rm:
        return validate_provenance(project, rm.group(1), rm.group(2), rm.group(3))
    return (False, f"unsupported Source {source!r} (expected 'run <id>, artifact <path>, "
                   "evidence <evidence>' or 'decision brain/decisions/<file>')")


def propose_practice(project, topic, rule, enforcement="prompt", languages=(),
                     surfaces=(), stations=(), source="", supersedes=None):
    """Write one quarantined practice proposal to brain/inbox/. Returns its file name.

    Nothing is validated here beyond writing the fields; promotion is the
    gate. brain/practices.md is never touched.
    """
    project = Path(project)
    inbox = inbox_dir(project)
    inbox.mkdir(parents=True, exist_ok=True)
    base = "practice-" + (slugify(topic or "")[:40].strip("-") or "untitled")
    name = f"{base}.md"
    counter = 2
    while (inbox / name).exists():
        name = f"{base}-{counter}.md"
        counter += 1
    lines = ["Kind: practice",
             f"Topic: {_one_line(topic)}",
             f"Rule: {_one_line(rule)}",
             f"Languages: {', '.join(_scope_list(languages))}",
             f"Surfaces: {', '.join(_scope_list(surfaces))}",
             f"Stations: {', '.join(_scope_list(stations))}",
             f"Enforcement: {_one_line(enforcement)}",
             f"Source: {_one_line(source)}"]
    if supersedes:
        lines.append(f"Supersedes: {_one_line(supersedes)}")
    (inbox / name).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return name


def _parse_practice_proposal(path):
    fields = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields.setdefault(key.strip(), value.strip())
    return fields


def promote_practice(project, inbox_name):
    """Run the consistency check on one proposal and, only if it passes, promote it.

    Returns the new practice id (for example "P-1"). Raises ValueError
    naming the refusal reason; on refusal nothing changes on disk.
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
    f = _parse_practice_proposal(candidate)
    if f.get("Kind") != "practice":
        raise ValueError("proposal is malformed: not a practice proposal (missing 'Kind: practice')")
    topic, rule = f.get("Topic", ""), f.get("Rule", "")
    enforcement = f.get("Enforcement", "").lower()
    if not topic:
        raise ValueError("proposal is malformed: no Topic")
    if not rule:
        raise ValueError("proposal is malformed: no Rule")
    if enforcement not in PRACTICE_ENFORCEMENTS:
        raise ValueError(f"proposal is malformed: Enforcement {f.get('Enforcement', '')!r} "
                         "is not prompt or gate")
    entries, problems = check_practices(project)
    if problems:
        raise ValueError("practices base is invalid, fix it first: " + "; ".join(problems))
    ok, reason = validate_practice_source(project, f.get("Source", ""))
    if not ok:
        raise ValueError(reason)
    scope = {dim: _scope_list(f.get(dim.capitalize(), "")) for dim in SCOPE_DIMENSIONS}
    supersedes = f.get("Supersedes", "")
    by_id = {e["id"]: e for e in entries}
    if supersedes:
        old = by_id.get(supersedes)
        if old is None:
            raise ValueError(f"Supersedes names unknown practice {supersedes}")
        if old["status"] != "active":
            raise ValueError(f"Supersedes names {supersedes}, which is not active")
    for e in entries:
        if e["status"] != "active" or e["id"] == supersedes:
            continue
        if e["topic"] == topic and _scope_overlaps(e, scope):
            raise ValueError(f"conflicts with active practice {e['id']} on topic {topic} "
                             f"with overlapping scope; add Supersedes: {e['id']} to replace it")
    numbers = [_practice_sort_key(e["id"]) for e in entries]
    pid = f"P-{(max(numbers) + 1) if numbers else 1}"
    target = practices_path(project)
    text = target.read_text(encoding="utf-8") if target.exists() else PRACTICES_HEADER
    if supersedes:
        lines = text.splitlines()
        old = by_id[supersedes]
        for idx in range(old["start"], old["end"]):
            if lines[idx].split(":", 1)[0].strip() == "Status":
                lines[idx] = "Status: superseded"
                break
        text = "\n".join(lines) + "\n"
    if text and not text.endswith("\n"):
        text += "\n"
    block = [f"\n## {pid}: {topic}",
             f"Topic: {topic}",
             f"Rule: {rule}",
             f"Languages: {', '.join(scope['languages'])}",
             f"Surfaces: {', '.join(scope['surfaces'])}",
             f"Stations: {', '.join(scope['stations'])}",
             f"Enforcement: {enforcement}",
             f"Source: {f.get('Source', '')}"]
    if supersedes:
        block.append(f"Supersedes: {supersedes}")
    block.append("Status: active")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text + "\n".join(block) + "\n", encoding="utf-8")
    candidate.unlink()
    return pid


def resolve_practices(project, work_order, station_ids, config):
    """R3, R5: the practices that apply to each station of a work order.

    Signals: surfaces from the work order, the station list, and languages
    from the project config plus any languages the work order carries.
    Topics named in config practice_overrides (exact names) resolve
    nothing. Returns {"resolved": {station: [ids]}, "excluded_topics":
    [topics], "active_count": n}; ids are ordered by practice number.
    Deterministic standard library code; malformed entries never resolve.
    """
    config = config or {}
    entries = [e for e in _read_practices(project)[0] if e["status"] == "active"]
    entries.sort(key=lambda e: _practice_sort_key(e["id"]))
    overrides = config.get("practice_overrides") or []
    if isinstance(overrides, str):
        overrides = [overrides]
    overrides = {str(t).strip() for t in overrides if str(t).strip()}
    excluded = sorted({e["topic"] for e in entries if e["topic"] in overrides})
    candidates = [e for e in entries if e["topic"] not in overrides]
    languages = list(config.get("languages") or []) + list(getattr(work_order, "languages", None) or [])
    surfaces = list(getattr(work_order, "surfaces", None) or [])
    resolved = {}
    for station in station_ids:
        signals = {"languages": _scope_list(languages), "surfaces": _scope_list(surfaces),
                   "stations": _scope_list([station])}
        resolved[station] = [e["id"] for e in candidates if _scope_matches(e, signals)]
    return {"resolved": resolved, "excluded_topics": excluded, "active_count": len(entries)}


def practices_by_id(project):
    return {e["id"]: _public_practice(e) for e in _read_practices(project)[0]}


def packet_practices_section(project, resolution, station_id, entries=None):
    """R6: the Practices section for one station: prompt practices only, or ""."""
    entries = entries if entries is not None else practices_by_id(project)
    ids = (resolution or {}).get("resolved", {}).get(station_id, [])
    chosen = [entries[i] for i in ids if i in entries and entries[i]["enforcement"] == "prompt"]
    if not chosen:
        return ""
    lines = ["## Practices", "",
             "Promoted practices that resolved for this station. Follow each rule.", ""]
    for e in chosen:
        lines.append(f"- {e['id']} ({e['topic']}): {e['rule']}")
    return "\n".join(lines)


def gate_practices_section(project, resolution, entries=None):
    """R6: the checks gate listing of gate enforced practices, by id and topic, or ""."""
    entries = entries if entries is not None else practices_by_id(project)
    ids = set()
    for station_ids in (resolution or {}).get("resolved", {}).values():
        ids.update(station_ids)
    chosen = sorted((entries[i] for i in ids if i in entries and entries[i]["enforcement"] == "gate"),
                    key=lambda e: _practice_sort_key(e["id"]))
    if not chosen:
        return ""
    lines = ["## Gate practices", "",
             "Gate enforced practices this run resolved. The gate is accountable for them:", ""]
    for e in chosen:
        lines.append(f"- {e['id']}: {e['topic']}")
    return "\n".join(lines)
