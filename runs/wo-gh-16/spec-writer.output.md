Spec-writer task completed. The spec at `.openspec/specs/review-parsing-integrity/spec.md` is already complete and approved, with the loopback round section (L1 and L2) fully documented. 

The loopback section specifies:
- **L1**: Add the output contract section to all 9 reviewer station prompts
- **L2**: Make the packet contract in anvil/runner.py canonical, with tools/claude_station.py either matching it word-for-word or deferring to it

I've created the output file at `runs/wo-gh-16/spec-writer.output.md` confirming the spec is ready for implementation.
