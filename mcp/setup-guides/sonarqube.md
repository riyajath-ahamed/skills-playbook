---
title: SonarQube MCP setup
type: integration
domain: software-engineering
status: active
id: guide.mcp.sonarqube
last_verified: "2026-10-31"
tags:
  - sonarqube
  - mcp
---

# Provider

- Local connector: `mcp-servers/sonar/server.py`.
- Upstream API: [SonarQube Web API](https://docs.sonarsource.com/sonarqube-server/latest/extension-guide/web-api/).
- Cursor starts it over stdio. `python scripts/mcpctl.py start sonar-mcp` serves it on `127.0.0.1:8108`.

# Authentication

- `SONARQUBE_TOKEN` is optional. Without it, the tools return `configured: false` and do not call SonarQube.
- `SONARQUBE_URL` defaults to `https://sonarcloud.io`. Set it for a self-hosted server.
- `SONARQUBE_ORG` is the SonarQube Cloud organization key when the token is for Cloud.
- Use a user token. Do not put it in Git.

# Permissions

- `get_quality_gate` and `search_issues` are reads.
- Changing a quality gate or resolving an issue is outside this connector.
