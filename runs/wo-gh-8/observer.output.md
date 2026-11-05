## Observation Complete

I've completed the observation for work order wo-gh-8 and created the observation report at `runs/wo-gh-8/observer.output.md`.

**Summary**: The risk and surface routing feature is **fully implemented and spec-compliant**. All six scenarios (S1-S6) work as specified:

- ✓ **S1**: Low risk reduced panel at cheaper models
- ✓ **S2**: Security surface always keeps reviewer-security at strong model
- ✓ **S3**: Full panel routing for default/unrated cases, UI surface handling
- ✓ **S4**: Policy ceiling enforcement at config load time
- ✓ **S5**: Routed out reviewers as expected absences
- ✓ **S6**: Routing decisions in report with reasons

**Test status**: 242/242 tests passing (23 new risk routing tests)

**Review status**: 5/5 reviewers passed with 0 findings

**Loopback resolution**: Both loopback 1 (5 findings) and loopback 2 (1 test fix) successfully addressed

The implementation is production-ready, follows factory patterns, includes comprehensive documentation, and successfully dogfoods itself (routing was applied to its own work order).
