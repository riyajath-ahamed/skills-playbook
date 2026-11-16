---
title: Evidence before confidence
type: principle
domain: research
status: active
id: principle.evidence-before-confidence
tags:
  - evidence
  - verification
---

# Rule

- A claim about an external system cites a source and the date it was checked, or it is labeled unverified.
- A claim about this repository cites a path, a command, or a test that was run.
- A recommendation is not an accepted decision. Acceptance is recorded in an ADR.
- A validator or test result applies only to the command that was executed.

# Application

- Skills that research or review record what they checked and what they did not check.
- The `ei` CLI reports missing optional tools as missing. It does not describe them as healthy.
- Evaluation fixtures are not treated as a passing model run.
