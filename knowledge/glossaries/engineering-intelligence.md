---
title: Engineering intelligence glossary
type: glossary
domain: agentic-systems
status: active
id: glossary.engineering-intelligence
tags:
  - glossary
  - canonical-source-revision
---

# Terms

| Term | Meaning |
|---|---|
| Skill | A portable procedure in `skills/<domain>/<name>/SKILL.md`. |
| Workflow | An ordered composition of skills in `workflows/<name>/WORKFLOW.md`. |
| Canonical source | A Git-tracked Markdown or YAML file. Search indexes are derived from it. |
| Canonical source revision | The Git revision recorded on a derived index document. The index is discarded and rebuilt rather than edited. |
| Profile | A permission policy in `mcp/policies/`. |
| Run | A future execution of a workflow. The state machine exists. The agent executor does not. |
| Evidence | A path, command result, or source recorded for a claim. It is not a secret payload. |
