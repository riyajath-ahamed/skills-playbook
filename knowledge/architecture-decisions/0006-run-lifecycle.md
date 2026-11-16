---
title: "ADR-0006: Explicit run lifecycle"
description: "A run moves through named states, and illegal transitions fail."
type: adr
domain: platform-engineering
status: active
id: adr.0006
tags:
  - runs
---

# Status

Accepted.

# Context

- Later execution needs approval, cancellation, failure, and recovery to be visible.
- Implict status strings would let a run skip approval or verification.
- Persistence in PostgreSQL is not part of this release.

# Decision

The project will model run state in `platform/internal/runs` with only these transitions:

| From | To |
|---|---|
| `pending` | `planning`, `cancelled` |
| `planning` | `awaiting_approval`, `running`, `failed`, `cancelled` |
| `awaiting_approval` | `running`, `cancelled`, `failed` |
| `running` | `verifying`, `failed`, `cancelled` |
| `verifying` | `succeeded`, `failed`, `cancelled` |
| `failed` | `planning` |

`succeeded` and `cancelled` are terminal. `failed` returns to `planning` only when recovery is requested. The transition function checks the current state and rejects anything else.

# Consequences

- Callers cannot mark a run succeeded from `pending`.
- The state machine is in memory. A process restart drops runs until a store exists.
- The next platform increment is a local run store in front of this state machine, still without a network database.

# Confirmation

- Unit tests cover each legal transition and at least one illegal transition from every non-terminal state.
- No command in `ei` claims a run was executed.
