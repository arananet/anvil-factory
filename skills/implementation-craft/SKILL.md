---
name: implementation-craft
description: Implement a spec so the code is correct, small, readable and verified before it is handed to review. Use whenever a station writes or changes code.
---

The build is finished when the spec scenarios pass on the final tree, the project checks are green, and a reviewer can follow the change without you in the room. Passing the new tests is the floor, not the goal.

**Before writing**
- Read the spec, the tests, and the code you are about to touch, including its callers. Find how the project already solves similar problems and do it the same way.
- Restate the change to yourself as a short list of scenario by scenario steps. If a scenario cannot be met from the inputs, stop and say which one and why.

**Write the change**
- Make the smallest change that fully satisfies the spec. Do not refactor nearby code, rename things or add features the spec did not ask for; note them as follow ups instead.
- Solve the general case the scenario describes. Never special case the test inputs, hard code an expected value, or detect that a test is running.
- Names say what a thing is or does. Functions do one thing at one level of abstraction. Prefer plain control flow to cleverness.
- Validate input at the boundary and fail with a message that names the offending value and the rule it broke. Do not swallow exceptions or return a quiet default for a real error.
- Handle the unhappy paths the spec lists and the obvious ones it does not: empty input, missing file, bad encoding, repeated call.
- Reuse an existing helper before writing a new one. If you must duplicate logic that has to stay in sync, say so in a comment at both sites.
- Comments explain why, not what. Remove debug output, dead code and leftover scaffolding before you finish.
- Stay inside the write set the work order allows. Protected paths and frozen surfaces are not yours to change.

**Verify before handoff**
- Run the project check command on the final tree and read the output. Fix what fails. Do not hand off a red suite and do not edit a test to turn it green.
- Exercise the change the way a user would: run the command, open the page, call the endpoint. Tests passing and the feature working are two different facts; confirm both.
- For anything visual, look at the rendered result at the sizes the spec names before you call it done, and produce the captures the order asks for.
- Re-read your full diff once as a reviewer would. Look for the unhandled case, the leftover TODO, the file you did not mean to touch.

**Report honestly**
- The builder report states what changed (files and the scenario each change serves), what you verified and how (the exact command and its real summary line), and what is not done or not verified.
- Every number and claim in the report must reproduce against the final tree. If a scenario is unmet or a check fails, say so plainly; a known gap reported is worth more than a clean report that review disproves.
