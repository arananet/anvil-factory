from .gates import human_gate

def aggregate(reviews):
    verdicts = [r.verdict if hasattr(r, "verdict") else r.get("verdict") for r in reviews]
    if "fail" in verdicts:
        return "rejected"
    if "changes_requested" in verdicts:
        return "changes_requested"
    if verdicts and all(v == "pass" for v in verdicts):
        return "approved"
    return "changes_requested"

# alias
aggregate_reviews = aggregate

def needs_human(work_order, approver_verdict):
    if approver_verdict != "approved":
        return True
    return human_gate(work_order) == "required"
