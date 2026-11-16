---
title: Local keyword search
type: research
domain: research
status: active
id: research.local-keyword-search
tags:
  - search
last_verified: "2026-10-30"
---

# Current method

- `ei knowledge search` scans Markdown under the repository and ranks documents that contain every query term.
- Title matches count more than body matches. Ties break by path.
- `scripts/build-index.sh` writes the same documents to `.eit/index.json` for rebuilds. Search does not require that file.

# Why this is enough

- The first corpus is the toolkit itself. Exact terms such as skill names and document ids are the common queries.
- A vector index needs an embedding path, a database, and a quality comparison that this release has not measured.

# Limit

- Paraphrase queries can miss a relevant page. That gap is the trigger to evaluate hybrid retrieval, not a reason to invent a citation.
