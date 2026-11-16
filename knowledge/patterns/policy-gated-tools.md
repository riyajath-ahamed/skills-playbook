---
title: Policy-gated tools
type: pattern
domain: security
status: active
id: pattern.policy-gated-tools
tags:
  - mcp
  - policy
---

# Current behavior

- An integration is described in `mcp/catalog.yaml` and bound to one default profile.
- `platform/internal/policy` evaluates a requested capability against that profile.
- A denied decision never calls a tool adapter.
- The tool adapter in this release refuses live calls even after a decision allows them.

# Limits

- A coding-agent client can still be configured outside this repository. The catalog does not control that client.
- Setup guides tell the operator which official server flags to leave off. They cannot flip those flags remotely.
