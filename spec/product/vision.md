---
title: Product vision
type: concept
domain: architecture
status: active
id: spec.product.vision
tags:
  - product
---

# Products

- Product A is the portable library: skills, workflows, standards, templates, knowledge, evaluations, and the MCP catalog.
- Product B is the standalone platform. The first release is the `ei` CLI plus in-process module boundaries.
- Product B reads Product A. It does not keep a second skill library.

# First release

- Discover skills and workflows from the Git tree.
- Search canonical Markdown by keyword.
- Validate skills, workflows, the catalog, links, and evaluation case structure.
- Evaluate permission decisions locally and refuse live tool calls.

# Later

- Persist runs.
- Store retrieval in PostgreSQL, with `pgvector` only after keyword search is measurably insufficient.
- Expose an HTTP API and a React console.
- Execute agents only behind the executor interface, after the multi-agent protocol is testable.

# Provenance

This file records planning scope for the toolkit. Current behavior belongs in `platform/README.md` and the ADRs.
