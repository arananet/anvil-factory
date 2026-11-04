Revised spec written to `.openspec/specs/post-deploy-health/spec.md`. The revision addresses all 6 gate loopback findings:

**1. Runner integration** (critical): Added explicit runner integration contract detailing how the runner calls the health module, records results in RunReport, serializes to the report health section, reflects outcome in deployment status, forces human gate when unhealthy, and shows in the swimlane. Also added S7 scenario to verify this wiring.

**2. Config contract**: Clarified that health target is declared in anvil.json or anvil.yaml, and that the runner loads, validates, and passes this configuration to the health verification module.

**3. Demonstration wiring**: Enhanced demonstration requirement to explicitly state "The demonstration must execute in an actual run: the demonstration configuration is loaded, the health verification runs, and the run report contains the health section with real evidence."

**4. SSRF and input hardening**: Added comprehensive Security hardening section covering:
- URL scheme validation (http/https only)
- SSRF protection (RFC1918, loopback, link-local, cloud metadata)
- Input validation for API parameters (alphanumerics, hyphens, underscores)
- Exception sanitization to prevent credential/topology leakage
- HTTP status validation (100-599)
- Credential guidance for documentation
- Added S6 scenario to verify SSRF protections

**5. Responsive table**: Added Rendered health results section specifying responsive handling for 390x844 mobile viewports without horizontal scrolling, while rendering cleanly at 1440x900 desktop.

**6. Tests**: The existing scenarios S1-S5 plus new S6 (SSRF) and S7 (runner integration) provide complete test coverage for the loopback requirements.
