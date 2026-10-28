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

export default {
  async fetch(request, env) {
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
    return Response.json({ error: "Not found" }, { status: 404 });
  },
};
