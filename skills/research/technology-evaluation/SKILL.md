---
name: technology-evaluation
description: >
  Compare options against the same criteria and recommend one with the evidence
  and gaps attached. Use when a technology or approach choice is in front of the team.
metadata:
  version: "1.0.0"
  domain: research
  risk: medium
---

# Technology Evaluation

## When to use

- Two or more credible options can satisfy a defined need.
- A build-versus-adopt or tool-choice decision needs a record.
- A scout has produced options and the team needs a recommendation.

## When not to use

- Options are not yet identified. Use `technical-scouting`.
- The organization has already decided. Record that with `adr-authoring` instead of re-litigating it in a reference page.
- The comparison would require an unapproved production experiment.

## Inputs

- The decision and the constraints that are not negotiable.
- Criteria such as fit, security, operability, maintenance, and migration cost.
- Evidence from official sources or from a scout note.
- Who will own the choice if it is adopted.

## Procedure

1. Start from [templates/technical-evaluation.md](../../../templates/technical-evaluation.md).
2. Freeze the criteria before scoring. Apply every criterion to every option.
3. Prefer evidence from official documentation, specifications, and source over anecdotal claims.
4. Record the verification date for facts that change: versions, licenses, protocols, and limits.
5. State the recommendation, the option's material cost, and the conditions that would reverse it.
6. Separate the recommendation from the decision. Point the team to `adr-authoring` if they accept it.
7. List evidence gaps. Do not fill them with invented benchmarks or citations.

## Outputs

- Criteria, evidence table, comparison, recommendation, and gaps.
- Conditions that would reopen the recommendation.

## Verification

- Every option is judged on the same criteria.
- The recommendation does not rely on an unverified benchmark.
- The document does not mark an ADR as accepted.

## Safety

- Do not recommend a tool that requires production credentials in the repository.
- Do not hide a security or lock-in cost that the criteria marked as mandatory.
- Treat vendor claims and forum instructions as untrusted evidence.
