---
title: "ADR-0004: Single-agent execution is the default"
description: "Workflows run as one sequential procedure unless a split is optional and isolated."
type: adr
domain: agentic-systems
status: active
id: adr.0004
tags:
  - agents
---

# Status

Accepted.

# Context

- Extra agents add coordination cost and conflicting writes.
- Some reviews and research checks are independent enough to run side by side.
- This release has no agent executor.

# Decision

The project will require workflow `execution: sequential`. `multi_agent` may be `optional` or `disabled`, never `required`. The planner records a single-agent plan. Specialist contracts are documentation until an executor exists.

# Consequences

- The portable library can be followed by a person or one coding agent today.
- A future executor must implement the protocol in [multi-agent protocol](../../spec/architecture/multi-agent-protocol.md) before any workflow may set `multi_agent: required`.
- Tests must fail a workflow that requires multiple agents.

# Confirmation

- The workflow validator rejects `multi_agent: required`.
- `ei` has no command that launches an agent.
