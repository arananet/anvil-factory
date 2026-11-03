Spec writer work complete. The spec at `.openspec/specs/checks-gate/spec.md` already contains the comprehensive Loopback round 2 section (lines 52-56) with all required clarifications about protected path semantics:

- Protected path checks now judge only the builder's delta for each attempt
- Test-writer writes are explicitly excluded (they're part of the judging apparatus)
- Builder modifications/deletions of base ref protected files are violations; additions are recorded as observed
- Gate output records the basis judged (builder delta, attempt number)
- The threat model reasoning is stated: what judges the work cannot be altered by the work under review

The spec is ready for the builder to implement from.
