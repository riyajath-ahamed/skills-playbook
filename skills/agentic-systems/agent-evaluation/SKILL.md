---
name: agent-evaluation
description: >
  Specify how an agent workflow should be judged, including expected properties,
  failure conditions, and whether the judge is a script, a person, or a model.
  Use when adding or changing a reusable skill or workflow.
metadata:
  version: "1.0.0"
  domain: agentic-systems
  risk: medium
---

# Agent Evaluation

## When to use

- A reusable skill or workflow needs a regression case.
- A team wants to compare a single-agent and a multi-agent approach.
- A quality claim needs a method that someone else can repeat.

## When not to use

- The need is a unit test for ordinary code. Use `tdd`.
- The need is to verify a citation. Use `source-verification`.
- No task has been defined yet. Design the workflow first.

## Inputs

- The task input and the context the agent is allowed to see.
- Properties that a good result must have.
- Outcomes that count as failure even if the prose looks fluent.
- Whether the property can be checked deterministically.

## Procedure

1. Write a stable case id and place it under `evals/`.
2. Describe expected properties, not a single acceptable paragraph.
3. Record failure conditions, especially permission bypasses, invented evidence, and skipped approval gates.
4. Choose the method: `deterministic`, `human`, `llm-judge`, or `hybrid`.
5. Implement a script only for properties that have an objective check.
6. For human or model judgment, write the rubric and state that the case has not passed until that judgment is recorded.
7. Keep fixtures free of secrets and production data.
8. When comparing orchestration styles, include a single-agent baseline and note cost, latency, and coordination failures.

## Outputs

- An evaluation case with id, task, context, expected properties, failure conditions, and method.
- A deterministic check when one is honest.
- An explicit statement of which judgments were not run.

## Verification

- Two reviewers would reach the same pass or fail on the deterministic checks.
- The case does not require verbatim wording unless the wording is a contract.
- A passing structural check is not described as a passing model evaluation.

## Safety

- Do not put live credentials, personal data, or customer content in fixtures.
- Do not score a workflow as safe because its instructions say it is safe.
- Include permission and refusal cases for tools that can write, deploy, or reach production.
