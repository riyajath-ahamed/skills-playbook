---
title: Skill metadata
type: standard
domain: documentation
status: active
id: standard.skills.metadata
tags:
  - skills
  - metadata
---

# Required frontmatter

```yaml
name: skill-name
description: >
  What the skill does and when to use it.
metadata:
  version: "1.0.0"
  domain: architecture
  risk: low
```

| Field | Required | Rule |
|---|---|---|
| `name` | yes | Lowercase letters, digits, and hyphens. Unique. Matches the skill directory name. At most 64 characters. |
| `description` | yes | Non-empty and at most 1024 characters. States what the skill does and when to apply it. |
| `metadata.version` | yes | Quoted semantic version string. |
| `metadata.domain` | yes | One of `architecture`, `agentic-systems`, `platform-engineering`, `application-engineering`, `software-engineering`, `documentation`, `research`, `learning`, `security`. |
| `metadata.risk` | yes | One of `low`, `medium`, `high`, `critical`. |
| `metadata.status` | no | `active`, `draft`, or `deprecated`. Omitted means `active`. |
| `metadata.tools` | no | List of tool capability names. Listing a tool does not mean it is installed. |
| `metadata.outputs` | no | List of artifact types the procedure produces. |

# Required sections

- `When to use`
- `When not to use`
- `Inputs`
- `Procedure`
- `Outputs`
- `Verification`
- `Safety`

Additional sections are allowed. Canonical writing rules live in [writing guidelines](../documentation/writing-guidelines.md). Runtime mapping lives in `adapters/`.
