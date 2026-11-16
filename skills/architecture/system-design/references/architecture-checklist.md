---
title: Architecture checklist
type: standard
domain: architecture
status: active
id: skill.system-design.checklist
tags:
  - architecture
  - review
---

# Boundaries

- Each component has one responsibility and a named data owner.
- External dependencies have a failure mode and a timeout or equivalent limit.
- Proposed components are distinguished from components that already exist.

# Quality

- Availability, recovery, and degraded behavior are stated for the critical path.
- Security boundaries and authorization are stated where data crosses a trust line.
- Capacity and cost assumptions are explicit.
- Operational signals needed to run the design are named.

# Decision quality

- At least one credible alternative is compared on the same criteria.
- Irreversible choices point to an ADR.
- Open questions name the evidence that would close them.
