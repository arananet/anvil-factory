## Security Review Complete

I performed a comprehensive security review of the checks gate implementation, verifying all security controls across the three loopback rounds.

### Verified Security Controls

**✅ S4 Base Ref Enforcement (Critical)**
- Base ref configuration resolved once at run start from git, never re-read from working tree
- Uses `git show <base_ref>:anvil.json` to read from immutable base ref snapshot
- `resolve_base_ref_config` called exactly once (runner.py:342)
- Both module and CLI regression tests pass

**✅ CLI Path Wiring (Loopback Round 3)**
- `derive_base_ref()` automatically calculates merge-base of HEAD and base branch
- CLI invokes derivation before calling `run_pipeline` (cli.py:105-118)
- `--base-ref` option available for manual override
- Base ref recorded in run report for auditable provenance
- CLI regression test passes, proving S4 control works through real execution path

**✅ Shell Command Safety**
- Check commands executed with `shell=True` but safe due to base ref provenance
- Commands cannot be tampered with because they come from immutable base ref
- Git operations use list-form subprocess calls (no shell injection in git commands)
- Safety reasoning documented in docs/CHECKS-GATE.md

**✅ Protected Path Enforcement**
- Builder delta basis correctly implemented (runner.py:362-365, 691-695)
- Distinguishes violations (modify/delete base ref files) from observations (additions)
- Uses `_get_base_ref_files()` to determine which files existed in base ref
- Path matching uses `startswith()` on git-normalized paths (safe from traversal)

**✅ Documentation & Tests**
- Comprehensive docs/CHECKS-GATE.md with threat model and security rationale
- CHANGELOG.md updated with all three loopback round changes
- All 144 tests pass including critical S4 CLI regression test
- Test coverage includes both uncommitted and committed tampering attempts

### Threat Model Validation

The core security property holds: **a work branch cannot modify the checks it will be judged by**.

This is enforced through:
1. Check commands resolved from base ref via `git show`
2. Protected paths list resolved from base ref
3. Tampering with config file triggers protected path violation
4. Works correctly through both CLI and module API paths

**Verdict: PASS** - No security vulnerabilities identified. All critical controls from three loopback rounds properly implemented and tested.
