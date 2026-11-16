---
title: Context7 MCP setup
type: integration
domain: research
status: active
id: guide.mcp.context7
last_verified: "2026-10-30"
tags:
  - context7
  - mcp
---

# Provider

- Package: `@upstash/context7-mcp`.
- Local transport: stdio through `npx -y @upstash/context7-mcp`.
- Remote endpoint documented by the provider: `https://mcp.context7.com/mcp`.
- The npm page checked on 2026-10-30 listed Node.js 20.18.1 or newer for the current package line. An API key is optional and raises rate limits.

# Authentication

- Pass the key as `CONTEXT7_API_KEY` or the provider's `--api-key` flag sourced from the environment.
- Do not commit the key. Queries leave the machine, so treat the integration as a data export of the prompt you send.

# Permissions

- The catalog profile is `read-only`.
- This repository does not install or call the package.
