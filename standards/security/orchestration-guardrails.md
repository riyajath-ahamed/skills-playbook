---
title: Orchestration guardrails
type: standard
domain: security
status: active
id: standard.security.orchestration-guardrails
tags:
  - agents
  - orchestration
related:
  - permission-boundaries.md
  - ../../spec/architecture/multi-agent-protocol.md
---

# Enforcement

`platform/internal/agents.Guard` rejects an orchestration contract that breaks these rules. `agents.ScreenResult` rejects specialist text that tries to override policy. Neither function starts an agent. `agents.Executor` still returns not implemented.

# Limits

| Rule | Limit |
|---|---|
| Default execution | One agent. Concurrency starts at 1 |
| Concurrency | 1 through 4, and never higher than the specialist count |
| Timeout | Required for every specialist. At least 1 second and at most 15 minutes |
| Retries | 0 through 2 for the whole contract |
| Cancellation | Required when concurrency is greater than 1 |
| Final verification | Required when more than one specialist is assigned |
| Write scope | Empty means read-only. `.`, absolute paths, and `..` are rejected |
| Isolation | Write paths must not be equal or nested across specialists |
| Tools | A specialist lists only its own tools. `*`, `all`, `shell`, `deploy`, `delete`, and `credential_admin` are rejected |
| Environment | `development` or `test` when the specialist has tools or a write scope. Production is rejected |
| Skills | Every specialist skill must exist in the supplied registry |

# Specialist results

- A result is evidence for the coordinator to accept or reject.
- Text that tells the coordinator to ignore instructions, ignore policy, or bypass approval is rejected.
- A rejected result does not widen tools, write scope, or the target environment.

# Stop conditions

- Missing coordinator, specialist id, skill, or timeout.
- Unknown skill, unknown environment, or a duplicate specialist id.
- Isolation, cancellation, or final verification cannot be recorded on the contract.
