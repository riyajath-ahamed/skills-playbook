---
name: deployment-strategy
description: >
  Choose how a change is released, verified, and rolled back. Use when a
  build is ready to move beyond a local workspace.
metadata:
  version: "1.0.0"
  domain: platform-engineering
  risk: high
---

# Deployment Strategy

## When to use

- A change needs a path from development to a shared environment.
- The team must choose a rollout, verification, and rollback method.
- A release is blocked on an approval or a missing operational check.

## When not to use

- The code is not yet reviewed. Use `code-review` first.
- The question is which signals to collect in general. Use `observability-design`.
- The request is to deploy production immediately without a named approver.

## Inputs

- The change and its user-visible or operational effect.
- Target environment and release owner.
- Compatibility and migration constraints.
- Signals that indicate success or the need to roll back.

## Procedure

1. Keep the first release local or in a non-production environment unless production is explicitly authorized.
2. Define the artifact that is deployed: image, package, or revision. Avoid deploying an uncommitted workspace to a shared environment.
3. Choose a rollout that matches the blast radius. A full replacement needs a faster rollback than a small reversible flag.
4. Write the pre-deploy checks: tests, migration safety, and configuration that must be present.
5. Write the post-deploy checks and the time window for watching them.
6. Write rollback steps, including data migrations that cannot be reversed automatically.
7. Name the approval required for production, data loss, or an irreversible migration.
8. Record the strategy in a runbook when operators will repeat it.

## Outputs

- Target environment, artifact, rollout, verification, and rollback.
- Approval gates and the person or role who can pass them.
- Checks that are still missing.

## Verification

- Rollback is possible with the permissions available to the release owner, or the gap is explicit.
- Production is not the default target.
- The strategy does not say a deploy succeeded unless it was executed and checked.

## Safety

- Treat deploy, migration, and publication as high-risk capabilities.
- Stop when the target environment or approver is ambiguous.
- Do not embed credentials in the pipeline definition.
