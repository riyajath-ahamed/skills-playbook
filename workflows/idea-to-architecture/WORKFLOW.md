---
name: idea-to-architecture
description: >
  Turn a product or system idea into a reviewed design and the ADRs that
  record its consequential choices.
execution: sequential
multi_agent: optional
skills:
  - system-design
  - threat-modeling
  - architecture-review
  - adr-authoring
---

# Idea to Architecture

## Purpose

Produce a design that names boundaries, risks, and accepted decisions before implementation starts.

## Activation

- A new system or a boundary-changing capability is being proposed.
- Implementation would otherwise start without a recorded data owner or trust boundary.
- The idea is larger than a single interface or bug fix.

## Inputs

- Goals, users, and known constraints.
- Existing systems the idea must fit.
- Security or compliance constraints that are already accepted.

## Steps

### 1. Draft the design
- Depends on: none
- Skill: system-design
- Produces: design note with alternatives and assumptions

### 2. Model threats
- Depends on: design draft
- Skill: threat-modeling
- Produces: threat model for the proposed boundaries

### 3. Review the design
- Depends on: design draft and threat model
- Skill: architecture-review
- Produces: ranked findings and blocking questions

### 4. Record accepted decisions
- Depends on: review findings resolved or explicitly deferred
- Skill: adr-authoring
- Produces: one ADR per consequential choice

## Outputs

- Design note.
- Threat model.
- Review findings.
- ADRs for accepted choices.

## Verification

- Requirements in the design map to a mechanism.
- The threat model covers every trust boundary the design introduces.
- Blocking review findings are closed or explicitly deferred by the approver.

## Failure handling

- Return to step 1 when the review finds a missing data owner or an undefined boundary.
- Stop when a mandatory constraint makes the idea infeasible. Record that conclusion.
- Do not treat an open question as an accepted assumption when it changes the design.

## Approval gates

- A person accepts the design before implementation is treated as authorized.
- Production inspection, if the design work appears to need it, requires separate authorization and is not part of this workflow by default.

## Completion

The workflow is complete when the design, threat model, and review exist, and every consequential choice is an ADR or an explicit deferral.

## Multi-agent strategy

A coordinator may run threat modeling and an independent architecture review in parallel after the draft exists. Reviewers are read-only. The coordinator reconciles their findings before any ADR is accepted. One agent remains the default. `ei` does not execute this split.
