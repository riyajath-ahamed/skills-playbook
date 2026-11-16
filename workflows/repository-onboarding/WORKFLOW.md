---
name: repository-onboarding
description: >
  Learn a repository's structure, how to verify a change, and where the
  canonical documents live, without modifying the repository.
execution: sequential
multi_agent: disabled
skills:
  - living-documentation
  - architecture-review
  - reference-documentation
  - guided-lab
---

# Repository Onboarding

## Purpose

Produce a short, sourced map of how a repository is organized and how a change is checked.

## Activation

- An engineer or agent is working in a repository they have not verified.
- Onboarding notes are missing or disagree with the tree.
- The task must not change the repository.

## Inputs

- Repository root and the instruction files that are present.
- The test, lint, or validation commands documented by that repository.
- The question the newcomer must be able to answer afterward.

## Steps

### 1. Compare docs with the tree
- Depends on: none
- Skill: living-documentation
- Produces: a list of instruction and reference claims that match the tree, and claims that do not

### 2. Review architecture records
- Depends on: docs-to-tree comparison
- Skill: architecture-review
- Produces: findings from an existing ADR or design, or a note that none was found

### 3. Locate canonical docs
- Depends on: boundaries
- Skill: reference-documentation
- Produces: links to existing canonical pages, or a gap list if a page is missing

### 4. Prove the local loop
- Depends on: documented commands
- Skill: guided-lab
- Produces: the command that was run and its result, or the missing prerequisite

## Outputs

- A brief onboarding note with paths, commands, and gaps.
- The result of the local verification command when it was run.

## Verification

- Every structural claim points at a file that was read.
- The note distinguishes missing documentation from missing code.
- No file in the onboarded repository was changed by this workflow.

## Failure handling

- If the documented command fails because a prerequisite is absent, record the prerequisite and stop.
- Do not invent a second build system to get a green result.
- If instruction files disagree, cite both and follow the repository's stated precedence.

## Approval gates

- No write approval is involved because this workflow does not modify the repository.
- Reading a private repository still requires authorization the operator already has.

## Completion

The workflow is complete when the newcomer note cites real paths and records the verification command's result or a specific missing prerequisite.

## Multi-agent strategy

Disabled. The output is one map, and parallel readers would still need a single editor to reconcile it.
