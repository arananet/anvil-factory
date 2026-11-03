New evidence, 2026-10-30, from arananet/platform25 run wo-gh-1 (asset factory), round 2, Actions run 41055025579.

The defect in this issue has a sharper mechanism than the original report, and it inverted a verdict. The review parser (anvil/runner.py, parse_review) scans the executor output and returns the FIRST object that parses with a verdict key. Reviewer station prompts ship worked examples containing exactly such objects: stations/reviewer-design/PROMPT.md carries Example 1, a changes_requested review whose finding states that no design system exists for the project.

In platform25 wo-gh-1 round 2, reviewer-design actually answered pass with no findings; its real output is on disk in the run evidence and in its station transcript. The parser counted the prompt example instead. The approver therefore produced verdict changes_requested on a single finding that is false against the run own tree: design/DESIGN.md and design/tokens.json exist in that tree, authored in the loopback round and verified value by value by reviewer-architecture, which passed.

So the counted review set was wrong in content, not only smaller than expected: 5 of 5 appeared counted, but one of the five was the prompt example, not the station answer. The same mechanism can ingest a pass example and approve work nobody approved. The counted vs expected decision fields cannot detect this, because the count looks complete.

The fix is filed as issue 16 with its own spec (.openspec/specs/review-parsing-integrity/spec.md): reviewers emit through one authoritative review file per station, the parser reads only that file as one whole JSON document and never scans free executor output, prompt examples are removed or rendered non JSON, and a missing or malformed review fails closed as uncounted and reported, never as a guessed verdict.

Posting note: this comment was posted by the anvil-execute-wo-gh-16 workflow with the workflow token, because the operator vault PAT cannot create issue comments (GitHub answers 403). The text is the operator's, unedited.
