---
name: sonar-review
description: >
  Read a SonarQube quality gate and unresolved issues through the sonar-mcp
  connector. Use when a review has a SonarQube project key.
metadata:
  version: "1.0.0"
  domain: software-engineering
  risk: medium
  tools:
    - get_quality_gate
    - search_issues
---

# Sonar Review

## When to use

- A review or pull request has a SonarQube project key.
- The task asks whether the quality gate failed.

## When not to use

- There is no project key. Use `code-review` on the diff.
- The task is to change a quality gate or resolve issues in SonarQube.

## Inputs

- The SonarQube project key.

## Procedure

1. Call `get_quality_gate` on `sonar-mcp` with the project key.
2. Call `search_issues` on `sonar-mcp` when the gate is not OK or the task asks for the issues.
3. If the connector returns `configured: false`, say the token is unset and continue the review from the diff.
4. Report the metric, status, and message returned by the connector. Do not reimplement the SonarQube API.

## Outputs

- The quality gate status.
- Unresolved issues that were returned, with severity and component.

## Verification

- A failed gate is reported only when `get_quality_gate` returned that status.
- The skill output does not claim an issue was resolved in SonarQube.

## Safety

- These tools are reads.
- Do not copy `SONARQUBE_TOKEN` into the skill output, a log, or Git.
