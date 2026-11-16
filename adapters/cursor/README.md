# Cursor adapter

Cursor project skills live under `.cursor/skills/<name>/SKILL.md` and require `name` and `description`. Toolkit skills use the same two fields. `metadata` is for this repository's validator and can remain in the file.

Skills in `skills/` are not loaded by Cursor automatically. Link one only when you want that host to discover it:

```bash
scripts/link-skills.sh
scripts/link-skills.sh --apply --target .cursor/skills
```

The default command prints the mapping and writes nothing. Local skill links under `.cursor/skills/` are gitignored.

The project Cursor connector is `.cursor/mcp.json`. `make mcp-config` writes it from [the manifest](../../config/mcpctl-manifest.yaml). It holds absolute paths to the local checkout, so it is gitignored and each clone generates its own. Each entry is stdio, the `.venv` Python, and one `server.py`. The file names no tokens. The servers load `.env`. `mcp/catalog.yaml` is not valid Cursor MCP configuration.

This adapter does not assert that any MCP server in the catalog is enabled in the current Cursor session.
