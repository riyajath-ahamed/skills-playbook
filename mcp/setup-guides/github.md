---
title: GitHub MCP setup
type: integration
domain: agentic-systems
status: active
id: guide.mcp.github
last_verified: "2026-10-31"
tags:
  - github
  - mcp
---

# Provider

- Local connector: `mcp-servers/github/server.py`.
- Upstream API: [GitHub REST](https://docs.github.com/en/rest).
- Cursor starts it over stdio from `.cursor/mcp.json`, which `make mcp-config` generates locally. `python scripts/mcpctl.py start github-mcp` serves it on `127.0.0.1:8101`.

# Authentication

- Set `GITHUB_PERSONAL_ACCESS_TOKEN` in the repository `.env`.
- The connector reads that file. Do not put the token in `mcp/catalog.yaml`, `.cursor/mcp.json`, or Git.

# Permissions

- The tools are reads: pull requests, a pull request's changed files and diffs, files, commits, and issue search.
- Writes and merges are outside this connector.
- `python scripts/mcpctl.py doctor` checks that the token name is set. It does not call GitHub.
