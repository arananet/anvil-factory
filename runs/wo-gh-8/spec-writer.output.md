Spec revision complete. I've updated the risk-routing spec to align with the work order's detailed scenario descriptions:

**Changes made:**
1. **Status**: Changed from "approved" to "draft" (revision requires re-approval)
2. **S1**: Made explicit that the reduced set is "reviewer-spec and reviewer-tests"
3. **S3**: Expanded from covering only null risk to covering all full-panel cases:
   - Null risk rating defaults to full panel (unrated)
   - UI surface keeps reviewer-design in the set
   - Medium risk runs full panel at policy models
   - High risk runs full panel with explicit "no reduction" recorded

The spec now provides comprehensive test scenarios (S1-S6) that match the work order requirements while maintaining all the original requirements in the Requirements section. The spec is ready for review and approval before implementation begins.
