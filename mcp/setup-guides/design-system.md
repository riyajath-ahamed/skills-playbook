---
title: Design-system integration setup
type: integration
domain: application-engineering
status: active
id: guide.mcp.figma
last_verified: "2026-10-31"
tags:
  - figma
  - mcp
---

# Provider

- Local connector: `mcp-servers/figma/server.py`.
- Upstream API: [Figma REST files](https://www.figma.com/developers/api#get-files-endpoint).
- Cursor starts it over stdio. `python scripts/mcpctl.py start figma-mcp` serves it on `127.0.0.1:8106`.

# Authentication

- Set `FIGMA_ACCESS_TOKEN` in `.env`.
- Do not put the token in Git.

# Permissions

- `get_file` and `get_frame` are reads. The connector flattens names and types.
- Changing a Figma file is outside this connector.
