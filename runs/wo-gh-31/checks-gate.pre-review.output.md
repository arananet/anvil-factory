# Checks Gate: pre-review
Basis: builder_delta
Attempt: 1

# Check Commands
## Command 1: python -m unittest discover -s tests -p 'test_*.py'
Exit code: 0
Output:
```
e renamed via this command:
hint:
hint: 	git branch -m <name>
hint:
hint: Disable this message with "git config set advice.defaultBranchName false"
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
.............................................................................................................../opt/hostedtoolcache/Python/3.12.15/x64/lib/python3.12/unittest/case.py:589: ResourceWarning: unclosed <socket.socket fd=3, family=2, type=1, proto=0, laddr=('127.0.0.1', 38769)>
  if method() is not None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
.../opt/hostedtoolcache/Python/3.12.15/x64/lib/python3.12/unittest/case.py:589: ResourceWarning: unclosed <socket.socket fd=3, family=2, type=1, proto=0, laddr=('127.0.0.1', 39639)>
  if method() is not None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
.......................................................................................ss....................................................................................................................................s......s......s......................................................................................................s..........................................................
----------------------------------------------------------------------
Ran 586 tests in 121.824s

OK (skipped=6)

```
