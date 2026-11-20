# Checks Gate: pre-review
Basis: builder_delta
Attempt: 3

# Check Commands
## Command 1: python -m unittest discover -s tests -p 'test_*.py'
Exit code: 0
Output:
```
anchName false"
Switched to a new branch 'work-branch'
.hint: Using 'master' as the name for the initial branch. This default branch name
hint: will change to "main" in Git 3.0. To configure the initial branch name
hint: to use in all of your new repositories, which will suppress this warning,
hint: call:
hint:
hint: 	git config --global init.defaultBranch <name>
hint:
hint: Names commonly chosen instead of 'master' are 'main', 'trunk' and
hint: 'development'. The just-created branch can be renamed via this command:
hint:
hint: 	git branch -m <name>
hint:
hint: Disable this message with "git config set advice.defaultBranchName false"
Switched to a new branch 'work-branch'
................................................................................................................................../opt/hostedtoolcache/Python/3.12.16/x64/lib/python3.12/unittest/case.py:589: ResourceWarning: unclosed <socket.socket fd=3, family=2, type=1, proto=0, laddr=('127.0.0.1', 46391)>
  if method() is not None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
.../opt/hostedtoolcache/Python/3.12.16/x64/lib/python3.12/unittest/case.py:589: ResourceWarning: unclosed <socket.socket fd=3, family=2, type=1, proto=0, laddr=('127.0.0.1', 37785)>
  if method() is not None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
....................................................................................s....................................ss.........................................................................................................................................................s......s......................................................................................................s............................................................................................................................
----------------------------------------------------------------------
Ran 736 tests in 70.892s

OK (skipped=6)

```

## Gate practices

Gate enforced practices this run resolved. The gate is accountable for them:

- P-1: Traversal proof for platformer orders
- P-2: Deterministic validation of builder reports with declared literals
- P-3: Capture evidence must exist before design review

## Artifact validation

- builder report: /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-41/runs/wo-gh-41/builder.output.md
- observed: missing
- report source: none
- required literals declared: 0
- result: fail
- finding: Builder report artifact /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-41/runs/wo-gh-41/builder.output.md is missing.
