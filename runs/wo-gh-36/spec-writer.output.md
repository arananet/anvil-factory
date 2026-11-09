I changed scenario S8 in `.openspec/specs/practice-skills/spec.md` to the exact sentence from the loopback addendum. It now reads: "S8. With no practices base present, a run's packets are unchanged and report.json records an empty practices resolution; the verdict is the honest approver outcome for the reviews the run can count, and is not asserted to be approved."

The git diff shows one line changed in that file, and it contains no em or en dashes. I didn't change any other spec text, and I didn't run any tests. The test correction belongs to the test writer, so I left `tests/test_practice_skills.py` alone.
{"model": "claude-sonnet-5-5"}
