Implementation complete. All loopback requirements addressed:

**1. S2/S3 Integration** - Contact sheet assembly and scoped packet builder now wired into run_pipeline. reviewer-design receives fresh scoped packets; builder packets consult evidence_images field.

**2. Layer Violation Fixed** - build_reviewer_design_packet in anvil/runner.py with no module-level imports from .stations. Station prompt loading happens inside the function.

**3. Provenance-Based Allowlist** - Content tagged with source paths; verify_packet_allowlist_by_provenance checks tags, not text patterns.

**4. PNG Hardening** - _read_png enforces byte/dimension caps before inflation, verifies CRCs, bounds-checks chunks. validate_work_order_paths validates file paths resolve inside project tree.

**5. Report Visibility** - astra_measured_tokens_total field added to RunReport, tracked per step, present in report.json.

**6. Review Channel** - Review written to builder.review.json as single JSON object.

All 26 tests pass. Files modified: anvil/runner.py (main implementation), runs/wo-gh-21/builder.output.md, runs/wo-gh-21/builder.review.json.
