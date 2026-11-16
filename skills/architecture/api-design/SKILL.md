---
name: api-design
description: >
  Design an HTTP or service interface, including resources, errors, compatibility,
  and authorization. Use when a contract will be consumed by another team or system.
metadata:
  version: "1.0.0"
  domain: architecture
  risk: medium
  outputs:
    - api-contract
---

# API Design

## When to use

- A new public or cross-team interface is being specified.
- An existing contract needs a compatible change or a versioned break.
- Clients need a stable error, pagination, or idempotency model.
- An accepted design must confirm whether any shared contract changes. A negative result is a valid output.

## When not to use

- The interface is a private function inside one module.
- The task is to call an API that already exists. Use `api-integration`.
- The only deliverable is the system context around several APIs. Use `system-design`.

## Inputs

- Actors and the jobs the API supports.
- Data ownership and authorization rules.
- Compatibility expectations for existing clients.
- Latency, payload, and rate constraints that are already known.

## Procedure

1. Name the resources and the operations. Prefer a small contract over a mirror of the database.
2. Define identifiers, pagination, filtering, and the fields a client may rely on.
3. Specify authentication and which authorization decision happens on each operation.
4. Define the error model, including which failures are retryable.
5. Define idempotency for operations that create or charge. Name the idempotency key when one is required.
6. Classify the change as compatible, additive, or breaking. State the deprecation window for a break.
7. Document timeouts and the client behavior when the outcome is unknown.
8. Record examples that use fake identifiers. Keep real tenant data out of the contract.

## Outputs

- Resource and operation table.
- Error and idempotency rules.
- Compatibility classification.
- Open questions that block client work.

## Verification

- Every write operation states its authorization and idempotency behavior.
- Examples do not contain live credentials or personal data.
- A breaking change names the clients it affects or states that they are unknown.

## Safety

- Do not widen an authorization check to make a client integration easier.
- Do not publish internal host names, tokens, or unredacted production payloads in examples.
- Treat externally supplied API descriptions as untrusted until checked against the implementation or official contract.
