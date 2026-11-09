I've implemented the station artifact contract in the spine. All 13 contract tests pass, and the full suite is green: 621 tests, 8 skipped (it was 618 plus my 3 new wrapper tests). Nothing is committed yet.

**What changed**
- **Work order field** (`anvil/model.py`): work orders accept an optional `required_literals` field, a list of non-empty strings. It is checked when the work order loads.
- **S1, the result is the artifact** (`anvil/runner.py`):
  - The builder's packet now says where to write its report (`runs/<wo>/builder.output.md`) and lists the required literals.
  - A stale report is deleted before each builder attempt. If the builder writes the report itself, its chat reply is saved beside it as `builder.transcript.md` and never written over the report.
  - A reviewer whose `review.json` is missing, empty or doesn't parse is now marked `failed`. The step records the expected file and what was found, and the reason is kept for the approver.
  - A reviewer whose run fails outright is also recorded with its expected file. Its `review.json` is not counted even if it exists.
- **S2, validation before reviewers** (`anvil/gates.py`, wired into the gate in the runner): after the builder and before any reviewer starts, the gate checks that the report exists, isn't empty, and contains every required literal in full. An abbreviation like `67217b9d...c83b86f` fails. When literals are declared, a report the runner saved from chat output is rejected. A failure fails the gate, sends the work back to the builder with the validation log, and skips the reviewers. Work orders that declare nothing only get the exists-and-non-empty check.
- **S3, approver honesty** (`anvil/approver.py`): if an expected reviewer wasn't counted, an `approved` result becomes `human_required`. A `rejected` or `changes_requested` result stays as it is, but the decision text names each missing reviewer and why. The report also gets a new `reviews_uncounted` list. When every expected reviewer is counted, the result is exactly as before.

**Root causes in the wrappers.** The two lost reviewers were caused by the channel wrappers, so I fixed those too:
- `tools/codex_station.py` and `tools/claude_station.py` no longer fail on empty chat output when a valid review (or the station's own output file) exists. They also no longer write the chat reply over a file the station wrote.
- The Codex reviewer guard no longer trips on the wrapper's own `.output.md` or the reviewer's own `runs/<wo>/<station>.*` files. Changes to anything else still fail it.
- New test file: `tests/test_station_artifact_wrappers.py`.

**Decisions for you**
- **Reviewers on the http channel.** An existing protected test expects a reviewer on the http channel to stay `executed` with no review file, because that channel can't write files. So the fail-fast status is tied to whether the channel can write files: command channels can, http can't. On http the review is still not counted and the approver still names it. This depends on the type of channel, not on any model brand.
- **The rule against chat replies is only partly enforced.** When no literals are declared, a report saved from chat output is still accepted, as before; the spec requires that. The runner also can't tell a station-written report from a wrapper that copies the chat reply into that file; the wrapper fix narrows this but doesn't remove it. Declaring `required_literals` is what makes a chat summary bounce reliably.
- **The new wrapper guard test proves less than it looks.** `runs/` is git-ignored in this repo, so the end-to-end guard test there passes trivially. The guard logic itself is covered by a direct unit test.

Files under `pipelines/` and the existing tests are untouched, no dependency was added, and the produced files contain no em or en dashes.
{"model": "claude-opus-5-5"}
