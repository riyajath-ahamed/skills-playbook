---
title: Workflow definition
type: standard
domain: documentation
status: active
id: standard.workflows.definition
tags:
  - workflows
---

# File location

Each workflow is `workflows/<name>/WORKFLOW.md`.

# Required frontmatter

| Field | Required | Rule |
|---|---|---|
| `name` | yes | Matches the directory name. |
| `description` | yes | States the outcome and when to start the workflow. |
| `execution` | yes | `sequential`. The library defaults to one agent. |
| `multi_agent` | no | `optional` or `disabled`. A workflow must not set `required`. |
| `skills` | yes | Skill names used by the steps. Every name must exist under `skills/`. |

# Required sections

- `Purpose`
- `Activation`
- `Inputs`
- `Steps`
- `Outputs`
- `Verification`
- `Failure handling`
- `Approval gates`
- `Completion`

# Step format

Each step names one existing skill:

```markdown
### 1. Frame the question
- Depends on: none
- Skill: technical-scouting
- Produces: research brief
```

# Execution rule

A workflow file is a procedure. Reading it does not start agents, call tools, or change systems. Multi-agent notes describe when parallel work is justified. They do not require a distributed runtime.
