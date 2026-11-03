Security review completed. Found 5 security issues requiring changes:

**Critical findings:**
1. **Missing intake_outcome validation** - The WorkOrder model accepts arbitrary intake outcome structures without validating outcome values, required fields, or types
2. **Unsafe executor trust** - Runner directly assigns executor output to work order fields without validation (lines 449-465)

**Medium findings:**
3. **Missing risk validation** - Accepts any string instead of constraining to {low, medium, high}
4. **Missing surfaces validation** - Accepts arbitrary values instead of the defined vocabulary
5. **Content injection risk** - Intake outcome text (reasons, questions, descriptions) written to markdown reports without sanitization

Review written to `runs/wo-gh-7/reviewer-security.review.json`
