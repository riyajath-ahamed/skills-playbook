---
title: "ADR-0003: Git is canonical and the index is derived"
description: "Search indexes are rebuildable artifacts. They are not the source of engineering knowledge."
type: adr
domain: documentation
status: active
id: adr.0003
tags:
  - knowledge
  - search
---

# Status

Accepted.

# Context

- Agents and people need to find skills and principles without reading every file.
- Embeddings and search indexes drift when they become editable sources.
- PostgreSQL full-text search and `pgvector` are the intended later store, and they are not required to search a small Git tree.

# Decision

The project will treat Git-tracked Markdown and YAML as canonical. `scripts/build-index.sh` rebuilds `.eit/index.json` from those files. The index is gitignored. Keyword search reads the files directly so a missing index cannot hide a document.

# Consequences

- Moving a document without an `id` changes its derived identifier.
- The index must not be edited to fix a bad search result. Fix the source and rebuild.
- A database-backed hybrid index is future work recorded in [retrieval](../../spec/architecture/retrieval.md).

# Confirmation

- Re-running the index builder produces the same document set for the same Git revision.
- Search results include repository paths.
