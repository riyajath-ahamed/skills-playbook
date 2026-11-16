---
title: Jira MCP setup
type: integration
domain: agentic-systems
status: active
id: guide.mcp.jira
last_verified: "2026-10-31"
tags:
  - jira
  - mcp
---

# Provider

- Local connector: `mcp-servers/jira/server.py`.
- Upstream API: [Jira Cloud REST v3](https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/).
- Cursor starts it over stdio. `python scripts/mcpctl.py start jira-mcp` serves it on `127.0.0.1:8102`.

# Authentication

- Set `JIRA_BASE_URL`, `JIRA_EMAIL`, and `JIRA_API_TOKEN` in `.env`.
- `JIRA_BASE_URL` is the site origin, such as `https://example.atlassian.net`.
- Do not put the token in Git.

# Permissions

- `get_issue_details` and `get_issue_comments` are reads.
- `create_issues_batch` returns a preview until `confirmed` is true and `JIRA_WRITE_ENABLED` is `true`.
- Production sites are denied by the catalog profile. Point `JIRA_BASE_URL` at a development site.
