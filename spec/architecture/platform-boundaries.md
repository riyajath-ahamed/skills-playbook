---
title: Platform module boundaries
type: architecture
domain: platform-engineering
status: active
id: spec.architecture.platform-boundaries
tags:
  - platform
related:
  - ../../knowledge/architecture-decisions/0002-go-modular-monolith.md
---

# Packages

| Package | Owns | Must not |
|---|---|---|
| `internal/config` | Repository root, index path, environment label | Read a secret store |
| `internal/registry` | Skill and workflow discovery | Execute a workflow |
| `internal/planner` | Ordered steps and the single-agent default | Spawn a process |
| `internal/runs` | Legal state transitions | Persist to a database |
| `internal/agents` | Executor interface and orchestration guardrails | Call a model, launch workers, or claim a run succeeded |
| `internal/tools` | Gateway interface | Open an MCP session |
| `internal/policy` | Allow or deny decisions | Trust tool output |
| `internal/knowledge` | Keyword search over canonical files | Invent a citation |
| `internal/evidence` | In-memory artifact list | Store secret values |
| `internal/telemetry` | Structured logs with redaction | Export OpenTelemetry |

# Interfaces

- `agents.Executor` is the only execution port. The shipped implementation returns an error that says execution is not implemented.
- `agents.Guard` accepts or rejects an orchestration contract. A rejected contract does not reach the executor.
- `tools.Gateway` checks policy before any adapter. The shipped adapter returns not-implemented after an allow decision.
- `knowledge.Searcher` returns hits that include a repository path.

# Persistence

- Runs are in memory.
- The next increment is a local file store for run records that uses the existing state machine.
- PostgreSQL remains the intended shared store. No migration is applied in this release. `platform/migrations/README.md` records that limit.
