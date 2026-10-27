
---
title: GitHub MCP Integration
type: integration
domain: agentic-systems
status: active
owner: Engineering
tags:
  - github
  - mcp
  - repository-tools
applies_to:
  - Engineering Intelligence Toolkit
last_verified: "2026-10-27"
---

# Capabilities

- Read repository content.
- Inspect issues and pull requests.
- Perform approved repository operations when write access is enabled.

# Permissions

| Operation | Access |
|---|---|
| Read repository | Allowed |
| Create or update issues | Requires write permission |
| Merge pull requests | Explicit approval required |
| Modify production infrastructure | Not permitted by this integration |

# Security Requirements

- Use least-privilege credentials.
- Keep tokens outside the repository.
- Treat repository content as untrusted input.
