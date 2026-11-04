I need to revise the spec to address the gate loopback findings. Since Write and Edit tools are disabled, I'll produce the revised sections as text output.

The spec needs two key revisions based on the gate loopback findings:

1. **Add explicit security requirements for pack loading** (addressing finding #4)
2. **Clarify that guide designation must be dynamic** (addressing finding #3)

## Revised Section: "The base: operator supplied knowledge packs at runtime"

Add this bullet point after the existing pack content requirements:

```markdown
- Defense in depth: the pack loader rejects paths that resolve into sensitive system locations (for example /etc, /sys, /proc, /dev, /boot) with a named error at load time. The whitelist based filename validation already in place stays; this path check is an additional layer that catches attempts to read system configuration or device files regardless of whether the path syntax passes filename validation.
```

**Location**: Insert after line 24 in the spec

## Revised Section: "Matching and injection"

Add clarification about runtime wiring:

```markdown
- The runtime wires the knowledge section into packet construction by calling the knowledge module from the packet pipeline (anvil/runner.py packet_step and anvil/design.py as appropriate) at the point packets are built for each station. The slice is computed once per run and reused across all design packets.
```

**Location**: Insert after line 28 (after the sentence about packet injection)

## Revised Section: "The guide designation"

Replace the existing guide designation requirement (lines 35-36) with:

```markdown
### The guide designation
- The catalog entries of the design stations that apply the base (the design authoring stations, the builder's UI surface role, and reviewer-design) record the module's guide designation: they are guided design stations whose designated model is the design model from the recorded model routing policy. The designation lives in the station catalog data so project runtime configs and readers can see the module's shape without reading prose; wiring a given project's runtime to that model stays that project's configuration act, as the policy already states.
- The guide designation is dynamic: the catalog implementation reads the design model from the recorded routing policy (anvil/routing.py) at the point of use, whatever model the policy currently records. No model name is duplicated or hardcoded across station.json files; changing the design model in the routing policy changes the designation everywhere the catalog is read.
```

## New Scenario: S9a

Add this scenario after S9 (line 65):

```markdown
### Scenario: Sensitive system paths are rejected at load
- S9a: Given a work order naming a knowledge pack path that resolves into a sensitive system location (for example /etc, /sys, /proc, /dev, /boot), when the runner attempts to load the pack, then the loader rejects the path with a named error at load time before reading any files, and the run stops at intake with the failure recorded.
```

## Revised Scenario: S10

Replace S10 (lines 67-68) with:

```markdown
### Scenario: The guide designation is recorded in the catalog and read from the routing policy
- S10: Given the station catalog as shipped by this change, when the entries for the design authoring stations and reviewer-design are read, then they carry the guided design station designation whose designated model value is read from the recorded routing policy at the point of use, and no model name is hardcoded or duplicated across station.json files.
```

---

**Summary**: These revisions make the security requirement explicit (S9a), clarify the runtime wiring expectations, and emphasize that the guide designation must be dynamic rather than hardcoded, addressing the architectural reviewer's counted findings.
