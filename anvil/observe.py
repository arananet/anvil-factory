"""Operational observability for a run (spec: governed-delivery).

A run report is written once, at the end. This module is what exists while
the run is still going, and what leaves the project:

- state.json: the run's current state, rewritten atomically after every
  station, so a run in progress or one that died halfway can be seen.
- events.jsonl: one structured event per station, loopback and run
  boundary. Scalar facts only (ids, status, model, tokens, cost, verdict):
  no prompts, no station output, no paths.
- Export, both optional and configured in anvil.yaml under observability:
  each event POSTed to a webhook, and the finished run sent as one
  OpenTelemetry trace (OTLP/HTTP JSON) with a span per station.

Export never decides a run: a failed POST is recorded in state.json and the
line goes on. Standard library only.
"""

import hashlib
import json
import os
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from .telemetry import normalize_usage, summarize_steps

STATE_FILE = "state.json"
EVENTS_FILE = "events.jsonl"
STALE_AFTER_SECONDS = 3 * 3600


def _now():
    return datetime.now(timezone.utc)


def observability_config(config):
    value = (config or {}).get("observability") if isinstance(config, dict) else None
    return value if isinstance(value, dict) else {}


def _headers_from_env(name):
    """Headers from an environment variable shaped "name=value,name2=value2"."""
    headers = {}
    for pair in os.environ.get(name or "", "").split(","):
        key, sep, value = pair.partition("=")
        if sep and key.strip():
            headers[key.strip()] = value.strip()
    return headers


def _post(url, payload, headers, timeout):
    if not str(url).lower().startswith(("https://", "http://")):
        raise ValueError("export url must be http or https")
    request = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), method="POST")
    request.add_header("Content-Type", "application/json")
    for key, value in headers.items():
        request.add_header(key, value)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        response.read()


def step_event(step):
    """The scalar facts of one step, as they go into an event."""
    event = {key: step[key] for key in ("station", "status", "attempt", "configured_model", "executed_model",
                                        "duration_ms", "cost", "gate_verdict", "phase", "return_to", "url")
             if step.get(key) is not None}
    usage = normalize_usage(step.get("usage"))
    if usage is not None:
        event["usage"] = usage
    return event


class RunRecorder:
    """Writes state.json and events.jsonl for one run and exports them."""

    def __init__(self, run_dir, run_id, work_order_id, project, pipeline, config=None):
        self.run_dir = Path(run_dir)
        self.base = {"run_id": run_id, "work_order_id": work_order_id, "project": project, "pipeline": pipeline}
        self.config = observability_config(config)
        self.timeout = float(self.config.get("timeout_seconds", 5))
        self.started_at = _now()
        self.emitted = 0
        self.export_errors = []
        self.spans = []

    # events -----------------------------------------------------------
    def event(self, kind, **fields):
        record = {"schema": "anvil/event@1", "ts": _now().isoformat(), "event": kind, **self.base, **fields}
        with open(self.run_dir / EVENTS_FILE, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
        url = self.config.get("events_url")
        if url:
            headers = {}
            token = os.environ.get(str(self.config.get("events_token_env") or ""), "")
            if token:
                headers["Authorization"] = f"Bearer {token}"
            try:
                _post(url, record, headers, self.timeout)
            except Exception as exc:  # export never decides a run
                self._export_failed("events", exc)
        return record

    def _export_failed(self, channel, exc):
        note = f"{channel}: {type(exc).__name__}"
        if note not in self.export_errors:
            self.export_errors.append(note)

    # state ------------------------------------------------------------
    def state(self, state, steps, current_station=None, verdict="", loopbacks=0, **extra):
        usage = summarize_steps(steps)
        costs = [s.get("cost") for s in steps if isinstance(s.get("cost"), (int, float))]
        record = {"schema": "anvil/run-state@1", **self.base, "state": state,
                  "current_station": current_station, "verdict": verdict or None, "loopbacks": loopbacks,
                  "started_at": self.started_at.isoformat(), "updated_at": _now().isoformat(),
                  "steps": [{key: s[key] for key in ("station", "status", "attempt") if s.get(key) is not None}
                            for s in steps],
                  "token_usage": {key: usage.get(key) for key in ("calls", "total_tokens", "measured_calls",
                                                                   "unmeasured_calls")},
                  "cost": round(sum(costs), 6) if costs else None,
                  "export_errors": list(self.export_errors), **extra}
        tmp = self.run_dir / (STATE_FILE + ".tmp")
        tmp.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp, self.run_dir / STATE_FILE)
        return record

    def flush(self, steps, current_station=None, verdict="", loopbacks=0):
        """Emit an event for every step not yet emitted and rewrite the state."""
        for step in steps[self.emitted:]:
            kind = "loopback" if step.get("status") == "loopback" else "station.finished"
            record = self.event(kind, **step_event(step))
            self.spans.append((record, step))
        self.emitted = len(steps)
        self.state("running", steps, current_station=current_station, verdict=verdict, loopbacks=loopbacks)

    def finish(self, steps, report):
        self.flush(steps, verdict=report.get("verdict"), loopbacks=report.get("loopbacks", 0))
        usage = summarize_steps(steps)
        costs = [s.get("cost") for s in steps if isinstance(s.get("cost"), (int, float))]
        self.event("run.finished", verdict=report.get("verdict"), human_required=report.get("human_required"),
                   loopbacks=report.get("loopbacks", 0), deployment_status=report.get("deployment_status"),
                   calls=usage.get("calls"), total_tokens=usage.get("total_tokens"),
                   cost=round(sum(costs), 6) if costs else None)
        self._export_trace(report)
        self.state("finished", steps, verdict=report.get("verdict"), loopbacks=report.get("loopbacks", 0),
                   human_required=report.get("human_required"),
                   deployment_status=report.get("deployment_status"))

    # OpenTelemetry ----------------------------------------------------
    def trace_payload(self, report):
        """The run as one OTLP/HTTP JSON trace: a root span and one per step."""
        trace_id = hashlib.sha256(str(self.base["run_id"]).encode()).hexdigest()[:32]
        root_id = hashlib.sha256(f"{trace_id}:root".encode()).hexdigest()[:16]
        end = _now()

        def attrs(values):
            out = []
            for key, value in values.items():
                if value is None:
                    continue
                if isinstance(value, bool):
                    out.append({"key": key, "value": {"boolValue": value}})
                elif isinstance(value, int):
                    out.append({"key": key, "value": {"intValue": str(value)}})
                elif isinstance(value, float):
                    out.append({"key": key, "value": {"doubleValue": value}})
                else:
                    out.append({"key": key, "value": {"stringValue": str(value)}})
            return out

        def nanos(moment):
            return str(int(moment.timestamp() * 1_000_000_000))

        ok = report.get("verdict") in {"approved", "packet_ready"}
        spans = [{"traceId": trace_id, "spanId": root_id, "name": f"anvil.run {self.base['pipeline']}", "kind": 1,
                  "startTimeUnixNano": nanos(self.started_at), "endTimeUnixNano": nanos(end),
                  "attributes": attrs({"anvil.run_id": self.base["run_id"],
                                       "anvil.work_order_id": self.base["work_order_id"],
                                       "anvil.project": self.base["project"],
                                       "anvil.pipeline": self.base["pipeline"],
                                       "anvil.verdict": report.get("verdict"),
                                       "anvil.human_required": report.get("human_required"),
                                       "anvil.loopbacks": report.get("loopbacks", 0),
                                       "anvil.deployment_status": report.get("deployment_status")}),
                  "status": {"code": 1 if ok else 2}}]
        for index, (record, step) in enumerate(self.spans):
            finished = datetime.fromisoformat(record["ts"])
            duration = float(step.get("duration_ms") or 0) / 1000.0
            started = datetime.fromtimestamp(finished.timestamp() - duration, timezone.utc)
            usage = normalize_usage(step.get("usage")) or {}
            spans.append({
                "traceId": trace_id, "parentSpanId": root_id,
                "spanId": hashlib.sha256(f"{trace_id}:{index}".encode()).hexdigest()[:16],
                "name": f"anvil.station {step.get('station')}", "kind": 1,
                "startTimeUnixNano": nanos(started), "endTimeUnixNano": nanos(finished),
                "attributes": attrs({"anvil.station": step.get("station"), "anvil.status": step.get("status"),
                                     "anvil.attempt": step.get("attempt", 1),
                                     "gen_ai.request.model": step.get("configured_model"),
                                     "gen_ai.response.model": step.get("executed_model"),
                                     "gen_ai.usage.input_tokens": usage.get("input_tokens"),
                                     "gen_ai.usage.output_tokens": usage.get("output_tokens"),
                                     "anvil.total_tokens": usage.get("total_tokens"),
                                     "anvil.cost_usd": step.get("cost")}),
                "status": {"code": 2 if step.get("status") == "failed" else 1}})
        return {"resourceSpans": [{
            "resource": {"attributes": attrs({"service.name": "anvil", "anvil.project": self.base["project"]})},
            "scopeSpans": [{"scope": {"name": "anvil.runner"}, "spans": spans}]}]}

    def _export_trace(self, report):
        endpoint = self.config.get("otlp_endpoint")
        if not endpoint:
            return
        try:
            _post(endpoint, self.trace_payload(report),
                  _headers_from_env(self.config.get("otlp_headers_env")), self.timeout)
        except Exception as exc:
            self._export_failed("otlp", exc)


def mark_crashed(run_dir, error):
    """Turn a state left running by a raised exception into crashed."""
    path = Path(run_dir) / STATE_FILE
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if record.get("state") != "running":
        return None
    record.update({"state": "crashed", "error": f"{type(error).__name__}: {str(error)[:300]}",
                   "updated_at": _now().isoformat()})
    path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    event = {"schema": "anvil/event@1", "ts": record["updated_at"], "event": "run.crashed",
             **{key: record.get(key) for key in ("run_id", "work_order_id", "project", "pipeline")},
             "station": record.get("current_station"), "error": type(error).__name__}
    with open(Path(run_dir) / EVENTS_FILE, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")
    return record


def run_states(project, now=None):
    """Every run state under a project, newest first.

    A run still marked running whose state has not moved for
    STALE_AFTER_SECONDS is reported as stalled: the process was killed
    without a chance to say so.
    """
    now = now or _now()
    states = []
    runs_dir = Path(project) / "runs"
    if not runs_dir.is_dir():
        return states
    for folder in sorted(p for p in runs_dir.iterdir() if p.is_dir()):
        try:
            record = json.loads((folder / STATE_FILE).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(record, dict) or record.get("schema") != "anvil/run-state@1":
            continue
        if record.get("state") == "running":
            try:
                age = (now - datetime.fromisoformat(record["updated_at"])).total_seconds()
            except (KeyError, ValueError, TypeError):
                age = 0
            if age > STALE_AFTER_SECONDS:
                record = dict(record, state="stalled")
        states.append(record)
    states.sort(key=lambda r: str(r.get("updated_at", "")), reverse=True)
    return states


def fleet_summary(project):
    """Aggregate facts across a project's runs, from reports and states."""
    from .statuspage import collect_runs
    reports, _ = collect_runs(project, include_history=True)
    current = [r for r in reports if not r.get("_archived")]
    by_pipeline, rejections = {}, {}
    for report in current:
        group = by_pipeline.setdefault(str(report.get("pipeline")), {"runs": 0, "approved": 0, "loopbacks": 0})
        group["runs"] += 1
        group["approved"] += report.get("verdict") == "approved"
        group["loopbacks"] += int(report.get("loopbacks") or 0)
        for review in ((report.get("decision") or {}).get("approver") or {}).get("reviews_counted") or []:
            if review.get("verdict") != "pass":
                rejections[review.get("station")] = rejections.get(review.get("station"), 0) + 1
    for group in by_pipeline.values():
        group["approval_rate"] = round(group["approved"] / group["runs"], 3) if group["runs"] else None
    usage = summarize_steps([step for report in reports for step in report.get("steps") or []])
    costs = [step.get("cost") for report in reports for step in report.get("steps") or []
             if isinstance(step.get("cost"), (int, float))]
    states = run_states(project)
    return {"runs": len(current), "archived_runs": len(reports) - len(current), "by_pipeline": by_pipeline,
            "reviews_not_passed_by_station": rejections,
            "in_progress": [s["work_order_id"] for s in states if s["state"] == "running"],
            "interrupted": [{"work_order_id": s["work_order_id"], "state": s["state"],
                             "station": s.get("current_station")} for s in states
                            if s["state"] in {"crashed", "stalled"}],
            "token_usage": {key: usage.get(key) for key in ("calls", "total_tokens", "measured_calls",
                                                             "unmeasured_calls")},
            "cost": round(sum(costs), 6) if costs else None}
