---
name: incident-to-root-cause
description: >
  Move from an incident signal to a confirmed cause, a mitigation, and a
  durable report. Use during or immediately after an operational failure.
execution: sequential
multi_agent: optional
skills:
  - debugging
  - source-verification
  - observability-design
  - runbook-authoring
---

# Incident to Root Cause

## Purpose

Establish what failed, what evidence supports the cause, and what operators should do next time.

## Activation

- Users or operators are affected, or an alert says a critical path failed.
- The cause is not already confirmed.
- A person is accountable for mitigation in the affected environment.

## Inputs

- Impact, start time, and the environment.
- Alerts, logs, traces, or user reports already collected.
- The change window that preceded the impact.

## Steps

### 1. Isolate the failure
- Depends on: none
- Skill: debugging
- Produces: reproduction or a narrowed path, plus the evidence collected

### 2. Check external explanations
- Depends on: narrowed path
- Skill: source-verification
- Produces: confirmation or rejection of a vendor or dependency claim used as the cause

### 3. Close evidence gaps
- Depends on: isolation
- Skill: observability-design
- Produces: the signal that was missing and whether it is specified or implemented

### 4. Leave an operator procedure
- Depends on: mitigation known
- Skill: runbook-authoring
- Produces: runbook updates and an incident report from the incident template

## Outputs

- Timeline and impact.
- Cause labeled confirmed or hypothesis.
- Mitigation and rollback state.
- Runbook or incident report, including follow-up.

## Verification

- The stated cause predicts the evidence already collected.
- Mitigation is checked against the original symptom.
- The report separates confirmed facts from hypotheses.

## Failure handling

- If the failure cannot be reproduced outside production, collect read-only evidence and stop before any destructive diagnostic.
- Do not retry a mitigation that already failed unless a condition changed.
- If the cause stays a hypothesis, publish it as a hypothesis and name the missing evidence.

## Approval gates

- Production reads beyond the incident's existing authorization require the incident owner.
- Restart, rollback, data repair, and any destructive action require explicit approval.
- External status communication requires the owner designated for communication.

## Completion

The workflow is complete when impact, evidence, and either a confirmed cause or a labeled hypothesis are recorded, and follow-up owners are named.

## Multi-agent strategy

A coordinator may assign independent read-only evidence collection, such as one person on recent changes and one on an external status page. Writers of the mitigation stay singular. `ei` does not launch these workers. One responder is the default.
