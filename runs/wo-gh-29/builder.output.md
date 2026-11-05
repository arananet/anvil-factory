The OpenAI station runtime is now the real Codex CLI. `tools/codex_station.py` no longer makes a plain chat completion. The full suite passes (560 tests, 3 skipped); the only test files I touched are two new ones. Whether this works live, with reviewer-design writing a review the runner counts and recording `openai/gpt-6.1-sol`, is only proven when this run executes. I could not reach the gateway from here.

**What the runtime does**
- **Invocation:** it runs `codex exec` headlessly in the repo tree, with the packet as the task and the bare model id `gpt-6.1-sol`. Stdin is closed, because `codex exec` appends piped stdin to the task and otherwise waits on it.
- **Route and credential:** Codex is pointed at the gateway OpenAI route, worked out as in round 4. The credential comes from `CF_AIG_TOKEN` or the `cf-aig-authorization` header. It reaches Codex only through two child-only environment variables, never the arguments; Codex error text is scrubbed of it.
- **Permissions:** all stations skip Codex's approval prompts and sandbox, the same as the Claude wrapper's skip-permissions. Builder and test-writer may write; every other station gets no-edit instructions.
- **Review handling:** review validation and the one in-session correction work as in the Claude wrapper. The dispatcher reports `openai/gpt-6.1-sol` as the executed model only after a successful run.
- **Failure:** a missing `codex` CLI, missing gateway environment, or non-OpenAI model fails the station loudly. There is no completion fallback.

**Checked against the real CLI (0.166, installed here) using a local stand-in server**
- **Request:** it went to `.../openai/responses` for `gpt-6.1-sol`, with the token in both the `Authorization` and `cf-aig-authorization` headers.
- **Agentic:** Codex declares its shell tool (`exec_command`) and its edit tool (`apply_patch`) to this model. They sit inside the request input rather than a top-level `tools` field, so the runtime really can act.
- **End to end:** going through the dispatcher with the credential taken from the header, the stand-in's error produced exit 2, no output file, no model report, and no token in any output.

**Decisions for you**
1. **Reviewers still have Codex's edit tool.** The obvious setting (`include_apply_patch_tool`) and three similar ones are ignored by Codex 0.166. The only thing that removes the tool is replacing the whole model catalog, which means copying OpenAI's instruction prompt into the repo or calling the CLI an extra time per run; the extra call breaks the new Codex tests, which count CLI calls. So:
   - Non-write stations get no-edit `developer_instructions`, which Codex does honour; this is the counterpart of Claude's denylist.
   - On top of that, I added a check: after each attempt, a reviewer that changed anything in the tree other than its own review file fails loudly. It compares git status before and after, so git-ignored paths such as `runs/` scratch files are outside its view. It's covered in the new `tests/test_codex_reviewer_guard.py`.
   - This check is stricter than the Claude side; say if you'd rather drop it.
2. **The completion call still exists in `codex_station.py` as a stub.** The protected round 3 and 4 tests call `codex_station.call_openai_api`, while the new tests ban the completion code from that file. The completion now lives only in `tools/model_route_smoke.py` (`route_completion`). `call_openai_api` just hands off to it, and station execution never calls it. Reviewers may see this as a leftover of the old path.

**Things to know for the live run**
- If the gateway's OpenAI route turns out not to serve `/responses`, setting `ANVIL_CODEX_WIRE_API` switches the wire format without a code change.
- The workflow installs the latest `@openai/codex`, while I checked 0.166, so a newer release could change any of this behaviour.

I also updated `docs/EXECUTION.md` and the CHANGELOG Unreleased section. I didn't touch `.github/` or any existing test file, and the files I produced contain no em or en dashes.
{"model": "claude-opus-5-5"}
