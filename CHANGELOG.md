# Changelog

## Unreleased

- `jira-mcp`: `get_issue_details` reads smart-link cards and hyperlinks in the issue description, not only bare URLs in text.
- `github-mcp`: add `get_pull_request_files`, which pages through a pull request's changed files and returns each file's diff within a character budget. `github-change-review` 1.1.0 uses it.
- Catalog: Jira uses the `development-write` profile because `jira-mcp` ships a gated create. The catalog validator fails a connector under `mcp-servers/` that exposes a write its profile does not grant.
- The skill validator fails when the README skill or workflow count is stale.
- `.cursor/mcp.json` is no longer tracked. Generate it with `make mcp-config`.
- Add the skill evaluation harness (`scripts/run-skill-evals.sh`) and rubric fixtures for `code-review`, `secrets-audit`, `threat-modeling`, `adr-authoring`, and `ux-review`.
- Add the `ux-review` skill with usability heuristics, the UX review template, and the UX research persona.
- CI runs `scripts/test-all.sh`, including the Python tests and rubric calibration, on Python 3.12 and 3.14.

## 0.1.0 — 2026-10-30

- Add the portable skill library, workflow definitions, documentation standards, and templates.
- Add the MCP integration catalog and permission profiles.
- Add deterministic validators, local knowledge indexing, and evaluation cases.
- Add the `ei` command-line interface for discovery, search, diagnostics, and validation.
- Document platform module boundaries and the run lifecycle. Agent execution, MCP calls, and PostgreSQL are not part of this release.
