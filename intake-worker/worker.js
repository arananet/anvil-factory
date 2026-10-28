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

function issueToWorkOrder(issue) {
  const labels = Array.isArray(issue.labels)
    ? issue.labels.map((l) => (typeof l === "string" ? l : l && l.name)).filter(Boolean)
    : [];
  const description = [issue.body || "", "", `GitHub issue: ${issue.html_url || ""}`].join("\n").trim();
  return normalize({
    kind: labels.includes("task") ? "task" : "bug",
    title: issue.title || "GitHub issue",
    source: "github-issue",
    description,
  });
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
      const wo = normalize(body);
      // Optional GitHub dispatch: if env.GITHUB_REPO and env.GITHUB_TOKEN are set,
      // a deployment can forward the work order to a repository dispatch event.
      // No secrets live in this file; both values come from the Worker environment.
      return Response.json(wo, { status: 201 });
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
      return Response.json(issueToWorkOrder(payload.issue), { status: 202 });
    }
    return Response.json({ error: "Not found" }, { status: 404 });
  },
};
