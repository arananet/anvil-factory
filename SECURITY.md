# Security Policy

## Supported Versions

The following versions of ANVIL are currently supported with security updates:

- The main branch
- The latest release

## Reporting a Vulnerability

If you discover a security vulnerability in ANVIL, please report it privately. **Do not open a public issue for vulnerabilities.**

GitHub private vulnerability reporting is not enabled on this repository. Please send your report to info@arananet.net.

Your report should include:

- A description of the vulnerability
- Steps to reproduce the issue
- The potential impact
- Any suggested mitigations, if you have them

## Security Relevant Surfaces

We especially welcome reports against these security relevant surfaces in the ANVIL system:

- **The deterministic checks gate and its base ref enforcement**: The gate that validates changes before they are approved. Reports about bypasses, ref manipulation, or enforcement gaps are critical.

- **The review parsing contract**: How the approver station reads and aggregates reviewer output. Reports about injection, parsing bugs, or verdict manipulation are important.

- **Gateway credential routing**: How credentials are routed to agent runtime executors. Reports about credential leakage, unauthorized access, or routing bypasses are critical.

## Response Timeline

We will acknowledge your report and work to understand and address the issue. We do not promise specific response timelines, but we take security reports seriously and will keep you informed of our progress.

## Disclosure Policy

Please allow us a reasonable amount of time to address the vulnerability before disclosing it publicly. We will coordinate with you on the disclosure timeline.
