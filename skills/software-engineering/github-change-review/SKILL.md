---
name: github-change-review
description: >
  Read a GitHub pull request, its changed files and diff, a file, the commit
  list, or an issue search through the github-mcp connector. Use when a review
  needs the remote change.
metadata:
  version: "1.1.0"
  domain: software-engineering
  risk: medium
  tools:
    - get_pull_request
    - get_pull_request_files
    - get_file
    - list_commits
    - search_issues
---

# GitHub Change Review

## When to use

- A review names an owner, repository, and pull request number.
- The reviewer needs the changed files and diff, a file, the commit list, or an issue search from GitHub.

## When not to use

- The diff is already local and no GitHub record is required. Use `code-review`.
- The task is a SonarQube quality gate. Use `sonar-review`.

## Inputs

- The repository owner and name.
- The pull request number, file path, commit ref, or search query.

## Procedure

1. Call `get_pull_request` on `github-mcp` when the task names a pull request.
2. Call `get_pull_request_files` on `github-mcp` to get the changed paths and each file's diff. This is the change under review.
3. For each entry with `patch_omitted`, call `get_file` with the head branch from step 1 when that file matters to the review. Say which omitted files were not read.
4. Call `list_commits` on `github-mcp` when the review needs the commit subjects.
5. Call `get_file` on `github-mcp` for surrounding code that the diff alone cannot explain.
6. Call `search_issues` on `github-mcp` only for the query the task asked for.
7. Hand the returned fields to `code-review`. Do not reimplement the GitHub API.

## Outputs

- The pull request title, state, branches, and body when a pull request was read.
- The changed files with status, line counts, and diffs, and the files whose diff was omitted.
- Commit subjects, file metadata, or search hits that the task required.

## Verification

- Findings cite the pull request number or file path returned by the connector.
- The review does not describe a file as unchanged when its patch was omitted and not read.
- The skill output does not claim a merge, review submission, or file write.

## Safety

- These tools are reads. Do not send a write, merge, or permission change.
- Do not copy `GITHUB_PERSONAL_ACCESS_TOKEN` into the skill output, a log, or Git.
