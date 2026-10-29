The spec at `.openspec/specs/checks-gate/spec.md` already exists with status **approved** and comprehensively covers all requirements from work order wo-gh-6:

**Coverage verification:**
- ✓ S1: Passing checks scenario (line 27-28)
- ✓ S2: Failing checks return to builder with loopback (line 30-32)
- ✓ S3: Protected paths auto-fail gate (line 34-35)
- ✓ S4: Config from base ref snapshot (line 37-38)
- ✓ S5: Pre-deploy gate run after merge sync (line 40-41)
- ✓ S6: No checks configured case (line 43-44)
- ✓ Recording in report and swimlane (line 22-23)
- ✓ Loopback consumption (line 19)
- ✓ Protected paths default (checks config + tests/) (line 17)
- ✓ Delete counts as touching (line 21)

The spec is complete, approved, and ready for implementation by the implementer station. No revision is needed.
