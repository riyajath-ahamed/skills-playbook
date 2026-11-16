---
title: Cloud infrastructure inspection setup
type: integration
domain: platform-engineering
status: active
id: guide.mcp.cloud
last_verified: "2026-10-30"
tags:
  - aws
  - mcp
---

# Provider

- Official remote server documented by AWS: `https://aws-mcp.us-east-1.api.aws/mcp`.
- Europe (Frankfurt) endpoint documented on the same page: `https://aws-mcp.eu-central-1.api.aws/mcp`.
- Documentation: [Getting started with the AWS MCP server](https://docs.aws.amazon.com/agent-toolkit/latest/userguide/getting-started-aws-mcp-server.html).
- This entry does not cover other cloud vendors. Google Cloud is [GCP infrastructure inspection](gcp-cloud-infrastructure.md).

# Authentication

- The provider supports OAuth. Some clients need `?oauth=initialize` on the URL. Follow the provider's client list rather than guessing.
- IAM still bounds what the signed-in identity can do. Attach the provider's documented OAuth sign-in policy only on a role that should have it.
- Do not copy access keys into MCP configuration.

# Permissions

- Catalog profile: `read-only`.
- Reads require approval because they can expose account inventory.
- Writes, deploys, and production use are denied by the catalog defaults.
