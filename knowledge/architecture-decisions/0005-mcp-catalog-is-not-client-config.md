---
title: "ADR-0005: The MCP catalog is an internal schema"
description: "mcp/catalog.yaml describes approved integrations and permissions. It is not a client configuration file."
type: adr
domain: security
status: active
id: adr.0005
tags:
  - mcp
---

# Status

Accepted.

# Context

- MCP hosts use different configuration files and transports.
- A catalog that doubled as someone's live config would be copied with secrets or wrong paths.
- Presence in the catalog was being confused with a connected server.

# Decision

The project will keep `mcp/catalog.yaml` as an internal description. Entries set `installed: false` until a separate, checked mechanism can report a live connection. Setup guides link to official provider docs and show secret references, not secret values. Policies live in `mcp/policies/`.

# Consequences

- Operators translate a catalog entry into the host's real config format.
- The validator fails a catalog that embeds a detected credential or claims `installed: true`.
- The platform tool gateway consults the catalog and still does not open a connection in this release.

# Confirmation

- `scripts/validate-catalog.sh` enforces the schema and the secret check.
- Setup guides contain no personal access tokens or private keys.
