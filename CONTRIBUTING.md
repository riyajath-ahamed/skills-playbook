# Contributing

## Change process

- Read [AGENTS.md](AGENTS.md) and the standard that applies to the change.
- Keep one canonical copy of a rule. Link to it from skills and workflows.
- Do not add credentials, live tokens, or claimed integration status.
- Run `make test` before opening a review. It needs `.venv` with `mcp-servers/requirements.txt` installed, and Go.

## Add a skill

1. Create `skills/<domain>/<name>/SKILL.md`.
2. Follow [skill metadata](standards/skills/metadata.md).
3. Reference shared standards instead of copying them.
4. Run `scripts/validate-skills.sh`.
5. For a high-value skill, add a rubric fixture. See [evaluation fixtures](evals/fixtures/README.md).

## Add a workflow

1. Create `workflows/<name>/WORKFLOW.md`.
2. Follow [workflow definitions](standards/workflows/definition.md).
3. Reference skills that already exist.
4. Keep execution sequential. Mark multi-agent work as `optional` or `disabled`.

## Add knowledge

1. Choose the directory under `knowledge/` that matches the document type.
2. Add frontmatter from [frontmatter-template.yaml](standards/documentation/frontmatter-template.yaml).
3. Give durable documents an `id` when the path may change.
4. Rebuild the derived index with `scripts/build-index.sh`. The index is gitignored.

## Platform code

- Module path: `engineering-intelligence/platform`.
- Build and test from `platform/`: `go test ./...`.
- Do not add a network client that pretends to call MCP, a model, or a database.

## Review expectations

- Behavior changes need a test or a deterministic check.
- Documentation changes need valid frontmatter and working relative links.
- Security-sensitive permission changes need an explicit approval note in the review.
