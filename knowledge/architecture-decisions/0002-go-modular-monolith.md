---
title: "ADR-0002: Go modular monolith for the first platform"
description: "The first platform is one Go module with internal packages, not a set of network services."
type: adr
domain: platform-engineering
status: active
id: adr.0002
tags:
  - go
  - platform
---

# Status

Accepted.

# Context

- The fixed language choice for the initial platform is Go.
- The first useful commands are discovery, search, diagnostics, and validation.
- Splitting those commands into services would add deployment and failure modes before there is a second client.

# Decision

The project will implement the platform as one Go module in `platform/`. Package boundaries follow the responsibilities in [platform boundaries](../../spec/architecture/platform-boundaries.md). PostgreSQL, an HTTP API, and a web console remain extension points.

# Consequences

- `go test` and `go vet` cover the first release.
- A package may depend on another internal package. It may not open a network connection to simulate a missing service.
- Extraction of a service requires a later ADR.

# Confirmation

- The module builds a single `ei` binary.
- No package listens on a port in this release.
