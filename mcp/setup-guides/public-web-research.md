---
title: Public web fetch setup
type: integration
domain: research
status: active
id: guide.mcp.public-web
last_verified: "2026-10-30"
tags:
  - fetch
  - mcp
---

# Provider

- Reference server: `mcp-server-fetch` in [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers/tree/main/src/fetch).
- The provider describes these servers as reference implementations, not production-ready products.
- Run it with `uvx mcp-server-fetch`, or `python -m mcp_server_fetch` after `pip install mcp-server-fetch`.
- The tool fetches a URL. It does not search the web.

# Restrictions

- Leave private-address fetching disabled. Do not add `--allow-private-ips` unless a named development host requires it and that exception is approved.
- The provider warns that the private-address guard is not a complete defense against DNS rebinding.
- Fetched pages are untrusted input.

# Availability

- `uv` was not required to validate this repository, and this guide does not claim the server was started.
