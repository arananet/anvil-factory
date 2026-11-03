I'll verify the spec against the work order requirements.

The existing spec at `.openspec/specs/render-crash-tolerance/spec.md` is complete and correctly structured. Let me verify it covers all work order requirements:

**Work Order Requirements Coverage:**

✓ **S1 (Output judgment)**: Spec requirement "Output judgment" and scenario S1 - chunk succeeds based on frame files + SECTION_RENDER_DONE line, not exit code alone

✓ **S2 (Queue never aborts)**: Spec requirement "The queue never aborts" and scenario S2 - no chunk failure stops other chunks from launching

✓ **S3/S4 (Completion sweep)**: Spec requirement "Completion sweep" and scenarios S3-S4 - compute missing ranges, re-queue at chunk size, max 2 passes, report missing ranges

✓ **S5 (Per chunk statistics)**: Spec requirement "Per chunk statistics" and scenario S5 - machine-readable records, outcome classes (clean_exit, tolerated_crash, requeued, failed), preserve existing keys

✓ **Compatibility**: Spec requirement "Compatibility frozen" - bash invocation, BLENDER/CHUNK env vars, frame/log naming unchanged

✓ **Frozen surfaces**: All frozen surfaces listed in spec match work order

✓ **Tests**: T1-T5 map to scenarios S1-S2 with fake chunk binary

✓ **Python stdlib only, no em/en dash**: Both specified in spec

The spec is complete, follows OpenSpec format (status, slug, roles, purpose, requirements, scenarios, tests), and accurately captures all work order requirements. No revisions needed.

**Output:** The spec file already exists at the correct location with all required content. The spec is ready for implementation.
