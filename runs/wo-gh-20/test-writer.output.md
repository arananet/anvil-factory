Tests written to `tests/test_community.py`. The file contains 6 test methods covering all required scenarios:

**S1** (line 12): `test_s1_init_project_creates_full_community_set` - Verifies scaffolded projects have all 7 community files with substituted values and no template residue

**S2** (line 51): `test_s2_onboard_preserves_existing_contributing` - Confirms onboarding preserves existing CONTRIBUTING.md byte-identical while creating the other 6 files

**S3** (line 92): `test_s3_scaffold_and_onboard_produce_identical_files` - Proves both doors render identical community files from the same metadata

**S4** (line 140): `test_s4_contact_substitution_and_no_hardcoded_identity` - Validates distinctive contact appears as enforcement/reporting contact with no other email addresses

**S4** (line 178): `test_s4_no_contact_fallback_to_github` - Tests GitHub fallback behavior when no contact is configured

**Additional** (line 198): `test_renderer_produces_complete_set` - Direct test of the render_community_files function

The tests assume anvil/community.py will export a render_community_files function, and that init_project and onboard_project will accept optional description and contact parameters as specified in the work order.
