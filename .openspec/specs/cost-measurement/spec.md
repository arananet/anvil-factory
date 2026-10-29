# Per Job Cost Measurement

Status: approved
Slug: cost-measurement

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose
A run report today records cost as null because nothing measures it, so nobody can say what a work order cost or compare the price of one line shape against another. This spec adds measurement where measurement is possible and honesty where it is not: usage the runtime actually reports gets summed and priced from a labelled price table; usage nobody reported stays unmeasured and is recorded as unmeasured. The factory never estimates silently, because a guessed cost is worse than an admitted gap.

## Requirements
- Each run step gains a cost record: measured (true or false), the token usage it is based on (input and output tokens, when reported), the model the price was taken from, and the priced amount when measured. Steps with no usage source carry measured false and a null amount.
- For stations executed by a runtime that leaves session transcripts with token usage (the Claude Code station wrapper's runtime writes transcript files recording per message usage), the executor sums the transcript usage attributable to the step's execution window and attaches it to the step. Attribution is by the transcript files the execution created or appended during that step; usage that cannot be attributed to a step is not spread across steps.
- For stations executed through the AI gateway over HTTP, the executor reads the usage object the gateway response reports (prompt and completion tokens) when the response carries one, and attaches it to the step the same way.
- Prices live in configuration: a price table mapping model names to input and output prices per million tokens, each entry labelled with its source and the date the price was recorded. A model with no table entry prices as unmeasured, and the step records that the price was missing rather than inventing one.
- The run report gains a cost section: the total, defined as the sum of measured steps only, the count of measured steps, and the count of unmeasured steps. The swimlane shows the total with its measured coverage (for example: total with 6 of 9 steps measured), so a partial total is never mistaken for a complete one.
- Cost measurement never changes a verdict: the approver, the gates and the human gate read nothing from the cost section.

## Scenarios

### Scenario: Transcript usage is summed and priced per step
- S1: Given a station execution whose runtime transcript records input and output token usage, when the step completes, then its cost record carries the summed usage, the configured price for the executed model, the priced amount, and measured true.

### Scenario: Gateway usage is consumed when the response reports it
- S2: Given an HTTP station execution whose response carries a usage object, when the step completes, then its cost record carries that usage and its priced amount with measured true; and given a response with no usage object, then the step records measured false and a null amount.

### Scenario: Unmeasured steps stay honestly unmeasured
- S3: Given a step with no transcript and no gateway usage, or an executed model with no price table entry, when the report is written, then the step's amount is null, measured is false, the reason (no usage reported, or no price recorded) is stated, and the step contributes nothing to the total.

### Scenario: The total is the sum of measured steps only and says so
- S4: Given a run with a mix of measured and unmeasured steps, when its report and swimlane are read, then the cost section's total equals the sum of the measured steps' amounts, the counts of measured and unmeasured steps are stated, and the swimlane shows the total with its coverage counts.

### Scenario: Prices carry their source and date
- S5: Given the shipped price table configuration, when it is read, then every entry names its source and the date the price was recorded, and the loader rejects an entry missing either label.
