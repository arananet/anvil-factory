# Runtime Verification: a Feature Map and a Station That Uses the Built App

Status: draft (not filed)
Slug: runtime-verification

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose

ANVIL's rendered evidence is a still picture. anvil/capture.py serves the built project, opens one page and takes one screenshot per breakpoint (page.goto, page.screenshot); nothing clicks, types or plays. reviewer-ux is asked whether "the interface's primary task can be started, followed, and finished" and answers from source and stills. For the factory's typical deliverables (single page apps, games) that leaves the central question unanswered by evidence: does the thing work when a user uses it. Promoted practices P-5, P-8, P-9, P-10 and P-11 describe behavior that only shows at runtime and are enforced today as reviewer prose.

This order adds the missing layer: a feature map that names every user-facing feature in the user's terms, and a verification stage that drives the built app through that map and records evidence per feature, before any reviewer is dispatched. Reviewers then judge evidence of use, not only source and stills. The reference for the shape is the public create-verification-skill in pstack (cursor/plugins): launch, health check, drive behavior, capture evidence, clean up, guided by a feature map.

## Requirements

### R1. Feature map
- A project with a servable configuration carries a feature map at verification/feature-map.json: a list of features, each with id, name (the user's words), where (how a user finds it), steps (ordered driver actions) and expect (one or more observable conditions).
- The spec-writer station writes or updates the feature map for every work order that changes a UI surface; a feature the order adds or changes appears in the map in the same run.
- The map is validated in deterministic code at load: required fields, unique ids, steps drawn from the driver's verb set, at least one expect per feature. A malformed map stops the run before the builder with the file and entry named.

### R2. Driver
- The factory ships a driver module (anvil/drive.py) that reuses the capture module's server lifecycle (free port, start, wait, stop with process group cleanup) and exposes a closed verb set: open, click, press, type, wait_for, expect_text, expect_visible, expect_state (a named value read from the page), measure (bounding box of a selector), set_visibility (hidden, visible), snapshot.
- Each verb is recorded with its arguments, outcome and elapsed time. The driver never evaluates arbitrary page script supplied by a station; expect_state reads only names the project declares in the feature map.
- Playwright stays an optional dependency exactly as in capture: when it is missing the driver reports unavailable and the stage records that it did not verify, never a pass.

### R3. Verification stage
- A deterministic stage named verify runs after the checks gate and before the reviewer stage. It drives every feature in the map against the built project at each configured breakpoint and writes runs/<work-order-id>/verification.json: per feature and breakpoint, the verb trace, pass or fail per expect, and the evidence files (a snapshot after the last step at minimum).
- A feature whose expect fails returns to the builder as a gate loopback, naming the feature, the failing expect and the evidence path; zero reviewer stations are dispatched for that attempt. It consumes a loopback as a checks failure does and is bounded by max loopbacks.
- A project without a servable configuration, or a run where the driver is unavailable, records verification as not performed with the reason. That outcome is never counted as rendered or runtime evidence (practice P-3 semantics extended).

### R4. Reviewers judge the evidence
- reviewer-ux and reviewer-design packets gain a Runtime verification section: the feature list with pass or fail, and the evidence paths. reviewer-ux's first judgment area (user flows and task completion) cites the verification record when it exists and states plainly when it does not.
- The owner acceptance record links the verification record so the human gate can be exercised on the evidence of use.

### R5. Regression tests
- New test files under tests/, driven with a fake driver implementation in the way test_rendered_design_review drives a fake capture: (a) a map with a failing expect dispatches zero reviewers and returns the named feature as a loopback; (b) a passing map writes verification.json with one entry per feature and breakpoint and existing evidence files; (c) a malformed map stops the run before the builder naming the entry; (d) an unavailable driver records not performed and the run cannot pass on runtime evidence; (e) reviewer-ux and reviewer-design packets carry the section when the record exists and omit it when it does not.

### Guardrails
- Python standard library in the spine; Playwright optional and imported lazily, as in anvil/capture.py.
- Authorized change to a protected path, stated up front per practice P-15: pipelines/sdlc-default.json gains the verify stage between checks-gate and the reviewer parallel stage. No other pipeline file changes.
- Frozen: the checks gate's verdicts and loopback accounting; capture's existing screenshot behavior and evidence names; the review parse contract; cost-measurement semantics.
- Relationship to staged orders: completeness (wo-gh-42) judges that artifacts exist; preflight (wo-gh-28) judges that code is alive; this order judges that features work when used. Each holds whether or not the others have landed.
- Existing test files at the base ref are not modified or deleted. No em dash or en dash character in any produced file.
- Nothing in this order merges, publishes or deploys anything.

## Scenarios

- S1: Given a project whose feature map has a feature with a failing expect, when the verify stage runs, then the feature, the expect and the evidence path return to the builder as a gate loopback and zero reviewer stations are dispatched.
- S2: Given a project whose features all pass, when the verify stage runs, then verification.json holds one entry per feature and breakpoint, each with a verb trace and an existing evidence file, and the reviewer stage is dispatched.
- S3: Given a feature map with a duplicate id or an unknown verb, when the run starts, then it stops before the builder naming the file and the entry.
- S4: Given a run where the driver is unavailable, when the verify stage runs, then the record says verification was not performed and why, and no later record counts it as runtime evidence.
- S5: Given a verification record, when reviewer-ux and reviewer-design packets are built, then both carry the Runtime verification section; given none, then neither does and reviewer-ux is instructed to say it judged without it.
- S6: Given a work order that adds a UI feature, when the spec-writer finishes, then the feature map contains an entry for that feature.
