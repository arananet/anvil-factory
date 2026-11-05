Looking at this work order for the intake station. This is a gate loopback (round 5, final) requesting two specific fixes to the quality standard implementation:

1. **PROMPT DOCUMENTATION**: Explicitly document the S7 same-subject test duty in `stations/reviewer-design/PROMPT.md`
2. **SANITIZATION REGRESSION**: Apply control character sanitization to work order strings in `anvil/quality.py`

Both fixes are precisely scoped with exact locations, requirements, and constraints. The work is buildable as stated.

**Risk assessment**: Medium - involves security hardening (sanitization) and documentation updates to station contracts. Targeted changes to existing code with clear test requirements.

**Surfaces**: 
- `security` - Control character sanitization addresses injection prevention
- `content` - Prompt documentation update

```json
{
  "intake_outcome": {
    "outcome": "accepted"
  },
  "risk": "medium",
  "surfaces": ["security", "content"]
}
```
