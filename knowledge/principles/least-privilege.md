---
title: Least privilege for agents and tools
type: principle
domain: security
status: active
id: principle.least-privilege
tags:
  - security
  - permissions
---

# Rule

- Grant the profile and capabilities a task needs, then stop.
- Development write access does not include production access.
- Unknown integrations, environments, and profiles are denied.
- Written policy is not a runtime boundary. Name the client, server flag, or `platform/internal/policy` check that enforces it.

# Application

- MCP catalog entries default to `installed: false` and a read-only profile unless a narrower statement is impossible.
- High-risk server flags that enable writes or private-network access stay off in setup guides.
- Secret values are redacted from diagnostics.
