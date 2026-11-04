Looking at the failing test and the actual implementation. The issue is clear: the test patches `'requests.get'` but `anvil/health.py` imports requests conditionally and uses it at the module level. Since the factory is stdlib-only and requests is not installed, the test needs to patch at the correct location.

This is round 3's scope: fix the one failing test by patching the correct HTTP surface.

```json
{
  "intake_outcome": {"outcome": "accepted"},
  "risk": "medium",
  "surfaces": ["deploy"]
}
```
