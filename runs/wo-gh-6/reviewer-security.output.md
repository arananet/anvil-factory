Security review complete. I've identified 6 security findings, including 1 critical and 1 high-severity issue:

**Critical Issues:**
- Base ref configuration not enforced - the implementation reads from the current working tree instead of from git, allowing branches to modify their own security checks

**High Issues:**  
- Command injection via shell=True without proper base ref enforcement

**Medium Issues:**
- Path traversal vulnerabilities in protected path matching
- Insecure fallback in changed file detection

**Low Issues:**
- Missing input validation on configuration values
- Deploy command uses same unsafe execution pattern

The review has been written to `/home/runner/work/anvil-factory/anvil-factory/runs/wo-gh-6/reviewer-security.output.md` with verdict "fail" and detailed, actionable findings.
