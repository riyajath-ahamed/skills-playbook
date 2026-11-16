---
name: architecture-to-implementation
description: >
  Implement an accepted design as a reviewed change with tests and updated
  reference documentation.
execution: sequential
multi_agent: disabled
skills:
  - api-design
  - tdd
  - code-review
  - reference-documentation
---

# Architecture to Implementation

## Purpose

Carry an accepted design into a change that preserves the recorded contracts and can be reviewed.

## Activation

- An accepted design or ADR identifies the behavior to build.
- The next work is implementation, not another design pass.
- The change can be made in a development environment.

## Inputs

- The accepted design and ADRs.
- The repository and test command.
- Interfaces that other teams already depend on.

## Steps

### 1. Specify changed interfaces
- Depends on: accepted design
- Skill: api-design
- Produces: contract notes for interfaces the change adds or breaks

### 2. Implement with tests
- Depends on: contract notes
- Skill: tdd
- Produces: code and tests for the accepted behavior

### 3. Review the change
- Depends on: implementation
- Skill: code-review
- Produces: findings and a list of tests the reviewer did not run

### 4. Update the reference
- Depends on: review findings addressed
- Skill: reference-documentation
- Produces: reference page that matches the change

## Outputs

- Interface notes for any contract that changed.
- Implementation and tests.
- Review result.
- Updated reference documentation.

## Verification

- Tests covering the new behavior were run, or the gap is stated.
- Review findings of defect severity are fixed or explicitly deferred by the owner.
- The reference page matches the code that was reviewed.

## Failure handling

- Stop and return to `idea-to-architecture` if implementation shows the accepted design is impossible.
- Do not keep retrying a failing test without changing the code or the incorrect expectation.
- A failed review blocks step 4 until defects are addressed.

## Approval gates

- Merging or publishing the change requires the repository's normal review approval.
- A breaking interface change requires the owner named in the ADR.

## Completion

The workflow is complete when the change is reviewed, required tests have recorded results, and the reference page matches the implementation.

## Multi-agent strategy

Disabled. Implementation and review share the same change. A separate reviewer may use `code-review`, but this workflow does not assign concurrent writers.
