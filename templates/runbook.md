---
title: "Runbook: <Operation>"
description: "<When an operator uses this runbook>"
type: runbook
domain: platform-engineering
status: draft
tags:
  - runbook
related:
  - incident-report.md
---

# Triggers

- Alerts, symptoms, or requests that make this the right procedure.

# Preconditions

- Access, environment, and approvals required before starting.
- How to confirm the target environment.

# Procedure

1. Confirm the blast radius and the rollback path.
2. Perform the change.
3. Check the signal that shows the change worked.

# Verification

- Command, query, or user-visible check.
- Expected result.

# Rollback

1. Condition that requires rollback.
2. Steps that return the system to the previous state.
3. Check that the rollback worked.

# Escalation

- When to stop.
- Who can approve a production or destructive step.
