## Spec Review Complete

The cost measurement spec requires no revision. The spec is unambiguous: **S3 explicitly states that a step whose model has no price table entry records `measured: false` with a null amount**.

The test failures occurred because tests asserted the opposite of what S3 specifies. Since the intake station's model is 'default' (which has no price table entry), per S3 it must be unmeasured. The tests contradicted this clear specification.

Output written to `runs/wo-gh-10/spec-writer.output.md` — the spec is fit for purpose, and test corrections are correctly scoped to the test-writer station.
