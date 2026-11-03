Architecture review completed. The changes fit well with the project structure and decisions, particularly Decision 0002 (Headless Blender as a production tool). The implementation makes the render wrapper more robust by judging chunks on outputs rather than exit codes, tolerating post-completion crashes, and using sweep passes to recover missing frames. All frozen surfaces are respected, and project style rules are followed.

Review written to runs/wo-gh-25/reviewer-architecture.review.json with verdict: pass.
