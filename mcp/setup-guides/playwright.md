---
title: Playwright MCP setup
type: integration
domain: application-engineering
status: active
id: guide.mcp.playwright
last_verified: "2026-10-30"
tags:
  - playwright
  - mcp
---

# Provider

- Package: `@playwright/mcp`.
- Transport: stdio through `npx @playwright/mcp@latest`.
- Official getting started page: [Playwright MCP](https://playwright.dev/docs/getting-started-mcp).
- The npm README checked on 2026-10-30 asks for Node.js 18 or newer. The Playwright docs page asks for Node.js 20 or newer. Use Node.js 20 or newer.

# Use

- Point the browser at a local or other non-production origin.
- Browser actions that submit, authenticate, or change data are writes and need approval.
- Do not store session cookies or passwords in the repository.

# Availability

- Installing the package was not part of catalog authoring.
- A visible browser is not evidence that a product flow passed.
