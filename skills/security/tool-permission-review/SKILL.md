---
name: tool-permission-review
description: >
  Review an agent's tool access against least privilege and fail-closed rules.
  Use when granting, widening, or auditing MCP and runtime permissions.
metadata:
  version: "1.0.0"
  domain: security
  risk: high
---

# Tool Permission Review

## When to use

- An agent, skill, or workflow is about to receive a new tool or a broader profile.
- A catalog or client configuration may allow production, writes, or shell access.
- A review must decide whether a requested integration is justified by the task.

## When not to use

- The tool is not being granted or widened, and nobody is relying on its permissions.
- The question is only whether a secret is present in a file. Use `secrets-audit`.
- The provider package itself is still unknown. Use `mcp-integration` to establish the facts, then review permissions.

## Inputs

- The task the agent is allowed to perform.
- The requested tools, profile, and target environment.
- `mcp/catalog.yaml`, the policy files, and [permission boundaries](../../../standards/security/permission-boundaries.md).

## Procedure

1. List the minimum capabilities the task needs. Deny the rest.
2. Compare the request with the integration's catalog profile. An escalation to a broader profile requires approval.
3. Deny the request when the environment is blank, production is implied but not authorized, or the integration is unknown.
4. Check server flags that enable writes, private-network access, or sensitive reads. Leave them off unless the approved task requires them.
5. Confirm development credentials and production credentials are not interchangeable in the proposed setup.
6. Confirm tool output cannot override higher-priority instructions or expand the grant.
7. State which controls the client or server enforces and which exist only as written policy.
8. Record the decision: allow, allow with a narrower profile, or deny.

## Outputs

- The decision and the profile that supports it.
- Capabilities granted and capabilities denied.
- Controls that the current runtime does not enforce.

## Verification

- Production access is denied unless the production-restricted profile and an approval are both present.
- A write or destructive capability has an approval rule.
- The review does not claim a server is installed or healthy unless that was checked.

## Safety

- Fail closed on ambiguous targets and profiles.
- Do not approve the union of all tools for convenience.
- Do not treat this document as a runtime enforcement mechanism. Name the enforcement point or its absence.
