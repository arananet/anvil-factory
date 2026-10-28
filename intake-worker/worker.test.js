import test from "node:test";
import assert from "node:assert/strict";
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
