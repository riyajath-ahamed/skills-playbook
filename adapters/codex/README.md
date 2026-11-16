# Codex adapter

Codex reads project guidance from `AGENTS.md` and can load skills whose frontmatter contains `name` and `description`. Toolkit `metadata` is additional and is not required by Codex.

Place a skill where the Codex installation discovers project skills, using a symlink to the canonical file. Follow the current Codex skill-discovery docs for that path. This repository does not claim a particular global directory is active on every machine.

Workflows stay in `workflows/`. Codex does not execute `WORKFLOW.md` as a native workflow engine. A person or one Codex session follows the steps.

MCP servers are configured in Codex's own configuration. Translate a catalog entry. Do not point Codex at `mcp/catalog.yaml` as if it were that configuration.
