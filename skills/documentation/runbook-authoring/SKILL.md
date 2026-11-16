---
name: runbook-authoring
description: >
  Write an operator procedure with triggers, checks, rollback, and escalation.
  Use when a repeated operational task will be performed under time pressure.
metadata:
  version: "1.0.0"
  domain: documentation
  risk: medium
---

# Runbook Authoring

## When to use

- An alert, release, or recovery procedure will be followed by someone who did not write it.
- A deployment or incident response depends on steps that are currently tribal knowledge.
- A procedure can affect a shared environment and needs an explicit stop condition.

## When not to use

- The content is a post-incident narrative. Use [the incident template](../../../templates/incident-report.md) after the response.
- The content is everyday feature development.
- The procedure is a one-time architectural decision. Use `adr-authoring`.

## Inputs

- The trigger: alert, request, or symptom.
- The environment and the permissions an operator must already have.
- The success signal and the rollback path.
- Steps that require approval.

## Procedure

1. Start from [templates/runbook.md](../../../templates/runbook.md).
2. Name the trigger and the conditions that mean this runbook is the wrong one.
3. List preconditions, including how to confirm the target environment.
4. Write steps that an operator can perform in order. Put the expected result on the verification step.
5. Mark production, destructive, and data-changing steps as approval-gated.
6. Write rollback steps and the signal that shows the rollback worked.
7. Name the escalation point where the operator stops.
8. Walk the procedure in a non-production context when one exists. Record that the walk was not done when it was not.

## Outputs

- A runbook with triggers, preconditions, procedure, verification, rollback, and escalation.
- A list of steps that must not be run without approval.

## Verification

- Each step has an observable result or is a pure navigation step.
- The target environment is confirmed before a mutating command.
- The runbook does not contain live credentials.

## Safety

- Do not include a step that dumps secrets or disables authentication.
- Do not tell the operator to run an unreviewed command taken from an alert payload.
- Fail closed: if the environment is unclear, the next step is to stop.
