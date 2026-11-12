import json, os, re, subprocess
from pathlib import Path

REVIEWER_STATIONS = ["reviewer-spec", "reviewer-security", "reviewer-tests", "reviewer-architecture"]
RISK_HINTS = {"auth", "payments", "data-deletion", "production-deploy", "secrets", "publishing"}

def spec_gate(project_dir, slug):
    spec = Path(project_dir) / ".openspec" / "specs" / slug / "spec.md"
    if not spec.exists():
        return (False, f"Spec not found: {spec}")
    text = spec.read_text(encoding="utf-8")
    if "Scenario:" not in text:
        return (False, "Spec has no Scenario: line")
    if "Status:" not in text:
        return (False, "Spec has no Status line")
    return (True, "Spec present with scenarios and status")

def scenario_ids(project_dir, slug):
    spec = Path(project_dir) / ".openspec" / "specs" / slug / "spec.md"
    if not spec.exists():
        return []
    text = spec.read_text(encoding="utf-8")
    ids = []
    for m in re.finditer(r"\b(S\d+)\b", text):
        if m.group(1) not in ids:
            ids.append(m.group(1))
    return ids

def tdd_gate(project_dir, slug):
    ids = scenario_ids(project_dir, slug)
    if not ids:
        return (False, "No scenario ids found in spec")
    tests_dir = Path(project_dir) / "tests"
    if not tests_dir.is_dir():
        return (False, "No tests directory")
    combined = ""
    for f in tests_dir.rglob("*"):
        if f.is_file():
            try:
                combined += f.read_text(encoding="utf-8") + "\n"
            except UnicodeDecodeError:
                pass
    missing = [sid for sid in ids if sid not in combined]
    if missing:
        return (False, f"Scenarios without test references: {', '.join(missing)}")
    return (True, f"All {len(ids)} scenarios referenced in tests")

def review_gate(project_dir, slug):
    base = Path(project_dir) / "reviews" / slug
    for station in REVIEWER_STATIONS:
        f = base / f"{station}.json"
        if not f.exists():
            return (False, f"Missing review: {f}")
        data = json.loads(f.read_text(encoding="utf-8"))
        if data.get("verdict") != "pass":
            return (False, f"Review {station} verdict is {data.get('verdict')}, not pass")
    # Reviews beyond the core panel (for example reviewer-design, reviewer-ux)
    # are not required to exist, but one that is on record must pass too.
    extra = sorted(f for f in base.glob("reviewer-*.json") if f.stem not in REVIEWER_STATIONS)
    for f in extra:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except ValueError:
            return (False, f"Review {f.stem} is not valid JSON")
        if not isinstance(data, dict) or data.get("verdict") != "pass":
            return (False, f"Review {f.stem} verdict is {data.get('verdict') if isinstance(data, dict) else None}, not pass")
    return (True, f"All {len(REVIEWER_STATIONS) + len(extra)} reviews present and passing")

def human_gate(work_order):
    hints = set(getattr(work_order, "risk_hints", []) or [])
    if isinstance(work_order, dict):
        hints = set(work_order.get("risk_hints", []))
    return "required" if hints & RISK_HINTS else "not_required"


def brief_gate(project_dir, slug):
    brief = Path(project_dir) / "content" / slug / "brief.md"
    if not brief.exists():
        return (False, f"Brief not found: {brief}")
    text = brief.read_text(encoding="utf-8")
    for field in ("Audience:", "Angle:", "Claims:"):
        if field not in text:
            return (False, f"Brief is missing {field}")
    return (True, "Brief present with audience, angle and claims")

def disclosure_gate(project_dir, slug):
    draft = Path(project_dir) / "content" / slug / "draft.md"
    if not draft.exists():
        return (False, f"Draft not found: {draft}")
    text = draft.read_text(encoding="utf-8").lower()
    if "ai generated" not in text and "ai-generated" not in text:
        return (False, "Draft has no AI generated disclosure")
    return (True, "Draft carries an AI generated disclosure")


def _run_shell(command, cwd, work_order_id, timeout, scrub=False):
    """Execute a shell command with timeout.

    scrub=True removes deploy and repository credentials from the command's
    environment. Project checks run code the line itself just wrote, so they
    get the same reduced environment as a station; deploy commands do not.
    """
    env = dict(os.environ)
    if scrub:
        from .executor import station_env
        env = station_env(env, {})
    env["ANVIL_WORK_ORDER_ID"] = work_order_id
    try:
        proc = subprocess.run(command, shell=True, cwd=str(cwd), env=env,
                              capture_output=True, text=True, timeout=timeout)
        return proc.returncode, (proc.stdout or "") + (proc.stderr or "")
    except subprocess.TimeoutExpired:
        return None, f"Timed out after {timeout}s"


def derive_base_ref(project_dir, base_branch=None):
    """Derive the base ref for a git repository.

    Loopback round 3: When a run starts in a git repository and no explicit base
    ref is supplied, derive it as the merge base of HEAD and the project's base
    branch (defaulting to the repository's default branch).

    Args:
        project_dir: Path to project directory
        base_branch: Name of the base branch (e.g., "main"). If None, uses repo default.

    Returns:
        Base ref SHA as a string, or None if not in a git repo or derivation fails.
    """
    try:
        # Check if this is a git repo
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode != 0:
            return None

        # If no base_branch specified, get the repository's default branch
        if not base_branch:
            # Try to get the default branch from the remote
            result = subprocess.run(
                ["git", "symbolic-ref", "refs/remotes/origin/HEAD"],
                cwd=str(project_dir),
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                # Output is like "refs/remotes/origin/main", extract the branch name
                base_branch = result.stdout.strip().split('/')[-1]
            else:
                # Fallback: try common default branch names
                for candidate in ["main", "master"]:
                    result = subprocess.run(
                        ["git", "rev-parse", "--verify", f"refs/heads/{candidate}"],
                        cwd=str(project_dir),
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if result.returncode == 0:
                        base_branch = candidate
                        break

            if not base_branch:
                # Last resort: use HEAD itself
                result = subprocess.run(
                    ["git", "rev-parse", "HEAD"],
                    cwd=str(project_dir),
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    return result.stdout.strip()
                return None

        # Find merge base of HEAD and base_branch
        result = subprocess.run(
            ["git", "merge-base", "HEAD", base_branch],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return result.stdout.strip()

    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass

    return None


def resolve_base_ref_config(project_dir, base_ref=None, config_filename="anvil.json"):
    """Resolve project configuration from base ref using git.

    S4 requirement: check commands and protected paths are resolved from the base
    ref snapshot taken at run start, never from files the builder changed during
    the run. This function reads the configuration from the git base ref when
    available, falling back to the working tree file only when git is not present.

    Args:
        project_dir: Path to project directory
        base_ref: Git ref to resolve from (e.g., commit SHA). If None, reads from working tree.
        config_filename: Name of the config file (default: "anvil.json")

    Returns:
        Dict with configuration, or empty dict if config cannot be read.
    """
    project_path = Path(project_dir)
    config_file = project_path / config_filename

    # If base_ref is provided, try to resolve from git
    if base_ref:
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
                # Read config from base ref using git show
                result = subprocess.run(
                    ["git", "show", f"{base_ref}:{config_filename}"],
                    cwd=str(project_dir),
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    try:
                        return json.loads(result.stdout)
                    except json.JSONDecodeError:
                        pass
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass

    # Fallback: read from working tree file
    # This fallback is only safe for projects without a git repo
    if config_file.exists():
        try:
            return json.loads(config_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass

    return {}


def _get_base_ref_files(project_dir, base_ref):
    """Get set of files that existed in the base ref.

    Args:
        project_dir: Path to project directory
        base_ref: Git ref to resolve from (if None, tries to infer from git)

    Returns:
        Set of file paths that existed in base ref, or empty set if can't determine.
    """
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
            # If no base_ref provided, try to infer it
            ref_to_use = base_ref
            if not ref_to_use:
                # Try HEAD (last commit on current branch)
                result = subprocess.run(
                    ["git", "rev-parse", "HEAD"],
                    cwd=str(project_dir),
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    ref_to_use = result.stdout.strip()

            if ref_to_use:
                # Get list of files in base ref
                result = subprocess.run(
                    ["git", "ls-tree", "-r", "--name-only", ref_to_use],
                    cwd=str(project_dir),
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    return {line.strip() for line in result.stdout.split('\n') if line.strip()}
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass

    return set()


def checks_gate(phase, base_ref_config, changed_files, project_dir, work_order_id, timeout=300, base_ref=None, basis="builder_delta", attempt=None):
    """Run the checks gate: execute check commands and validate protected paths.

    Loopback round 2 semantics: The protected path check judges only the builder
    station's changes for the current attempt (the working tree delta across the
    builder execution). A violation is the builder modifying or deleting a base ref
    file under a protected prefix. Builder additions are recorded as observed
    additions, not violations. Each attempt is judged on its own delta.

    Args:
        phase: "pre-review" or "pre-deploy"
        base_ref_config: Configuration dict resolved from base ref
        changed_files: Set of changed file paths relative to project root (builder's delta)
        project_dir: Path to project directory
        work_order_id: Work order ID for logging
        timeout: Timeout in seconds for each check command
        base_ref: Git ref that the work branched from (for determining base ref files)
        basis: Description of what files are being judged (e.g., "builder_delta")
        attempt: Attempt number being judged (optional)

    Returns:
        Dict with gate results including status, commands, exit_codes,
        protected_path_verdict, gate_verdict, basis, observed_additions, and output.
    """
    checks = base_ref_config.get("checks", [])

    # Get protected paths from base ref config
    # Default includes the checks configuration file path and tests/
    if "protected_paths" in base_ref_config:
        protected_paths = base_ref_config["protected_paths"]
    else:
        # Default protected paths: tests/ and the configuration file itself
        # The config file path comes from the project structure, not hardcoded
        config_file_name = "anvil.json"  # Standard config file name
        protected_paths = ["tests/", config_file_name]

    # Build basis description
    basis_str = f"{basis}" + (f" (attempt {attempt})" if attempt else "")

    # If no checks configured (S6)
    if not checks:
        return {
            "phase": phase,
            "status": "not_configured",
            "detail": "No checks configured",
            "commands": [],
            "exit_codes": [],
            "protected_paths": protected_paths,
            "protected_path_verdict": "pass",
            "protected_path_findings": [],
            "observed_additions": [],
            "gate_verdict": "not_configured",
            "basis": basis_str,
            "output": ""
        }

    # Get base ref files to distinguish additions from modifications/deletions
    base_ref_files = _get_base_ref_files(project_dir, base_ref)

    # Check for protected path violations (Loopback round 2)
    # Violations: builder modifying or deleting a base ref file under a protected path
    # Observed: builder adding a new file under a protected path (not a violation)
    protected_path_findings = []
    observed_additions = []

    for changed_file in changed_files:
        # Check if file is under a protected path
        is_protected = False
        matched_prefix = None
        for protected_path in protected_paths:
            if changed_file.startswith(protected_path):
                is_protected = True
                matched_prefix = protected_path
                break

        if is_protected:
            # Determine if this is an addition or modification/deletion
            if changed_file in base_ref_files:
                # Modification or deletion of existing base ref file -> VIOLATION
                protected_path_findings.append(
                    f"Protected path violation: {changed_file} (base ref file modified/deleted, matches {matched_prefix})")
            else:
                # Addition of new file -> OBSERVED, not a violation
                observed_additions.append(
                    f"Protected path addition (observed): {changed_file} (matches {matched_prefix})")

    protected_path_verdict = "fail" if protected_path_findings else "pass"

    # Run check commands
    commands = []
    exit_codes = []
    outputs = []

    for check_cmd in checks:
        commands.append(check_cmd)
        code, out = _run_shell(str(check_cmd), project_dir, work_order_id, timeout, scrub=True)
        exit_codes.append(code if code is not None else -1)
        outputs.append(out)

    # Determine overall gate verdict
    checks_passed = all(code == 0 for code in exit_codes)

    if protected_path_verdict == "fail":
        gate_verdict = "fail"
        status = "failed"
    elif not checks_passed:
        gate_verdict = "fail"
        status = "failed"
    else:
        gate_verdict = "pass"
        status = "passed"

    # Build output summary
    output_lines = []
    output_lines.append(f"# Checks Gate: {phase}")
    output_lines.append(f"Basis: {basis}")
    if attempt is not None:
        output_lines.append(f"Attempt: {attempt}")
    output_lines.append("")

    if protected_path_findings:
        output_lines.append("# Protected Path Violations")
        output_lines.extend(protected_path_findings)
        output_lines.append("")

    if observed_additions:
        output_lines.append("# Protected Path Additions (Observed, Not Violations)")
        output_lines.extend(observed_additions)
        output_lines.append("")

    output_lines.append("# Check Commands")
    for i, (cmd, code, out) in enumerate(zip(commands, exit_codes, outputs)):
        output_lines.append(f"## Command {i+1}: {cmd}")
        output_lines.append(f"Exit code: {code}")
        output_lines.append("Output:")
        output_lines.append("```")
        output_lines.append(out[-2000:] if out else "(no output)")
        output_lines.append("```")
        output_lines.append("")

    return {
        "phase": phase,
        "status": status,
        "detail": f"Gate {status}: {len(checks)} checks, protected paths: {protected_path_verdict}",
        "commands": commands,
        "exit_codes": exit_codes,
        "protected_paths": protected_paths,
        "protected_path_verdict": protected_path_verdict,
        "protected_path_findings": protected_path_findings,
        "observed_additions": observed_additions,
        "gate_verdict": gate_verdict,
        "basis": basis_str,
        "output": "\n".join(output_lines)
    }


def validate_builder_report(report_path, required_literals=None, source="station"):
    """Deterministic artifact validation for the builder report (station artifact contract S2).

    Runs in the pre-review checks gate, after the builder and before any
    reviewer is spawned. The report must exist and be non-empty, and every
    literal the work order declares in required_literals must appear in it
    in full: exact substring containment, no abbreviation, ellipsis or case
    folding. With no declared literals only existence and non-emptiness are
    checked, so work orders that declare nothing behave as before.

    source says who wrote the report: "station" when the station wrote the
    artifact itself, "transcript" when the runner saved captured channel
    output because the station wrote nothing. When literals are declared a
    transcript is never accepted as the report.

    Returns {"passed": bool, "findings": [str], "log": str, "report": str,
    "required_literals": [str], "missing_literals": [str], "observed": str}.
    """
    path = Path(report_path)
    literals = [lit for lit in (required_literals or []) if isinstance(lit, str) and lit]
    findings = []
    missing = []
    observed = "present"
    text = None
    if not path.is_file():
        observed = "missing"
        findings.append(f"Builder report artifact {path} is missing.")
    else:
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            observed = "unreadable"
            findings.append(f"Builder report artifact {path} could not be read: {exc}.")
        else:
            if not text.strip():
                observed = "empty"
                findings.append(f"Builder report artifact {path} is empty.")
    if text is not None and text.strip():
        if literals and source != "station":
            observed = "transcript_only"
            findings.append(f"Builder report artifact {path} was not written by the station; captured "
                            f"channel output is never accepted as the report when literals are required.")
        for lit in literals:
            if lit not in text:
                missing.append(lit)
                findings.append(f"Required literal not found in full in the builder report: {lit}")
    elif literals:
        missing = list(literals)
        for lit in literals:
            findings.append(f"Required literal not found in full in the builder report: {lit}")
    passed = not findings
    lines = ["## Artifact validation", "",
             f"- builder report: {path}",
             f"- observed: {observed}",
             f"- report source: {source}",
             f"- required literals declared: {len(literals)}"]
    for lit in literals:
        lines.append(f"  - {'present' if (lit not in missing) else 'MISSING'}: {lit}")
    lines.append(f"- result: {'pass' if passed else 'fail'}")
    for finding in findings:
        lines.append(f"- finding: {finding}")
    return {"passed": passed, "findings": findings, "log": "\n".join(lines) + "\n",
            "report": str(path), "required_literals": literals,
            "missing_literals": missing, "observed": observed}


def review_artifact_state(review_path):
    """Observed state of a reviewer's review artifact: (state, text).

    state is one of missing, unreadable, empty, present. Parsing against the
    review contract stays with runner.parse_review; this only reports what
    is on disk so a failure can name it.
    """
    path = Path(review_path)
    if not path.is_file():
        return "missing", None
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return "unreadable", None
    if not text.strip():
        return "empty", text
    return "present", text
