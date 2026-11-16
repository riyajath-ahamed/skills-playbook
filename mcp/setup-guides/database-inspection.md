---
title: Database inspection setup
type: integration
domain: platform-engineering
status: active
id: guide.mcp.database
last_verified: "2026-10-30"
tags:
  - postgres
  - aws
  - mcp
---

# Provider

- Package: `awslabs.postgres-mcp-server`.
- Documentation: [AWS Labs Postgres MCP server](https://github.com/awslabs/mcp/blob/main/src/postgres-mcp-server/README.md).
- Transport: local stdio through `uvx`. The provider also documents a Docker image built from that repository.
- Scope is Amazon Aurora PostgreSQL through AWS credentials and the RDS Data API. A local or non-AWS database needs a different server, which this catalog does not pin.

# Safe defaults

- Do not pass `--allow_write_query`.
- Keep `AWS_PROFILE` and `AWS_REGION` in the environment. Do not put access keys in the client file.
- The catalog profile is `read-only`, and reads still require approval because the data may be sensitive.
- Production clusters are denied.

# Availability

- Docker and `uv` were not used to start this server while writing the catalog.
