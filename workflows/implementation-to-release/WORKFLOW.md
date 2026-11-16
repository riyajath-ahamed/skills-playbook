---
name: implementation-to-release
description: >
  Take a reviewed implementation through a secret check, a release plan, and
  an operator runbook before it is released.
execution: sequential
multi_agent: optional
skills:
  - code-review
  - secrets-audit
  - deployment-strategy
  - runbook-authoring
---

# Implementation to Release

## Purpose

Release a change only after review, secret handling, verification, and rollback are explicit.

## Activation

- Implementation is complete enough to review.
- The change is intended for a shared environment.
- A release owner is identifiable.

## Inputs

- The diff and the test results already recorded.
- Target environment and release owner.
- Operational signals that indicate a bad release.

## Steps

### 1. Review the change
- Depends on: none
- Skill: code-review
- Produces: findings that block or allow a release candidate

### 2. Audit secrets
- Depends on: release candidate diff
- Skill: secrets-audit
- Produces: secret findings with values withheld

### 3. Plan the release
- Depends on: review and secret audit clear, or risks explicitly accepted
- Skill: deployment-strategy
- Produces: artifact, verification, rollback, and approvals

### 4. Write the operator steps
- Depends on: release plan
- Skill: runbook-authoring
- Produces: runbook for deploy and rollback

## Outputs

- Review and secret-audit results.
- Release plan.
- Runbook.
- A statement of whether the release was executed. Planning this workflow does not execute it.

## Verification

- Blocking review findings and real secret findings are closed before a shared environment is targeted.
- The plan names the target environment and the rollback.
- Production is not assumed to be the target.

## Failure handling

- A confirmed secret finding stops the release until the owner removes and rotates it.
- A failed verification step during an actual release follows the rollback in the plan. Do not improvise a second production write.
- Missing test evidence returns the change to implementation. It does not get waived silently.

## Approval gates

- Production release, data migration, and publication require the release owner.
- Accepting a residual security finding requires the owner accountable for that risk.

## Completion

The workflow is complete when the plan and runbook exist and either the release checks have been recorded or the release is explicitly not executed.

## Multi-agent strategy

Review and the secret audit may run in parallel as read-only passes. The release plan has one owner. `ei` does not execute the release or the parallel reviews.
