I revised the spec at `.openspec/specs/attribution-default/spec.md`. The filing commit had already written a draft, so I reworked that one. I did not run any tests or checks, other than a grep confirming the spec has no em dashes.

**Changed or added**
- **Out of scope** is a new section. It covers retrofits, forcing the line into onboarded pages, `anvil.json`, `pipelines/`, `anvil.yaml` and existing tests, and gate behaviour for non-web orders.
- **Exception record** is a new section that fixes the exception line's shape. It affects R3 and R4.
- **Compliance test for R4** is a new section that defines "visible text" and what counts as an attribution naming ANVIL. It replaces the soft words in R4.
- **Scenarios S1 to S5** keep their ids, which the order requires as literals. Each now names the requirement it proves and uses concrete values, such as the default line, the Sentia credit and a sample exception line. S1 now also covers onboard, and S3 now includes ANVIL appearing only in an HTML comment.
- **S6 to S8** are new. S6 covers R3, S7 covers R5 and the no-em-dash rule, and S8 covers game placement under R1.
- R1 to R6 are unchanged.

**Left for the owner**
1. **Exception line.** The order says an exception is "recorded in the project spec or project configuration" but gives no format. I proposed `Attribution exception: approved by <owner> on <YYYY-MM-DD>: <reason>`, read from the project spec only. The owner should confirm it or give a different format, and say whether project configuration should also be read.
2. **Multiple HTML files.** I wrote that only the index page is checked when a deliverable has several HTML files. The order is silent on this, so please confirm.
3. **Order versus spec.** The order's R6 lists four tests and the spec adds a fifth, for the exception case. This follows the spec and the S4 requirement.
4. **Placement wording.** S8 is a structural check (the line sits in a footer or credits element outside the game canvas). The order's "does not break gameplay" can't be tested directly, so S8 is my testable stand-in.
5. **Protected paths.** The authorised surface already lists the new tests as the test-writer station's job, so I made no other changes there.
{"model": "claude-sonnet-5-5"}
