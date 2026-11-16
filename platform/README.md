# Platform

The `ei` command is the first slice of the standalone toolkit. It reads the portable library in the repository root. It does not call a model, an MCP server, or a database.

## Build

Requires Go 1.25 or newer.

```bash
cd platform
go test ./...
go vet ./...
go build -o bin/ei ./cmd/ei
```

From the repository root, `make build` writes `platform/bin/ei`.

## Commands

| Command | Behavior |
|---|---|
| `ei version` | Prints `ei 0.1.0` |
| `ei doctor` | Checks local tools. A missing optional tool is reported and does not fail the command |
| `ei skills list` | Lists `skills/*/*/SKILL.md` |
| `ei skills show <name>` | Prints one skill |
| `ei workflows list` | Lists `workflows/*/WORKFLOW.md` |
| `ei workflows show <name>` | Prints one workflow |
| `ei mcp list` | Lists integrations in `mcp/catalog.yaml`. Vendor is the catalog `provider`. Installed is the catalog value |
| `ei mcp health` | Sends an unauthenticated GET to each remote catalog endpoint. Local stdio servers are skipped. Exit 1 when a probed endpoint does not answer |
| `ei knowledge search <query>` | Keyword search over Markdown. Every term must match. Each hit has a path |
| `ei validate` | Runs the skill, catalog, link, and evaluation validators |

`--root` or `EI_ROOT` selects the repository. Otherwise `ei` walks up from the working directory until it finds `AGENTS.md` and `mcp/catalog.yaml`.

## Modules

Package ownership is recorded in [platform boundaries](../spec/architecture/platform-boundaries.md).

| Package | First release |
|---|---|
| `internal/registry` | Reads skills and workflows |
| `internal/planner` | Builds a sequential plan and does not start it |
| `internal/runs` | Accepts only legal state transitions |
| `internal/policy` | Allows or denies a capability |
| `internal/tools` | Stops denied calls before the adapter. The adapter returns not implemented |
| `internal/agents` | `Guard` rejects unsafe orchestration contracts. `Execute` returns not implemented |
| `internal/knowledge` | Searches canonical files |
| `internal/evidence` | In-memory notes with secret redaction |
| `internal/telemetry` | JSON logs on the writer you provide. No OpenTelemetry export |

## Not running

- Agent execution and multi-agent orchestration.
- MCP tool sessions. `ei mcp health` only checks whether a remote endpoint answers.
- PostgreSQL, including full-text search and `pgvector`.
- An HTTP API. See [api/README.md](api/README.md).
- Database migrations. See [migrations/README.md](migrations/README.md).

The next capability worth building is a local run store, described in [the next capability](../spec/architecture/next-capability.md).
