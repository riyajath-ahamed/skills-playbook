---
title: GCP infrastructure inspection setup
type: integration
domain: platform-engineering
status: active
id: guide.mcp.gcp-cloud
last_verified: "2026-10-31"
tags:
  - gcp
  - mcp
---

# Provider

- Official remote server: `https://cloudcli.googleapis.com/mcp`.
- Documentation: [Use the Google Cloud CLI remote MCP server](https://docs.cloud.google.com/sdk/use-gcloud-mcp).
- Checked against that page on 2026-10-31. The provider marks this server Pre-GA. This guide does not mean the server is connected here.
- The server runs `gcloud` and `bq` for the signed-in identity. AWS remains [AWS infrastructure inspection](cloud-infrastructure.md).
- A local stdio package, `@google-cloud/gcloud-mcp`, is a different server. This catalog entry is the remote endpoint.

# Authentication

- Sign in with Google OAuth, or with the host's supported Google Cloud credential. The provider does not accept API keys for this server.
- The only OAuth scope documented for this server is `https://www.googleapis.com/auth/cloud-platform`. That scope can manage Google Cloud resources. IAM on the caller still limits what a command can do.
- Enable the Cloud CLI Execution API in the target project before the client can call the server. Do not copy a service account key into MCP configuration.

# Permissions

- Catalog profile: `read-only`.
- Reads require approval because they can expose project inventory.
- Writes, deploys, and production projects are denied by the catalog defaults.
- Do not point the signed-in identity at a production project.
