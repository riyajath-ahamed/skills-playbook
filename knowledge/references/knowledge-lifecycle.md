---
title: Knowledge lifecycle
type: concept
domain: documentation
status: active
id: reference.knowledge-lifecycle
tags:
  - knowledge
  - index
related:
  - ../architecture-decisions/0003-git-canonical-derived-index.md
---

# Add

- Put the document in the `knowledge/` directory that matches its type.
- Add frontmatter. Set `id` when the file should keep its identity if it moves.
- Status starts at `draft` until a reviewer checks the claims. Principles and ADRs in this repository are `active` only after that review in Git.

# Review

- Check claims against the source the document cites.
- Run `scripts/check-links.sh` and rebuild the index with `scripts/build-index.sh`.
- Do not edit `.eit/index.json` by hand.

# Deprecate

- Set `status: deprecated` and say which document replaces the guidance.
- Leave the file in Git so older links still resolve.

# Supersede

- Set `status: superseded` and `superseded_by` on the old document.
- Set `supersedes` on the new document.
- Search results may include superseded documents. Callers must show `status` and must not present a superseded page as current guidance.

# Retrieval

- Keyword search reads the canonical files.
- The derived index stores `id`, `path`, `type`, `domain`, `tags`, `status`, and `source_revision`.
- A result that cannot name its path is not returned.
- Semantic retrieval with PostgreSQL and `pgvector` is specified in [retrieval](../../spec/architecture/retrieval.md) and is not deployed.
