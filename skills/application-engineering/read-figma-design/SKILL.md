---
name: read-figma-design
description: >
  Read a Figma file or frame through the figma-mcp connector. Use when an
  implementation task needs the structure of a design.
metadata:
  version: "1.0.0"
  domain: application-engineering
  risk: medium
  tools:
    - get_file
    - get_frame
---

# Read Figma Design

## When to use

- The task includes a Figma file key, file URL, or frame node id.
- A Jira issue result lists a Figma link to open.

## When not to use

- The task is to change the Figma file. This connector is read-only.
- The task is a code review with no design link. Use `code-review`.

## Inputs

- The Figma file key or URL.
- The node id when the task names one frame.

## Procedure

1. Call `get_file` on `figma-mcp` for a whole file.
2. Call `get_frame` on `figma-mcp` when the task names a node id.
3. Use the flattened name, type, and children as the design structure.
4. Stop if the connector returns that `FIGMA_ACCESS_TOKEN` is not set.

## Outputs

- The file name and the flattened node tree.

## Verification

- The summary uses names returned by the connector.
- The skill output does not claim a Figma file was edited.

## Safety

- Do not paste more of the design into a prompt than the task needs.
- Do not copy the Figma token into the skill output, a log, or Git.
