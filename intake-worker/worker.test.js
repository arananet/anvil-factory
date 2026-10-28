import test from "node:test";
import assert from "node:assert/strict";
import { createHmac } from "node:crypto";
import worker from "./worker.js";

test("health returns ok", async () => {
  const res = await worker.fetch(new Request("https://example.test/health"));
  assert.equal(res.status, 200);
  assert.deepEqual(await res.json(), { ok: true });
});

test("create work order returns 201 and normalized shape", async () => {
  const req = new Request("https://example.test/work-orders", {
    method: "POST", headers: { "content-type": "application/json" },
    body: JSON.stringify({ kind: "feature", title: "Add export" }),
  });
  const res = await worker.fetch(req);
  assert.equal(res.status, 201);
  const body = await res.json();
  assert.match(body.id, /^wo-/);
  assert.equal(body.kind, "feature");
  assert.deepEqual(body.risk_hints, []);
  assert.equal(body.status, "new");
});

test("invalid body returns 400", async () => {
  const req = new Request("https://example.test/work-orders", {
    method: "POST", headers: { "content-type": "application/json" },
    body: JSON.stringify({ kind: "feature" }),
  });
  const res = await worker.fetch(req);
  assert.equal(res.status, 400);
});

test("unknown route returns 404", async () => {
  const res = await worker.fetch(new Request("https://example.test/nope"));
  assert.equal(res.status, 404);
});

const WEBHOOK_SECRET = "test-secret-for-node-tests";

function signedRequest(event, payload, secret = WEBHOOK_SECRET) {
  const raw = JSON.stringify(payload);
  const sig = "sha256=" + createHmac("sha256", secret).update(raw).digest("hex");
  return new Request("https://example.test/github", {
    method: "POST",
    headers: { "content-type": "application/json", "x-github-event": event, "x-hub-signature-256": sig },
    body: raw,
  });
}

const ISSUE_OPENED = {
  action: "opened",
  issue: {
    title: "Crash on empty title",
    body: "Steps to reproduce the crash.",
    html_url: "https://github.com/arananet/anvil-example-taskline/issues/7",
    labels: [{ name: "bug" }],
  },
};

test("github issues.opened with a valid signature maps to a work order", async () => {
  const res = await worker.fetch(signedRequest("issues", ISSUE_OPENED), { GITHUB_WEBHOOK_SECRET: WEBHOOK_SECRET });
  assert.equal(res.status, 202);
  const body = await res.json();
  assert.equal(body.kind, "bug");
  assert.equal(body.title, "Crash on empty title");
  assert.equal(body.source, "github-issue");
  assert.match(body.description, /GitHub issue: https:\/\/github\.com\/arananet\/anvil-example-taskline\/issues\/7/);
});

test("github issues.opened with an invalid signature returns 401", async () => {
  const req = signedRequest("issues", ISSUE_OPENED, "the-wrong-secret");
  const res = await worker.fetch(req, { GITHUB_WEBHOOK_SECRET: WEBHOOK_SECRET });
  assert.equal(res.status, 401);
});

test("github issue labeled task maps to kind task", async () => {
  const payload = {
    action: "opened",
    issue: { title: "Write docs", body: "", html_url: "https://github.com/x/y/issues/1", labels: [{ name: "task" }] },
  };
  const res = await worker.fetch(signedRequest("issues", payload), { GITHUB_WEBHOOK_SECRET: WEBHOOK_SECRET });
  assert.equal(res.status, 202);
  assert.equal((await res.json()).kind, "task");
});

test("github issue labeled anvil maps, other labels are ignored", async () => {
  const labeled = { action: "labeled", label: { name: "anvil" }, issue: ISSUE_OPENED.issue };
  const res = await worker.fetch(signedRequest("issues", labeled), { GITHUB_WEBHOOK_SECRET: WEBHOOK_SECRET });
  assert.equal(res.status, 202);
  assert.equal((await res.json()).source, "github-issue");
  const other = { action: "labeled", label: { name: "wontfix" }, issue: ISSUE_OPENED.issue };
  const res2 = await worker.fetch(signedRequest("issues", other), { GITHUB_WEBHOOK_SECRET: WEBHOOK_SECRET });
  assert.equal(res2.status, 202);
  assert.equal((await res2.json()).ignored, true);
});

test("github ping event is ignored with 202", async () => {
  const res = await worker.fetch(signedRequest("ping", { zen: "ok" }), { GITHUB_WEBHOOK_SECRET: WEBHOOK_SECRET });
  assert.equal(res.status, 202);
  assert.deepEqual(await res.json(), { ok: true, ignored: true });
});
