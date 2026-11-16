---
title: Retrieval design
type: architecture
domain: research
status: active
id: spec.architecture.retrieval
tags:
  - search
  - postgresql
---

# Implemented

- Canonical files stay in Git.
- Keyword search requires every query term to appear in the document.
- Ranking prefers title matches, then body matches, then path order.
- The derived index records `id`, `path`, `type`, `domain`, `tags`, `status`, and `source_revision`.
- Results without a path are not returned.

# Later PostgreSQL shape

| Store | Role |
|---|---|
| Document table | Id, path, type, domain, status, revision, tags, body |
| `tsvector` column | Full-text search |
| `pgvector` column | Added only after a measured set of paraphrase queries fails keyword search |

# Rules that stay

- Rebuild from Git. Do not edit the index in place.
- Show status, including `deprecated` and `superseded`.
- Do not generate a citation for a document that was not retrieved.
- Apply the caller's access rules before returning a restricted document. The first release has no restricted corpus.
