---
name: tdd
description: >
  Implement a behavior by writing a failing test, making it pass, and then
  refactoring. Use when the desired behavior can be checked automatically.
metadata:
  version: "1.0.0"
  domain: software-engineering
  risk: low
---

# Test-Driven Development

## When to use

- A new behavior or bug fix has an observable outcome a test can assert.
- A regression should be pinned before the fix.
- A refactor needs a safety net. Pair this skill with `refactoring`.

## When not to use

- The outcome is a research recommendation or a document with no code behavior.
- The environment cannot run the relevant test, and a test would only be pretended to pass.
- The work is exploratory debugging and the failing behavior is not yet isolated. Use `debugging` until it is.

## Inputs

- The behavior, including at least one failure or edge case.
- The existing test command and where similar tests live.
- Dependencies that must be faked or kept out of the test.

## Procedure

1. Find the nearest existing test pattern and command.
2. Write one test that fails for the missing behavior. Run it and confirm the failure reason.
3. Implement the smallest change that makes that test pass.
4. Add tests for the edge cases that the requirement actually includes.
5. Refactor while the tests stay green. Do not change the behavior during that pass.
6. Run the focused tests, then the broader suite the change can affect.
7. Report the commands and results. If a command was not run, say so.

## Outputs

- A failing test that became a passing test.
- The implementation and any refactor performed under that net.
- Commands run and their results.

## Verification

- The new test fails if the behavior is removed.
- The test does not depend on production services, live secrets, or wall-clock timing unless that is the subject.
- No test was weakened or deleted to hide a failure.

## Safety

- Do not put secrets, personal data, or production identifiers into fixtures.
- Do not point a test at a production system to obtain a green result.
- Do not report a pass from a test that was not executed.
