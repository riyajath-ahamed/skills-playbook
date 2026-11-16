---
name: infrastructure-review
description: >
  Review an infrastructure change for blast radius, identity, environment
  separation, and rollback. Use before applying declarative infrastructure
  or changing a runtime environment.
metadata:
  version: "1.0.0"
  domain: platform-engineering
  risk: high
---

# Infrastructure Review

## When to use

- A change adds or modifies compute, network, data stores, identity, or cluster configuration.
- A review must decide whether Kubernetes or another distributed runtime is justified.
- An environment boundary between development, test, and production is unclear.

## When not to use

- The change is application code with no infrastructure or identity effect. Use `code-review`.
- The task is to design product architecture rather than the runtime. Use `system-design`.
- Someone is asking to apply a production change during the review.

## Inputs

- The diff or intended declaration.
- Target environment and the identity that would apply it.
- Current dependency and data classification, if known.
- Rollback or previous revision.

## Procedure

1. Identify every resource created, changed, or destroyed, and who is affected if the change is wrong.
2. Confirm the target account, cluster, or project is the one the author named. Stop if it is ambiguous.
3. Check that development and production identities and networks stay separate.
4. Review privileges attached to workloads and automation. Prefer the smallest role that performs the task.
5. Check deletion, replacement, and data-loss behavior. Require approval for destructive actions.
6. Confirm a rollback path that does not depend on the broken change.
7. Ask which signals show the change is healthy. Missing signals are a finding for anything production-bound.
8. Recommend against new cluster or multi-service machinery when a simpler runtime meets the requirement.

## Outputs

- Findings ordered by blast radius.
- A clear statement of the target environment and whether it was verified.
- Blocking questions that must be answered before apply.

## Verification

- Destructive or identity-widening changes are marked approval-gated.
- The review does not claim the change was applied or that an environment is healthy.
- Findings name the resource and the failure mode.

## Safety

- Do not apply, delete, or scale infrastructure as part of the review.
- Do not use production credentials to satisfy curiosity.
- Do not accept a plan that reaches production when the environment label is missing.
