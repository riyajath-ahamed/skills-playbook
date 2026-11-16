---
name: learn-a-technology
description: >
  Learn a technology from a checked explanation and a small lab, then capture
  a learning note that stays separate from engineering standards.
execution: sequential
multi_agent: disabled
skills:
  - concept-tutor
  - technical-scouting
  - source-verification
  - guided-lab
---

# Learn a Technology

## Purpose

Give a learner a verified mental model and one practiced task, without promoting notes into standards.

## Activation

- A person needs to use or evaluate a technology they do not yet know well.
- The learning goal can be demonstrated with a local exercise.
- The outcome is understanding, not an adoption decision.

## Inputs

- The technology and the task the learner needs to perform.
- Current level and time available.
- Official documentation or the source repository.

## Steps

### 1. Explain the core model
- Depends on: none
- Skill: concept-tutor
- Produces: a short model, a boundary, and a comprehension check

### 2. Scout the primary sources
- Depends on: the model
- Skill: technical-scouting
- Produces: official sources and a list of claims that need checking

### 3. Verify the claims the lab depends on
- Depends on: scout notes
- Skill: source-verification
- Produces: confirmed or unverified labels for lab-critical claims

### 4. Practice in a local lab
- Depends on: verified lab-critical claims
- Skill: guided-lab
- Produces: a lab result or a recorded missing prerequisite

## Outputs

- Explanation and sources.
- Lab steps and the observed result, or a statement that the lab was not run.
- A learning note when the result is reusable. It stays in draft until reviewed.

## Verification

- The explanation matches the sources that were checked.
- The lab check fails when the practiced step is skipped.
- The learning note is not placed in `standards/`.

## Failure handling

- If a prerequisite is missing, the workflow ends with that fact rather than a fictional result.
- If a primary source contradicts the explanation, correct the explanation before the lab.
- An adoption question is handed to `research-to-decision` instead of being decided here.

## Approval gates

- No approval is required for local reading and local labs.
- Installing software, creating accounts, or using paid services requires the learner's own approval and stays out of this workflow unless they ask.

## Completion

The workflow is complete when the learner has a sourced model and either a recorded lab result or a specific blocker.

## Multi-agent strategy

Disabled. The learner has one path, and a second agent does not improve the practice loop.
