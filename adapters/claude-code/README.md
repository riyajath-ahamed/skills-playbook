# Claude Code adapter

Claude Code skills use `SKILL.md` with `name` and `description`. Toolkit skills already include those fields, so the body and `metadata` block can stay as written.

Claude Code loads skills from its own skill directories, not from this repository's `skills/` tree, until you add a skill there. Copying a skill duplicates it. Prefer a symlink that points back at the canonical `SKILL.md`, and make changes only in `skills/`.

`scripts/link-skills.sh` prints that mapping. It writes links only when `--apply` and `--target` are set.

This adapter does not install Claude Code or register an MCP server. Use `mcp/setup-guides/` and the host's `claude mcp add` flow when a guide names that command.
