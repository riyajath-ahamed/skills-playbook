---
name: refactoring
description: >
  Change code structure while preserving observable behavior. Use when
  duplication or tangled ownership is blocking a required change.
metadata:
  version: "1.0.0"
  domain: software-engineering
  risk: medium
---

# Refactoring

## When to use

- A required change is unsafe because the current structure hides the behavior.
- Demonstrated duplication should become one explicit interface.
- A module owns unrelated responsibilities and the boundary is already understood.

## When not to use

- The desired outcome includes new behavior. Ship or specify that behavior separately.
- There is no test or other characterization of the behavior being preserved, and the code is high-risk.
- The rewrite is motivated by preference and does not remove a concrete obstacle.

## Inputs

- The behavior that must stay the same.
- The structural problem, with an example of the pain it causes.
- Tests or a characterization method.

## Procedure

1. Characterize the current behavior with tests or a recorded oracle before moving code.
2. Make one structural change at a time. Keep the program buildable between steps.
3. Preserve public contracts and persistence formats unless a migration is an explicitly separate change.
4. Stop if a step requires a behavior change. Split that change out.
5. Re-run the characterization after each risky step.
6. Remove only the abstraction that the new structure made unused.
7. Describe the resulting ownership in the module or document that already owns that fact.

## Outputs

- The structural change and the behavior it preserves.
- Tests or checks used as the oracle.
- Any behavior change discovered and split out.

## Verification

- The characterization checks pass after the refactor.
- Public interfaces and stored formats are unchanged, or a migration is called out as not done.
- The diff does not mix an unrelated feature into the move.

## Safety

- Do not refactor security checks into a weaker shared helper.
- Do not expand production access in order to understand the code.
- Keep credentials and environment-specific endpoints where they already belong.
