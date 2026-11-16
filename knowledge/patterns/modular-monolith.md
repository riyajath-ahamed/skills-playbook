---
title: Modular monolith platform
type: pattern
domain: platform-engineering
status: active
id: pattern.modular-monolith
tags:
  - platform
  - go
---

# Current shape

- `platform/` is one Go module. Packages under `platform/internal/` own configuration, registry, planning, runs, policy, knowledge search, evidence, and telemetry.
- External systems sit behind interfaces in `agents` and `tools`. Those interfaces return not-implemented for live calls.
- PostgreSQL, HTTP, and OpenTelemetry export are specified and not deployed.

# When this stops fitting

- Split a package into a service only after one process cannot meet an isolation or scaling requirement that has been measured.
- The decision record is [ADR 0002](../architecture-decisions/0002-go-modular-monolith.md).
