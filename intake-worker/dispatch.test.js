// autonomous-line S7: the intake worker forwards work orders to the line.
import test from "node:test";
import assert from "node:assert/strict";
import { createHmac } from "node:crypto";
import worker from "./worker.js";

const SECRET = "test-webhook-secret";
const GH = { GITHUB_REPO: "acme/project", GITHUB_TOKEN: "t0ken" };

function signed(event, payload) {
  const raw = JSON.stringify(payload);
  const sig = "sha256=" + createHmac("sha256", SECRET).update(raw).digest("hex");
  return new Request("https://example.test/github", {
    method: "POST", body: raw,
    headers: { "x-github-event": event, "x-hub-signature-256": sig, "content-type": "application/json" },
  });
}

function issue(labels) {
  return { number: 42, title: "Add export", body: "Please add CSV export", html_url: "https://github.com/acme/project/issues/42",
    labels: labels.map((name) => ({ name })) };
}

async function withFetch(status, fn) {
  const calls = [];
  const original = globalThis.fetch;
  globalThis.fetch = async (url, init) => { calls.push({ url, init }); return new Response(null, { status }); };
  try { await fn(calls); } finally { globalThis.fetch = original; }
}

test("S7 a signed issue labeled anvil is dispatched to the line as wo-gh-<number>", async () => {
  await withFetch(204, async (calls) => {
    const payload = { action: "labeled", label: { name: "anvil" }, issue: issue(["anvil", "feature", "risk:auth"]) };
    const res = await worker.fetch(signed("issues", payload), { GITHUB_WEBHOOK_SECRET: SECRET, ...GH });
    assert.equal(res.status, 202);
    const body = await res.json();
    assert.equal(body.id, "wo-gh-42");
    assert.equal(body.kind, "feature");
    assert.deepEqual(body.risk_hints, ["auth"]);
    assert.deepEqual(body.dispatch, { dispatched: true, status: 204 });
    assert.equal(calls.length, 1);
    assert.equal(calls[0].url, "https://api.github.com/repos/acme/project/dispatches");
    assert.equal(calls[0].init.headers.Authorization, "Bearer t0ken");
    const sent = JSON.parse(calls[0].init.body);
    assert.equal(sent.event_type, "anvil-work-order");
    assert.equal(sent.client_payload.work_order.id, "wo-gh-42");
  });
});

test("S7 an opened issue without the anvil label is mapped but never dispatched", async () => {
  await withFetch(204, async (calls) => {
    const res = await worker.fetch(signed("issues", { action: "opened", issue: issue(["bug"]) }),
      { GITHUB_WEBHOOK_SECRET: SECRET, ...GH });
    const body = await res.json();
    assert.equal(body.dispatch.dispatched, false);
    assert.equal(body.dispatch.reason, "not_labeled_anvil");
    assert.equal(calls.length, 0);
  });
});

test("S7 an unsigned deployment never dispatches, even for the anvil label", async () => {
  await withFetch(204, async (calls) => {
    const raw = JSON.stringify({ action: "labeled", label: { name: "anvil" }, issue: issue(["anvil"]) });
    const req = new Request("https://example.test/github", { method: "POST", body: raw, headers: { "x-github-event": "issues" } });
    const body = await (await worker.fetch(req, GH)).json();
    assert.equal(body.dispatch.reason, "unsigned_delivery");
    assert.equal(calls.length, 0);
  });
});

test("S7 POST /work-orders dispatches only with the intake token", async () => {
  const make = (headers = {}) => new Request("https://example.test/work-orders", {
    method: "POST", body: JSON.stringify({ kind: "task", title: "Do it" }), headers });
  await withFetch(204, async (calls) => {
    const open = await (await worker.fetch(make(), GH)).json();
    assert.equal(open.dispatch.reason, "intake_token_required");
    assert.equal(calls.length, 0);
    const denied = await worker.fetch(make({ authorization: "Bearer wrong" }), { ...GH, INTAKE_TOKEN: "s3cret" });
    assert.equal(denied.status, 401);
    assert.equal(calls.length, 0);
    const ok = await worker.fetch(make({ authorization: "Bearer s3cret" }), { ...GH, INTAKE_TOKEN: "s3cret" });
    assert.equal(ok.status, 201);
    assert.equal((await ok.json()).dispatch.dispatched, true);
    assert.equal(calls.length, 1);
  });
});

test("S7 a refused or failing dispatch is reported, and intake still answers", async () => {
  await withFetch(403, async () => {
    const payload = { action: "labeled", label: { name: "anvil" }, issue: issue(["anvil"]) };
    const res = await worker.fetch(signed("issues", payload), { GITHUB_WEBHOOK_SECRET: SECRET, ...GH });
    assert.equal(res.status, 202);
    assert.deepEqual((await res.json()).dispatch, { dispatched: false, status: 403, reason: "github_refused" });
  });
  const res = await worker.fetch(signed("issues", { action: "labeled", label: { name: "anvil" }, issue: issue(["anvil"]) }),
    { GITHUB_WEBHOOK_SECRET: SECRET, GITHUB_REPO: "not a repo", GITHUB_TOKEN: "x" });
  assert.equal((await res.json()).dispatch.reason, "invalid_repo");
});
