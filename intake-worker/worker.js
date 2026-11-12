// ANVIL intake worker. Plain JavaScript, no dependencies.
function normalize(body) {
  const now = Date.now();
  return {
    id: body.id || "wo-" + now.toString(36),
    kind: body.kind,
    title: body.title,
    source: body.source || "intake-worker",
    description: body.description || "",
    risk_hints: Array.isArray(body.risk_hints) ? body.risk_hints : [],
    status: "new",
  };
}

function hexToBytes(hex) {
  const bytes = new Uint8Array(hex.length / 2);
  for (let i = 0; i < bytes.length; i++) {
    bytes[i] = parseInt(hex.substr(i * 2, 2), 16);
  }
  return bytes;
}

function constantTimeEqual(a, b) {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a[i] ^ b[i];
  return diff === 0;
}

async function validSignature(secret, rawBody, signatureHeader) {
  if (!signatureHeader || !signatureHeader.startsWith("sha256=")) return false;
  const expectedHex = signatureHeader.slice("sha256=".length).trim().toLowerCase();
  if (!/^[0-9a-f]{64}$/.test(expectedHex)) return false;
  const key = await crypto.subtle.importKey(
    "raw", new TextEncoder().encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const mac = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(rawBody));
  return constantTimeEqual(new Uint8Array(mac), hexToBytes(expectedHex));
}

const KINDS = ["idea", "feature", "bug", "incident", "task", "content"];
const RISK_HINTS = ["auth", "payments", "data-deletion", "production-deploy", "secrets", "publishing"];

// Same mapping as anvil/line.py work_order_from_issue: labels carry the kind
// (first match, default feature) and the risk hints (bare or risk:<hint>).
function issueToWorkOrder(issue) {
  const labels = Array.isArray(issue.labels)
    ? issue.labels.map((l) => (typeof l === "string" ? l : l && l.name)).filter(Boolean)
        .map((l) => String(l).trim().toLowerCase())
    : [];
  const description = [issue.body || "", "", `GitHub issue: ${issue.html_url || ""}`].join("\n").trim();
  const hints = [];
  for (const label of labels) {
    const hint = label.startsWith("risk:") ? label.slice(5) : label;
    if (RISK_HINTS.includes(hint) && !hints.includes(hint)) hints.push(hint);
  }
  const body = {
    kind: labels.find((l) => KINDS.includes(l)) || "feature",
    title: issue.title || "GitHub issue",
    source: "github-issue",
    description,
    risk_hints: hints,
  };
  if (Number.isInteger(issue.number)) body.id = `wo-gh-${issue.number}`;
  return normalize(body);
}

// Forward a work order to the line: a repository_dispatch event of type
// anvil-work-order on env.GITHUB_REPO, which the anvil-line workflow runs.
// Both values come from the Worker environment; no secret lives in this file.
// Returns {dispatched, status?, reason?} and never throws: intake still
// answers with the normalized work order when the forward fails.
async function dispatch(env, workOrder) {
  if (!env.GITHUB_REPO || !env.GITHUB_TOKEN) {
    return { dispatched: false, reason: "not_configured" };
  }
  if (!/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/.test(env.GITHUB_REPO)) {
    return { dispatched: false, reason: "invalid_repo" };
  }
  try {
    const response = await fetch(`https://api.github.com/repos/${env.GITHUB_REPO}/dispatches`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${env.GITHUB_TOKEN}`,
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
        "User-Agent": "anvil-intake-worker",
        "X-GitHub-Api-Version": "2022-11-28",
      },
      body: JSON.stringify({ event_type: "anvil-work-order", client_payload: { work_order: workOrder } }),
    });
    if (response.status === 204) return { dispatched: true, status: 204 };
    return { dispatched: false, status: response.status, reason: "github_refused" };
  } catch {
    return { dispatched: false, reason: "network_error" };
  }
}

export default {
  async fetch(request, env) {
    env = env || {};
    const url = new URL(request.url);
    if (request.method === "GET" && url.pathname === "/health") {
      return Response.json({ ok: true });
    }
    if (request.method === "POST" && url.pathname === "/work-orders") {
      let body;
      try { body = await request.json(); } catch {
        return Response.json({ error: "Invalid JSON body" }, { status: 400 });
      }
      if (!body || !body.kind || !body.title) {
        return Response.json({ error: "Body must include kind and title" }, { status: 400 });
      }
      // With an intake token configured, only its holder can file work orders.
      if (env.INTAKE_TOKEN) {
        const given = new TextEncoder().encode(request.headers.get("authorization") || "");
        const expected = new TextEncoder().encode(`Bearer ${env.INTAKE_TOKEN}`);
        if (!constantTimeEqual(given, expected)) {
          return Response.json({ error: "Unauthorized" }, { status: 401 });
        }
      }
      const wo = normalize(body);
      // Forwarding to the line needs the intake token: an open endpoint
      // must never be able to start runs.
      const forwarded = env.INTAKE_TOKEN
        ? await dispatch(env, wo)
        : { dispatched: false, reason: "intake_token_required" };
      return Response.json({ ...wo, dispatch: forwarded }, { status: 201 });
    }
    if (request.method === "POST" && url.pathname === "/github") {
      const raw = await request.text();
      if (env.GITHUB_WEBHOOK_SECRET) {
        const ok = await validSignature(env.GITHUB_WEBHOOK_SECRET, raw, request.headers.get("x-hub-signature-256"));
        if (!ok) {
          return Response.json({ error: "Invalid signature" }, { status: 401 });
        }
      }
      let payload;
      try { payload = JSON.parse(raw); } catch {
        return Response.json({ error: "Invalid JSON body" }, { status: 400 });
      }
      const event = request.headers.get("x-github-event") || "";
      if (event !== "issues" || !payload || !payload.issue) {
        return Response.json({ ok: true, ignored: true }, { status: 202 });
      }
      const action = payload.action || "";
      const labelName = payload.label && payload.label.name;
      const shouldMap = action === "opened" || (action === "labeled" && labelName === "anvil");
      if (!shouldMap) {
        return Response.json({ ok: true, ignored: true }, { status: 202 });
      }
      const wo = issueToWorkOrder(payload.issue);
      // Only a verified delivery carrying the anvil label starts a run: the
      // label is applied by someone with triage rights, never by the author
      // of an arbitrary issue.
      const labeled = action === "labeled" && labelName === "anvil";
      const forwarded = env.GITHUB_WEBHOOK_SECRET && labeled
        ? await dispatch(env, wo)
        : { dispatched: false, reason: labeled ? "unsigned_delivery" : "not_labeled_anvil" };
      return Response.json({ ...wo, dispatch: forwarded }, { status: 202 });
    }
    return Response.json({ error: "Not found" }, { status: 404 });
  },
};
