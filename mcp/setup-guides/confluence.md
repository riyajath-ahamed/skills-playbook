---
title: Confluence MCP setup
type: integration
domain: agentic-systems
status: active
id: guide.mcp.confluence
last_verified: "2026-10-31"
tags:
  - confluence
  - mcp
---

# Provider

- Local connector: `mcp-servers/confluence/server.py`.
- Upstream API: [Confluence Cloud REST v2](https://developer.atlassian.com/cloud/confluence/rest/v2/intro/).
- Cursor starts it over stdio. `python scripts/mcpctl.py start confluence-mcp` serves it on `127.0.0.1:8103`.

# Authentication

- Set `CONFLUENCE_BASE_URL`, `CONFLUENCE_EMAIL`, and `CONFLUENCE_API_TOKEN` in `.env`.
- Do not put the token in Git.

# Permissions

- `get_page` is a read.
- This server has no publish tool. Publishing stays a separate approved action.
