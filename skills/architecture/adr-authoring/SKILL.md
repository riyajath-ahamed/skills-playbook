---
name: adr-authoring
description: >
  Write an architecture decision record that states the decision, the forces
  that required it, and the consequences. Use when a choice is hard to reverse
  or needs a durable rationale.
metadata:
  version: "1.0.0"
  domain: architecture
  risk: low
  outputs:
    - adr
---

# ADR Authoring

## When to use

- A choice of boundary, data store, protocol, or execution model will be expensive to undo.
- Reviewers need the rationale kept somewhere other than a reference page.
- An existing decision is being superseded.

## When not to use

- The team is still comparing options. Use `technology-evaluation` or an RFC from [the RFC template](../../../templates/rfc.md).
- The text only describes current behavior. Use `reference-documentation`.
- The change is a routine implementation detail with no architectural consequence.

## Inputs

- The decision, or the short list still under consideration.
- Constraints that are already accepted.
- The document or ADR this record supersedes, if any.

## Procedure

1. Start from [templates/adr.md](../../../templates/adr.md).
2. Give the record a stable `id` and the next unused ADR number in `knowledge/architecture-decisions/`.
3. Write the decision as a direct statement of what the project will do.
4. Keep context to the forces that made a decision necessary.
5. Record consequences, including work that is explicitly deferred.
6. Add a confirmation section that says what evidence would support or reopen the decision.
7. If this supersedes another ADR, set `supersedes` and point the older record at this one.
8. Follow [writing guidelines](../../../standards/documentation/writing-guidelines.md). Do not paste the same rationale into a reference page.

## Outputs

- One ADR file with frontmatter, status, context, decision, consequences, and confirmation.

## Verification

- A reader can find the decision without reading the history of the discussion.
- Rejected options appear only when they explain a consequence or a constraint.
- The record does not claim the implementation is complete unless it is.
- Frontmatter validates and relative links resolve.

## Safety

- Do not put credentials, customer data, or exploit procedures in the record.
- Do not mark an ADR accepted without the review the change requires.
