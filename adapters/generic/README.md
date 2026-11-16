# Generic adapter

The canonical skill file is `skills/<domain>/<name>/SKILL.md`.

Required host-facing fields are `name` and `description`. Additional keys under `metadata` are toolkit fields. Hosts that ignore unknown YAML keys can read the file unchanged.

A host that only discovers skills in its own directory needs a copy or a link. Keep edits in `skills/`. Do not fork the procedure into the host directory.

Workflows are `workflows/<name>/WORKFLOW.md`. They are procedures for one agent unless `multi_agent` is `optional` and the host can actually isolate workers. The toolkit CLI does not launch those workers.
