## Security Review Complete

**Verdict: PASS**

I've verified the checks gate implementation across all three loopback rounds and the closing verification requirements. The implementation has robust security controls with no defects found.

### Critical Security Controls Verified

**S4 Base Ref Enforcement (Primary Security Control)**
- Check commands and protected paths resolve from git base ref via `git show <base-ref>:anvil.json`
- Working tree fallback only for non-git projects (documented)
- Prevents work from modifying the checks it will be judged by
- Two S4 regression tests verify malicious check commands are NOT executed
- CLI wiring complete: `derive_base_ref()` derives from merge base, `--base-ref` option available
- CLI regression test confirms full path works correctly (both uncommitted and committed tampering blocked)
- Base ref recorded in run report for auditable provenance

**Shell Command Execution Safety**
- Commands execute with `shell=True` but provenance from base ref makes this safe
- Base ref controlled by project maintainer, never from builder-modified files
- Security reasoning documented in docs/CHECKS-GATE.md lines 195-202
- Timeout protection (300s default) prevents runaway processes

**Protected Paths Mechanism**
- Correctly judges only builder's delta per attempt (loopback round 2 semantics)
- Distinguishes modifications/deletions of base ref files (violations) from additions (observations)
- Uses `git ls-tree` to determine base ref files for accurate comparison
- Five regression tests prove loopback round 2 semantics work correctly

**Architecture Integrity**
- Pure `checks_gate()` function in anvil/gates.py with correct signature
- Runner orchestrates, gate evaluates (separation of concerns)
- Station kind "deterministic" correctly declared in stations/checks-gate/station.json
- No security-relevant side effects in gate evaluation

### Verification Against Work Order

All loopback round requirements satisfied:
- ✅ Round 1: S4 base ref enforcement with regression tests
- ✅ Round 1: Hygiene items (docs, CHANGELOG, pure function, protected paths default, station kind)
- ✅ Round 2: Builder delta semantics with five regression tests
- ✅ Round 3: CLI base ref derivation with comprehensive CLI regression test
- ✅ Closing: 144 tests passing locally (operator verified)

### Threat Model Assessment

**Sound threat model**: What judges the work (checks configuration, protected paths list) cannot be altered by the work under review (builder changes), because it's resolved from an immutable git ref recorded at run start.

**Minor observation**: Non-git projects use working tree fallback lacking base ref protection, but this is documented and is the only option for projects without git repositories. Projects requiring this security property should use git.

### Dogfooding Verified

Factory project anvil.json:
- Checks configured: `python -m unittest discover -s tests -p 'test_*.py'`
- Protected paths: `tests/`, `anvil.json`, `pipelines/`
- Uses same controls it implements

Review written to: `runs/wo-gh-6/reviewer-security.review.json`
