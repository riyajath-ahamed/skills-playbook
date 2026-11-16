---
title: Next platform capability
type: architecture
domain: platform-engineering
status: active
id: spec.architecture.next-capability
tags:
  - roadmap
---

# Choice

Persist run records on the local filesystem, and add `ei runs` commands that create a run, show it, and apply only legal transitions.

# Why this one

- The state machine and its tests already exist.
- A file store removes the process-restart gap without operating PostgreSQL.
- It does not pretend to execute agents or call MCP.

# Not next

- PostgreSQL and `pgvector`, until a shared multi-user store or a measured retrieval gap exists.
- An HTTP API and a React console, until a second client needs them.
- A live executor, until task contracts and cancellation can be tested against a real host.
