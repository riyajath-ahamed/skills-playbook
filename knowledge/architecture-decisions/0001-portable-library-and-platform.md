---
title: "ADR-0001: Portable library plus a platform that consumes it"
description: "Skills and workflows stay canonical in Git. The platform discovers them instead of keeping a second copy."
type: adr
domain: architecture
status: active
id: adr.0001
tags:
  - architecture
---

# Status

Accepted.

# Context

- The same procedures need to work in more than one coding-agent host.
- A standalone platform is a later product, and building it by copying prompts would fork the library.
- Hosts disagree on where skill files live and which metadata they read.

# Decision

The project will keep portable skills, workflows, standards, and knowledge as the canonical library. The Go platform will discover those files. Host-specific mapping lives only in `adapters/`.

# Consequences

- A skill change is made once, under `skills/`.
- The platform cannot assume a host has loaded a skill until that host's adapter steps are followed.
- Features that need a running service stay behind interfaces until they exist.

# Confirmation

- `ei skills list` and `ei workflows list` report the files in this repository.
- Adapter documents do not contain a second copy of a skill procedure.
