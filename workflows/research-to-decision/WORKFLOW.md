---
name: research-to-decision
description: >
  Turn a technology or approach question into a sourced recommendation and,
  when accepted, an architecture decision record.
execution: sequential
multi_agent: optional
skills:
  - technical-scouting
  - source-verification
  - technology-evaluation
  - adr-authoring
---

# Research to Decision

## Purpose

Produce a recommendation that cites checked sources, and record an ADR only after a person accepts it.

## Activation

- A team must choose an approach, dependency, or product capability.
- The cost of a wrong choice is high enough to justify a written comparison.
- The choice is not already recorded in an accepted ADR.

## Inputs

- The decision and the constraints that are mandatory.
- The date after which external facts must be rechecked.
- The person who can accept the decision.

## Steps

### 1. Survey the options
- Depends on: none
- Skill: technical-scouting
- Produces: question, constraints, and a sourced option list

### 2. Check load-bearing claims
- Depends on: survey
- Skill: source-verification
- Produces: claim table marked confirmed, contradicted, or unverified

### 3. Compare the options
- Depends on: checked claims
- Skill: technology-evaluation
- Produces: recommendation, tradeoffs, and gaps

### 4. Record the decision
- Depends on: accepted recommendation
- Skill: adr-authoring
- Produces: ADR, or a note that the recommendation was not accepted

## Outputs

- Evaluation record.
- Evidence table.
- ADR when the recommendation is accepted. Otherwise the recommendation remains a proposal.

## Verification

- Load-bearing external claims have a source and a date.
- Every option is scored on the same criteria.
- An ADR is not marked accepted before the approval gate.

## Failure handling

- Stop if a mandatory constraint eliminates every option. Report that result.
- If a source cannot be opened, mark the claim unverified and continue only when the decision does not depend on it.
- Do not retry a missing official source by substituting an unsourced summary.
- A rejected recommendation ends the workflow at step 3.

## Approval gates

- Accepting the recommendation and publishing the ADR requires the named decision owner.
- No gate is required to read public documentation.

## Completion

The workflow is complete when the evaluation and evidence table exist, and either an accepted ADR is linked or the recommendation is explicitly left unaccepted.

## Multi-agent strategy

A coordinator may assign step 2 across independent claims. Specialists are read-only and must return the claim table, not a decision. The coordinator runs steps 3 and 4. This split is optional. One agent is the default. The `ei` platform does not launch the specialists.
