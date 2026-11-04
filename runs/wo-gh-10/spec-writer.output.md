I've reviewed the work order and checked the existing spec. The spec at `.openspec/specs/cost-measurement/spec.md` already exists and is marked as **approved**. 

Comparing the work order requirements with the existing spec:

**Work Order S1-S5 scenarios → Spec coverage:**
- ✓ S1: Transcript usage summed and priced per step
- ✓ S2: Gateway usage consumed from HTTP responses  
- ✓ S3: Unmeasured steps stay honestly unmeasured with reasons
- ✓ S4: Cost total is sum of measured steps only, with coverage counts
- ✓ S5: Price table with source and date labels, loader rejects incomplete entries

**Additional requirements all covered:**
- ✓ Cost measurement never changes verdicts (approver/gates ignore cost section)
- ✓ Attribution by execution window, no spreading of unattributable usage
- ✓ Model pricing from configuration table
- ✓ Swimlane displays total with coverage counts

The spec is complete, properly formatted, and matches all requirements from the work order. **No revision is needed.** The spec is ready for the next station (test-writer) to create tests based on scenarios S1-S5, followed by the builder to implement the code.
