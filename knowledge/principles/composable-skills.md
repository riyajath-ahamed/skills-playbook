---
title: Composable skills
type: principle
domain: agentic-systems
status: active
id: principle.composable-skills
tags:
  - skills
  - workflows
---

# Rule

- A skill does one job and names when it should be refused.
- A workflow composes skills. It does not copy their procedures.
- Shared rules live in `standards/` and `knowledge/`. Skills link to them.
- One agent executes a workflow unless a documented split produces independent evidence.

# Application

- Adding a skill requires frontmatter and the sections in [skill metadata](../../standards/skills/metadata.md).
- A workflow step names an existing skill. The platform planner reads that graph. It does not launch agents.
