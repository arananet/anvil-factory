# Deterministic Preflight

Status: proposed
Slug: deterministic-preflight

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose

The checks gate (capability item 1, issue 6, merged) runs the project's own test suite before any model station executes, but it trusts that suite: it proves the tests pass, not that the tests touch the code under change, and not that the code under change is alive in the run path. Twice in this factory's own record the gap cost full priced rounds. In capability item 4 (issue 9, rendered design review), the builder delivered 23 tests that never imported the implementation they claimed to test; the gate passed them, and only the paid model reviewers caught the facade, two extra rounds later. In wo-gh-21 (issue 21), the builder implemented a function, unit tested it in isolation, and never called it in the run path; again only the reviewers caught it. The owner's standing expectation, stated 2026-11-04, is that the factory controls and includes the rules that prevent launching tests and reviews on something that does not even work. This order adds that mechanical proof of life to the gate itself, in deterministic code, before a single model station runs.

## Requirements

### R1. Import integrity
- For each new or changed test file in the run delta, static analysis of the file (Python ast, standard library only) collects the modules it imports. The file passes import integrity only if at least one imported module belongs to the change's implementation set (the new or changed non-test modules of the same delta, matched by module path, including package relative imports resolved against the file's package).
- A test file that imports none of the implementation set fails preflight, and the failure names the file. Test files that belong to pre-existing suites and are unchanged by the delta are not judged by this rule.

### R2. Execution proof
- The project's test suite runs under execution tracing (the standard library trace module or an equivalent standard library mechanism), in the same gate stage that runs the suite today.
- Every changed implementation module must show at least one executed line under the suite. Within those modules, every changed or new function or method must show at least one execution; a changed function or method with zero executions is a named preflight finding.
- A suite that exits green while executing none of the changed code fails preflight. The tracing evidence (per module and per function execution counts) is recorded in the run evidence.

### R3. Wiring reachability
- Every public function or class introduced by the delta (a new top level def or class whose name does not start with an underscore, in a new or changed non-test module) must be referenced from non-test code (an import plus a use, or a call or attribute reference in a non-test module of the tree) or from a declared entry point.
- Intentional public API surface is exempted by name: the work order may declare a public API list, and names on that list are not flagged. The exemption list is part of the run's recorded inputs.
- An introduced public function or class that is referenced only from test code, or from nowhere, is a named preflight finding.

### R4. Liveness smoke
- When the project configuration declares a smoke command, preflight runs it after the suite, inside the gate stage. A non-zero exit is a preflight failure recorded as a smoke failure, distinct from a suite failure.
- When no smoke command is declared, the smoke step records itself as not declared and does not fail preflight.

### R5. Placement, economics and reporting
- Preflight runs inside the existing checks gate stage, before any model station of the pipeline executes. The checks gate's protected path rules and its S4 base ref config resolution are unchanged in behavior; preflight consumes the same recorded base ref and delta the gate already computes.
- A preflight failure ends the run's forward progress for that round: the named findings return to the builder as a pre-review loopback (counted against the gate loopback budget like a checks failure), and no reviewer station is launched. The run spend up to that point is the deterministic gate cost only.
- The run report records the preflight outcome as its own field set (outcome, named findings per rule, tracing evidence reference), distinct from the checks result and from any review verdicts. A run whose preflight failed shows no review section for that round.

### R6. Regression fixtures
- The order's own tests encode the two historical failures as fixtures and run preflight against them: (a) the facade fixture, a delta whose test files pass while importing none of the implementation set (modelled on issue 9's 23 facade tests); (b) the unwired fixture, a delta whose new public function is implemented and unit tested but never referenced from non-test code (modelled on issue 21).
- Preflight must convict both fixtures with the right rule and the right names, and must pass a healthy control fixture whose tests import, execute and wire the changed code.
- The fixtures live in the factory's test suite as data, not as copies of the historical projects; they are minimal trees constructed by the tests.

### Guardrails
- Python standard library only, consistent with the factory spine. No new dependency.
- Frozen surfaces: the review parse contract and parse_review semantics, the canonical review contract wording, the reviewer prompts and their Output Format sections, the review producer mechanisms (scoped reviewer writes, no stdout transcription), and the checks gate's S4 base ref behavior. This order changes only what the gate verifies before the model stations, and how the run report records it.
- The rules apply to the factory's own line first: this order's execution runs preflight against the factory repo's own delta for this change, and its own fixtures and tests must pass the preflight it adds.
- No em dash or en dash character in any produced file (project style rule).

## Scenarios

### Scenario: Facade tests are convicted by import integrity before any review
- S1: Given a run delta whose changed test files import none of the delta's implementation modules (the R6 facade fixture), when preflight runs, then preflight fails, the failure names each offending test file under R1, and no reviewer station is launched for that round.

### Scenario: A green suite that never executes the changed code fails execution proof
- S2: Given a delta whose suite exits green while tracing shows a changed implementation module with zero executed lines, or a changed function with zero executions, when preflight evaluates the tracing evidence, then preflight fails and names the module or function under R2.

### Scenario: An implemented but unwired function is convicted by wiring
- S3: Given a delta introducing a public function referenced only from test code and not declared as public API (the R6 unwired fixture), when preflight runs, then preflight fails naming the function under R3, and no reviewer station is launched for that round.

### Scenario: Declared public API is exempt from wiring by name
- S4: Given a delta introducing a public function listed in the work order's declared public API list and referenced from nowhere else, when preflight runs, then the function is not flagged under R3 and the exemption is visible in the run evidence.

### Scenario: A failing declared smoke command fails preflight as a smoke failure
- S5: Given a project declaring a smoke command that exits non-zero, when preflight runs it, then preflight fails with the outcome recorded as a smoke failure under R4, distinct from a suite failure.

### Scenario: A healthy delta passes preflight and the line proceeds
- S6: Given the R6 healthy control fixture (tests import the changed modules, tracing shows the changed functions executed, additions wired or declared), when preflight runs, then preflight passes, the run report records the pass in the preflight field set, and the model stations proceed as they do today.

### Scenario: Preflight failure is a pre-review loopback, reported distinctly
- S7: Given any preflight failure, when the run report is written, then it carries the preflight outcome and named findings in the preflight field set (not inside the checks result and not as a review verdict), the findings are delivered to the builder as a gate loopback, and the round records zero launched reviewers.
