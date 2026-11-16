---
name: living-documentation
description: >
  Compare durable documentation with the implementation and update the canonical
  page when behavior has drifted. Use after a change that alters documented behavior.
metadata:
  version: "1.0.0"
  domain: documentation
  risk: low
---

# Living Documentation

## When to use

- A code or configuration change alters a behavior that a reference page, runbook, or skill describes.
- A reader reports that a document and the system disagree.
- A release is incomplete because the operator-facing procedure is stale.

## When not to use

- There is no canonical document and the behavior is new. Use `reference-documentation` or `runbook-authoring`.
- The disagreement is an undecided design choice. Use `adr-authoring`.
- The text is a temporary task note. Do not promote it into `knowledge/` or `standards/`.

## Inputs

- The change and the documents that claim to describe the affected behavior.
- The implementation or other authoritative source.
- The document owner, when one is named in frontmatter.

## Procedure

1. Search the repository for the behavior's terms before creating a new page.
2. Compare each documented claim with the current source. List agreements and mismatches.
3. Update the canonical document. Do not create a second page that contradicts it.
4. Keep planning history in `spec/` and decision history in the ADR. Do not append a changelog section to the body.
5. Set or refresh `last_verified` only for claims that were checked.
6. Mark a document `deprecated` or `superseded` when it should no longer be followed, and link its replacement.
7. Run link and frontmatter checks on the pages that changed.

## Outputs

- Updated canonical pages, or a gap list when the source could not be verified.
- Supersession links when a document was retired.

## Verification

- The edited sentences match the implementation that was inspected.
- No second source of truth was introduced for the same fact.
- Unverified statements remain labeled.

## Safety

- Do not "fix" a document by describing a workaround that bypasses an authorization check.
- Do not include secret values found during the comparison.
- Do not delete a security constraint from a skill because the current code fails to enforce it. Report that as a defect.
