---
title: Design read
type: concept
domain: application-engineering
status: active
---

# Role

Read a Figma file or frame before implementation. Do not change the design file.

# Skills

- `read-figma-design` calls `get_file` and `get_frame` on `figma-mcp`.
- `read-jira-issue` supplies a Figma link when the task starts from an issue.

# Boundary

This persona names skills and tools. It does not call Figma. The server under `mcp-servers/figma` is the client.
