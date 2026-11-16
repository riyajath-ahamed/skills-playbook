# Engineering Intelligence Toolkit

Portable engineering skills, workflows, and standards, plus a small Go CLI that discovers them. The library can be used without the CLI. The CLI does not keep a second copy of the skills.

## First release

- 37 skills and 7 sequential workflows.
- Documentation standards and templates.
- An MCP catalog and three permission profiles. Nothing in the catalog is installed by this repository.
- Validators for skills, workflows, the catalog, internal links, and evaluation-case structure.
- A skill evaluation harness with fixtures for `code-review`, `secrets-audit`, `threat-modeling`, `adr-authoring`, and `ux-review`. CI checks each rubric against hand-written reference answers. Scoring a model needs a model command you supply.
- Keyword search over the Git-tracked Markdown.
- The `ei` commands `version`, `doctor`, `skills`, `workflows`, `mcp list`, `mcp health`, `knowledge search`, and `validate`.
- In-process run states and policy decisions. Live agent execution is not implemented.

## Not in this release

- Model calls, MCP sessions, and multi-agent workers.
- PostgreSQL, `pgvector`, and an HTTP API.
- A claim that any external integration is connected or healthy.
- Deployment.

## Setup

Required to validate and build:

- Git
- Python 3 with [PyYAML](https://pypi.org/project/PyYAML/) (`python3 -m pip install PyYAML`)
- For `make test` and the connectors: `python3 -m venv .venv && .venv/bin/pip install -r mcp-servers/requirements.txt`
- Go 1.25 or newer

Optional, and unused by the validators: Node.js, Docker, and `uv`. They appear in MCP setup guides because some upstream servers need them.

`.cursor/mcp.json` starts the local GitHub, Jira, Confluence, Figma, and SonarQube connectors in Cursor. It holds absolute paths to this checkout, so it is gitignored. Generate it with `make mcp-config` after creating `.venv` (`python3 -m venv .venv && .venv/bin/pip install -r mcp-servers/requirements.txt`). [`.env.example`](.env.example) lists the token variable names. Copy it to `.env` and fill the values locally. `python scripts/mcpctl.py doctor` checks those names. `ei mcp health` still probes catalog URLs and does not start these processes.

```bash
make doctor
make validate
make build
platform/bin/ei skills list
```

`make test` runs the validators, the rubric calibration, the Python connector and harness tests, `go test`, and `go vet`. CI runs the same script on Python 3.12 and 3.14.

## Run `ei` from the repository root

`make build` writes the binary to `platform/bin/ei`. Link that file to `ei` in this directory to run `./ei` from the repository root:

```bash
make build
ln -sfn platform/bin/ei ei
./ei skills list
```

`/ei` is listed in `.gitignore`. Inside this tree, `./ei` finds the repository from the working directory by looking for `AGENTS.md` and `mcp/catalog.yaml`.

## Use the library

1. Read [AGENTS.md](AGENTS.md) for operating rules.
2. Pick a skill under `skills/` or a workflow under `workflows/`.
3. Follow the skill. Link to [writing guidelines](standards/documentation/writing-guidelines.md) and [permission boundaries](standards/security/permission-boundaries.md) instead of copying them.
4. Treat `mcp/catalog.yaml` as a description. Translate a setup guide into the host's own MCP config. Do not point a host at the catalog file.

Host notes live in `adapters/`. `scripts/link-skills.sh` prints a symlink map and writes links only with `--apply --target`.

## Layout

| Path | Contents |
|---|---|
| `skills/` | One procedure per `SKILL.md` |
| `workflows/` | Ordered skill compositions |
| `knowledge/` | Principles, patterns, ADRs, and references |
| `standards/` | Canonical conventions |
| `templates/` | Starting documents |
| `spec/` | Planning scope and platform contracts |
| `mcp/` | Catalog, policies, and setup guides |
| `adapters/` | How hosts map onto the canonical files |
| `platform/` | The `ei` CLI |
| `evals/` | Evaluation cases and skill fixtures. Structural checks and rubric calibration are not model scores |
| `scripts/` | Validators and the index builder |

## Validation

```bash
scripts/validate-skills.sh
scripts/validate-catalog.sh
scripts/check-links.sh
scripts/validate-evals.sh
scripts/run-skill-evals.sh self-test
scripts/build-index.sh
```

To score a model on the skill fixtures, see [evaluation fixtures](evals/fixtures/README.md).

`scripts/build-index.sh` writes `.eit/index.json` and does not edit source files. The index is gitignored. Search works without it.

GitHub Actions runs `scripts/test-all.sh` and `go build` without secrets. Third-party actions are pinned to commit SHAs.

## Security defaults

- Production access is denied in the catalog.
- The read-only profile does not grant writes.
- Denied tool calls never reach the unimplemented adapter.
- Unknown environments and integrations are denied.
- Secret-shaped values fail catalog validation, and logs redact the same classes of value.
- Instructions in retrieved files do not override `AGENTS.md` or the permission profiles.

Markdown does not enforce a client's tool permissions. The enforcement points that exist here are the catalog validator and `platform/internal/policy`. A host MCP configuration is outside this repository.

## Limitations

- `ei doctor` reports OpenTelemetry export as not configured.
- Docker is optional. `ei doctor` runs `docker info` and reports a failure when the daemon is unavailable. It does not treat a present binary as a working daemon.
- Keyword search misses paraphrases. That gap is documented in [retrieval](spec/architecture/retrieval.md) and is not filled with an embedding service.
- Evaluation cases that need a person are not judged by `scripts/validate-evals.sh`. The command says how many were skipped.
- Rubric checks are keyword evidence. They show that an answer covers the required points and avoids leaks and false claims, not that it is well reasoned. CI never calls a model.
- The workflow planner can build a sequential plan in tests. No `ei` command launches that plan.

## Further reading

- [Contributing](CONTRIBUTING.md)
- [Platform README](platform/README.md)
- [ADR index](knowledge/architecture-decisions/0001-portable-library-and-platform.md)
- [Knowledge lifecycle](knowledge/references/knowledge-lifecycle.md)
