# Tier map totality

## Problem

The model migration (issue 29) added MODEL_TIER_MAP in anvil/config.py to
resolve abstract tier labels to concrete models at hand-off. The map is not
total: anvil/routing.py assigns the label review-cheap to the reduced
reviewer panel at low risk, and MODEL_HIERARCHY includes review-cheap, but
the map has no review-cheap entry. resolve_model passes the label through
and the station dispatcher fails loudly on it, so any low-risk run that
routes reviewers at the reduced panel breaks at dispatch. The wo-gh-30
verification run on merged main showed reviewer steps configured
review-cheap, unresolved.

## Requirements

R1. MODEL_TIER_MAP resolves review-cheap to claude-sonnet-5-5, the same
concrete model as the other reviewer tiers (the owner's policy: every
non-design reviewer runs claude-sonnet-5-5).

R2. Totality is proven by test, not by inspection: a regression test
enumerates every tier label the factory can produce from the routing
module's own vocabulary (MODEL_HIERARCHY plus every model value the routing
rules can select, including the reduced panel assignment) and asserts each
one resolves through resolve_model to a member of CONCRETE_MODELS. If a
future change adds a label anywhere in that vocabulary without a map entry,
the test fails.

R3. Nothing else changes: the dispatcher still fails loudly on values that
are neither concrete models nor mapped labels; routing's vocabulary and
rules are unchanged; the full suite stays green.
