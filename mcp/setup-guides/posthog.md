---
title: PostHog MCP setup
type: integration
domain: application-engineering
status: active
id: guide.mcp.posthog
last_verified: "2026-10-30"
tags:
  - posthog
  - mcp
---

# Provider

- Hosted server: `https://mcp.posthog.com/mcp`.
- Documentation: [PostHog MCP](https://posthog.com/docs/model-context-protocol).
- The provider's wizard command is `npx @posthog/wizard mcp add`. That wizard writes client configuration. Do not commit the result if it contains a key.
- `@posthog/mcp` is an analytics SDK for instrumenting your own server. It is not this hosted server.

# Authentication

- Prefer the host's OAuth flow. The provider routes the account to its US or EU region.
- A personal API key is an alternative `Authorization` bearer credential stored by the client. Create it with the provider's MCP preset so the scope stays on one project.
- Do not put the key in `mcp/catalog.yaml`.

# Permissions

- Catalog profile: `read-only`.
- Changing flags, destinations, or other project settings is a write and needs approval.
- Some provider tools call models and can incur PostHog AI usage. That billing control is the PostHog organization's, not this repository's.
