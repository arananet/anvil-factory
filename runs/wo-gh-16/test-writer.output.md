## Summary

Extended `tests/test_review_parsing_integrity.py` with two loopback round tests for S5 catalog coverage:

**L1 Test** (`test_all_reviewer_prompts_have_output_format_section_loopback_l1`):
- Verifies all 9 reviewer prompts have the Output Format section
- Checks for station, verdict, and findings fields
- Validates correct verdict vocabulary (pass, fail, changes_requested)
- **Status**: Failing on 8 of 9 stations (only reviewer-design has it)

**L2 Test** (`test_wrapper_restatement_matches_or_defers_to_canonical_packet_loopback_l2`):
- Verifies `tools/claude_station.py` either repeats canonical wording from `anvil/runner.py` or defers to packet
- Checks that wrapper doesn't create divergent contract statements
- **Status**: Failing (wrapper uses "authoritative review channel" instead of specific file path)

**Additional updates**:
- Fixed station count in `test_no_stations_added_removed_or_renamed_s6` to include all 9 reviewers
- Updated test documentation with loopback test listings

Tests are syntactically valid, executable, and confirmed failing before implementation. Output written to `runs/wo-gh-16/test-writer.output.md`.
