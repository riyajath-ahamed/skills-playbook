---
name: read-jira-issue
description: >
  Read a Jira issue through the jira-mcp connector. Use when a task starts
  from an issue key and later skills need its links.
metadata:
  version: "1.0.0"
  domain: agentic-systems
  risk: medium
  tools:
    - get_issue_details
    - get_issue_comments
---

# Read Jira Issue

## When to use

- The task names a Jira issue key.
- A later step needs the issue summary, status, or linked URLs.

## When not to use

- The task is to publish a Confluence page. Use `read-confluence-page` for a page read, and stop before any publish.
- The task is only a code review with no issue key. Use `code-review`.

## Inputs

- The Jira issue key.
- Whether comments are needed.

## Procedure

1. Call `get_issue_details` on `jira-mcp` with the issue key.
2. Keep `links`, `lucid_refs`, and `google_workspace_refs` from the result for later skills.
3. Call `get_issue_comments` on `jira-mcp` when the task depends on discussion on the issue.
4. Stop if the connector returns that `JIRA_BASE_URL` is not set.
5. Do not call `create_issues_batch` unless the user asked to create issues. A create stays a preview until `confirmed` is true and `JIRA_WRITE_ENABLED` is true.

## Outputs

- The issue key, summary, status, and description.
- Link lists for follow-up skills.
- Comments when they were requested.

## Verification

- The result cites the issue key returned by `get_issue_details`.
- No Jira write was sent unless both write gates were true.

## Safety

- Do not invent an issue body when the connector returns an error.
- Do not copy the API token into the skill output, a log, or Git.
