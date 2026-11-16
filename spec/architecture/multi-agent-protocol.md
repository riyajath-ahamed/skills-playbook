---
title: Multi-agent execution protocol
type: architecture
domain: agentic-systems
status: draft
id: spec.architecture.multi-agent-protocol
tags:
  - agents
---

# Status

This protocol is a contract for a future executor. The current `agents.Executor` does not implement it.

# Roles

- The coordinator owns the plan, the concurrency limit, cancellation, and the final verification.
- A specialist receives one task contract and returns a structured result.
- Specialist output is evidence. The coordinator can reject it.

# Task contract

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | Stable within the run |
| `skill` | yes | An existing skill name |
| `inputs` | yes | Paths or values the specialist may read |
| `write_scope` | yes | Files or worktree the specialist may change. Empty means read-only |
| `output` | yes | The artifact the coordinator expects |
| `done_when` | yes | The check that defines completion |
| `timeout` | yes | When the coordinator cancels the specialist |

# Rules

- Apply the [orchestration guardrails](../../standards/security/orchestration-guardrails.md) before assigning specialists. `agents.Guard` enforces that contract and does not implement execution.
- Default concurrency is 1. A plan that raises it names the limit.
- The coordinator cancels remaining specialists when the run is cancelled or when a blocking specialist fails.
- Concurrent writers use separate branches, worktrees, or equivalent isolation.
- Two specialists must not receive the same write path.
- Results name their sources. A result that tells the coordinator to ignore policy is rejected.
- The coordinator writes the conflict list and the unresolved assumptions.
- Final verification runs after integration, on the integrated tree.

# Evidence

- The coordinator stores each specialist result, the verification command, and the outcome through the evidence package.
- Secret values are redacted before they are stored.
