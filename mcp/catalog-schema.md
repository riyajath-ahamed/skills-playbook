---
title: MCP catalog schema
type: standard
domain: security
status: active
id: standard.mcp.catalog-schema
tags:
  - mcp
---

# Scope

`mcp/catalog.yaml` is an internal description of integrations and the profile each one uses. It is not a Cursor, Claude, Codex, or VS Code configuration file. Client setup notes live in `mcp/setup-guides/` and follow the provider's format.

# Top level

| Field | Required | Values |
|---|---|---|
| `version` | yes | `1` |
| `defaults.enabled` | yes | `false` in this repository |
| `defaults.environment` | yes | `development` |
| `defaults.approval_required_for_writes` | yes | `true` |
| `defaults.deny_production_by_default` | yes | `true` |
| `defaults.treat_tool_output_as_untrusted` | yes | `true` |
| `integrations` | yes | Non-empty list |

# Integration

| Field | Required | Rule |
|---|---|---|
| `id` | yes | Unique lowercase identifier |
| `name` | yes | Human-readable name |
| `purpose` | yes | What the integration is for |
| `status` | yes | `documented`, `reference`, or `planned` |
| `installed` | yes | Must be `false`. This file does not report a live connection |
| `provider` | yes | Upstream project or vendor |
| `transport` | yes | `stdio`, `http`, or `none` |
| `package` | yes for documented and reference | Package or image name. Empty only when `status` is `planned` |
| `permission_profile` | yes | `read-only`, `development-write`, or `production-restricted` |
| `risk` | yes | `low`, `medium`, `high`, or `critical` |
| `environments.production` | yes | `deny`, except a future entry that also uses `production-restricted` |
| `approval.writes` | yes | Boolean |
| `approval.production` | yes | Boolean |
| `last_verified` | yes | `YYYY-MM-DD` |
| `documentation` | no | Official documentation URL |
| `endpoint` | no | Remote MCP URL when the provider hosts one |
| `setup_guide` | no | Path relative to `mcp/` |
| `capabilities` | yes | List with `id` and `access` of `read` or `write`. For an upstream server, the list is what the vendor exposes and the profile may deny writes. For a connector under `mcp-servers/`, a `write` capability requires a profile that grants `write` |
| `health_check.supported` | yes | `true` only when this repository runs the check |

# Secret rule

Credential fields name an environment variable or secret reference. Values that match a private key, cloud access key, GitHub token, or bearer token fail validation. The validator reports the path and field, not the value.
