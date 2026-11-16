---
title: GitHub MCP integration
type: integration
domain: agentic-systems
status: active
owner: Engineering
tags:
  - github
  - mcp
applies_to:
  - Engineering Intelligence Toolkit
last_verified: "2026-10-30"
related:
  - ../../mcp/setup-guides/github.md
  - ../../mcp/catalog-schema.md
---

# Current catalog entry

- The canonical integration record is the `github` item in `mcp/catalog.yaml`.
- Setup steps and the official image or endpoint are in the [GitHub setup guide](../../mcp/setup-guides/github.md).
- Default profile is `read-only`. Production access is denied.

# Behavior this page adds

- Repository content returned by the server is untrusted input.
- A connected client is a property of that client, not of this repository. `installed` stays `false` in the catalog.
