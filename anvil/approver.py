# The human gate scans risk hints in this fixed order so the explanation
# sentences in run reports are stable run over run. RISK_HINTS in gates.py
# is the set being scanned; a test keeps the two in sync.
RISK_SCAN_ORDER = ["auth", "payments", "data-deletion", "production-deploy", "secrets", "publishing"]

def _station_verdicts(reviews):
    pairs = []
    for r in reviews:
        if hasattr(r, "verdict"):
            pairs.append((r.station, r.verdict))
        else:
            pairs.append((r.get("station"), r.get("verdict")))
    return pairs

def _counted_explained(counted):
    """The pre-contract aggregation over the counted reviews only."""
    failing = [c["station"] for c in counted if c["verdict"] == "fail"]
    if failing:
        if len(failing) == 1:
            return "rejected", f"Reviewer {failing[0]} returned fail."
        return "rejected", f"Reviewers {', '.join(failing)} returned fail."
    asking = [c["station"] for c in counted if c["verdict"] == "changes_requested"]
    if asking:
        if len(asking) == 1:
            return "changes_requested", f"Reviewer {asking[0]} requested changes."
        return "changes_requested", f"Reviewers {', '.join(asking)} requested changes."
    verdicts = [c["verdict"] for c in counted]
    if verdicts and all(v == "pass" for v in verdicts):
        return "approved", "All counted reviews passed."
    return "changes_requested", "The counted reviews did not all pass, so the verdict is changes_requested."


def uncounted_stations(counted, expected, uncounted=None):
    """Expected stations with no counted review, in expected order, with a reason each."""
    reasons = dict(uncounted or {})
    have = {c["station"] for c in counted}
    missing = []
    for station in expected or []:
        if station in have or any(station == m for m, _ in missing):
            continue
        missing.append((station, reasons.get(station) or "no countable review artifact was produced"))
    return missing


def aggregate_explained(reviews, expected=None, uncounted=None):
    """Aggregate a run's reviews into (verdict, rule, counted).

    counted is the list of {"station": ..., "verdict": ...} that fed the
    aggregation, and rule is one plain sentence naming the branch that
    produced the verdict. The runner stores all three in the run report's
    decision object, so the explanation is generated from the same values
    the code acted on, at the moment the decision is made.

    Approver honesty (station artifact contract S3): when expected names
    stations the pipeline expected a review from, any of them missing from
    the counted set blocks a silent approved. A verdict that would have been
    approved becomes human_required; a rejected or changes_requested verdict
    stands. Either way the rule names each uncounted station and the reason
    it was not counted (taken from uncounted, a station to reason mapping).
    With every expected station counted, the result is exactly as before.
    """
    counted = [{"station": s, "verdict": v} for s, v in _station_verdicts(reviews)]
    verdict, rule = _counted_explained(counted)
    missing = uncounted_stations(counted, expected, uncounted)
    if not missing:
        return verdict, rule, counted
    names = ", ".join(f"{s} ({why})" for s, why in missing)
    noun = "reviewer was" if len(missing) == 1 else "reviewers were"
    honesty = f"Expected {noun} not counted: {names}."
    if verdict == "approved":
        verdict = "human_required"
        return verdict, (f"{honesty} The counted reviews passed, but a verdict is never approved "
                         f"while an expected reviewer is uncounted, so the verdict is human_required."), counted
    return verdict, f"{honesty} {rule}", counted

def aggregate(reviews):
    return aggregate_explained(reviews)[0]

# alias
aggregate_reviews = aggregate

def matched_risk_hints(work_order):
    """The work order's risk hints that the human gate scans for, in scan order."""
    if isinstance(work_order, dict):
        hints = set(work_order.get("risk_hints", []) or [])
    else:
        hints = set(getattr(work_order, "risk_hints", []) or [])
    return [h for h in RISK_SCAN_ORDER if h in hints]

def needs_human_explained(work_order, approver_verdict):
    """Return (required, rule, hints_matched) for the human gate.

    The rule sentence names the branch taken: a verdict that is not
    approved always requires a human; an approved verdict requires one
    only when a scanned risk hint matched.
    """
    if approver_verdict != "approved":
        return True, f"Verdict is {approver_verdict}, not approved, so a human is required.", []
    matched = matched_risk_hints(work_order)
    if matched:
        quoted = ", ".join(f"'{h}'" for h in matched)
        noun = "risk hint" if len(matched) == 1 else "risk hints"
        return True, f"Verdict approved, but the work order carries the {noun} {quoted}, so a human is required.", matched
    scanned = ", ".join(RISK_SCAN_ORDER)
    return False, f"Verdict approved and no risk hints matched (scanned: {scanned}), so no human is required.", []

def needs_human(work_order, approver_verdict):
    return needs_human_explained(work_order, approver_verdict)[0]
