I added `tests/test_model_migration_verification.py`, which encodes the corrected builder policy. The full suite on current main passes: 592 tests, OK, 6 skipped. That includes the readme showcase link test.

**What the new test checks**
- **S2, builder by surface:** the builder step's `configured_model` and `executed_model` must both be `openai/gpt-6.1-sol` when the surfaces include `ui`. They must both be `claude-opus-5-5` when there is no UI surface. A test also confirms the policy rejects the opposite value in each case.
- **S1 and S4, per-step agreement:** for every executed step except intake, `configured_model` equals the policy assignment and equals `executed_model`. `executed_model` is non-null and no tier label leaks. This is checked on both UI and non-UI work orders.
- **S5, missing self-report:** a runtime that reports no model leaves `executed_model` null.

**Limits**
- **Fake runtime:** the tests use a fake command runtime that echoes the model it was handed as a JSON `model` field. They check the runner's wiring and recording, not live Claude or Codex execution.
- **Intake:** intake is skipped in the agreement check. Its `executed_model` is not asserted, because the fake runtime prints only the intake JSON and no self-report.
- **Not covered:** S3 (design reviewers on Codex), S6 (empty change) and S7 (the suite itself) have no new tests. S3 and S6 depend on the real run's evidence.

**Policy mismatch**
- **Cause:** my first version failed because `spec-writer` resolved to `claude-opus-5-5`. The station files say `reasoning-strong`, and only `anvil.yaml` sets sonnet.
- **Fix:** the CLI applies the `anvil.yaml` model overrides, and the test harness now does the same (`apply_overrides`). I did not change any code.
- **Risk:** any run that skips `anvil.yaml` would assign opus to `spec-writer` and `test-writer`. The standing wiring is correct only because the overrides are applied.

No source files were modified. The only additions are the new test file, plus the spec and work order that were already untracked.
{"model": "claude-sonnet-5-5"}
