---
title: Documentation Writing Guidelines
type: standard
domain: documentation
status: active
applies_to:
  - reference-documentation
  - model-documentation
  - integration-documentation
  - api-documentation
  - engineering-context
---

# What to Write

## Writing Rules

### Do

- **Frontmatter first.** Put document metadata in YAML frontmatter, not in the body. Agents use frontmatter to decide whether to load the document.
- **One concept per file.** Document one model, integration, API resource, or architectural concept per file.
- **Prefer bullets.** Use bullets for facts, constraints, and procedures. Use paragraphs only when reasoning requires them, such as in ADRs.
- **Use tables for structured data.** Use tables for fields, relationships, endpoints, configuration, and SLAs.
- **Write direct statements.** State ownership and behavior explicitly.
- **Reference, don't repeat.** Link to the canonical file for facts documented elsewhere.
- **Make headings descriptive.** Each heading should communicate its section's main point.
- **Put decisions in ADRs.** ADRs own the rationale. Reference pages state the current outcome without recounting the decision process.

### Do Not

- Do not add introductory paragraphs that repeat the title or frontmatter.
- Do not explain self-evident field names.
- Do not include empty sections or `TBD` placeholders.
- Do not maintain version history in the document body. Use Git history.
- Do not include temporary task or sprint context in engineering reference documentation.
- Do not cite upstream planning sources, such as PRDs, Confluence pages, or tickets, in reference pages. Keep provenance in `spec/`.
- Do not narrate decision history or rejected alternatives in reference pages. Record reasoning in the relevant ADR.
- Do not duplicate facts maintained in another canonical document.

## Document Structure

- Begin with YAML frontmatter.
- Start the body with the first meaningful topic heading.
- Include only sections relevant to the concept.
- Use relative links to related canonical documents where possible.
- Keep reference pages focused on the current, verified system state.

## Source of Truth

- Reference documentation represents the current verified engineering state.
- ADRs contain architectural decisions and their rationale.
- Planning specifications in `spec/` contain planning context and source provenance.
- Git history records changes over time.
