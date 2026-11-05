Verification complete. I've confirmed that all three test repairs from the loopback run are correctly in place in `tests/test_readme_showcase.py`:

1. **test_showcase_external_links_valid**: Now hermetic by default (skips unless `ANVIL_LIVE_TESTS=1`), uses browser user agent when enabled
2. **test_station_count_accurate_r3**: Uses the factory's authoritative station registry (`anvil.stations.load_registry`)
3. **test_factory_suite_can_run**: Removed the redundant nested pytest invocation

The test suite provides complete coverage of the spec scenarios (22 tests total) with no modifications needed for this closing verification run. Output recorded in `runs/wo-gh-23/test-writer.output.md`.
