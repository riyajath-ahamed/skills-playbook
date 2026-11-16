---
title: Kubernetes diagnostics setup
type: integration
domain: platform-engineering
status: active
id: guide.mcp.kubernetes
last_verified: "2026-10-30"
tags:
  - eks
  - kubernetes
  - mcp
---

# Provider

- Package: `awslabs.eks-mcp-server`.
- Documentation: [Amazon EKS MCP server](https://github.com/awslabs/mcp/blob/main/src/eks-mcp-server/README.md).
- Transport: local stdio through `uvx awslabs.eks-mcp-server@latest`.
- The provider's quickstart also shows `--allow-write` and `--allow-sensitive-data-access`. Omit both for this catalog entry.

# Permissions

- Profile: `read-only`. Cluster reads still require approval.
- Do not point kubeconfig or `AWS_PROFILE` at a production cluster.
- A non-EKS cluster is out of scope. Do not substitute an unreviewed Kubernetes MCP server.

# Availability

- This repository does not start the server or contact a cluster.
