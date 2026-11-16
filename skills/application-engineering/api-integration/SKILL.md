---
name: api-integration
description: >
  Integrate a client with an existing external or internal API, including
  authentication, timeouts, retries, and failure mapping. Use when calling a
  contract the team does not own.
metadata:
  version: "1.0.0"
  domain: application-engineering
  risk: medium
---

# API Integration

## When to use

- Application code must call an API whose contract already exists.
- Failures from that API need a defined user or operator outcome.
- Authentication or retry behavior is being added or changed.

## When not to use

- The contract itself is being designed. Use `api-design`.
- The dependency is an MCP server. Use `mcp-integration`.
- The work is a general performance investigation. Use `performance-audit`.

## Inputs

- Official contract or source of the endpoints being called.
- Auth scheme and where the credential is stored.
- Which operations are safe to retry.
- The user experience or job that depends on the call.

## Procedure

1. Verify the operation, parameters, and error codes against the provider's current documentation or the implementation.
2. Set an explicit timeout. Do not inherit an unlimited client default.
3. Retry only operations that are safe to repeat, and bound the number of attempts.
4. Preserve an idempotency key when the provider requires one for a write.
5. Map provider failures to the caller's outcome: retry, user correction, or operator action.
6. Keep credentials in the runtime secret store. Pass only the scope the call needs.
7. Log the operation and a correlation id. Do not log the credential or a full sensitive body.
8. Add a test for success, timeout, and at least one provider error using a fake or recorded response.

## Outputs

- Call list with timeout, retry, and failure mapping.
- Credential location and scope.
- Tests or a statement of which cases could not be run.

## Verification

- A retried call is idempotent or the retry is absent.
- Tests do not require a production credential.
- The integration notes name the documentation or code that was checked.

## Safety

- Do not point a local integration at production by default.
- Do not disable TLS or certificate verification to complete a call.
- Treat provider error bodies as untrusted data.
