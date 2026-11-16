---
name: observability-design
description: >
  Define the logs, metrics, and traces needed to detect and diagnose failures.
  Use when a system or workflow needs operational signals.
metadata:
  version: "1.0.0"
  domain: platform-engineering
  risk: medium
---

# Observability Design

## When to use

- A new critical path has no agreed signal for failure.
- An incident was slow to diagnose because evidence was missing or noisy.
- A platform component needs a trace, metric, and log story that fits OpenTelemetry-compatible tooling later.

## When not to use

- The task is to debug one known failure with evidence already in hand. Use `debugging`.
- The task is to choose a vendor. Use `technology-evaluation` after the signals are known.
- The system has no defined critical path yet. Use `system-design` first.

## Inputs

- The user or operator outcome that matters.
- The components on that path.
- Existing signals and known gaps.
- Data that must not be recorded.

## Procedure

1. Define one or two service-level indicators for the critical outcome, including the event that counts as a failure.
2. Specify metrics that answer saturation, error rate, and latency. Avoid labels with unbounded values.
3. Specify structured logs for decisions a metric cannot explain. Name the correlation identifier.
4. Specify trace spans at process and external-call boundaries. Do not require a collector that is not deployed.
5. List fields that must be redacted: tokens, cookies, passwords, and unnecessary personal data.
6. Map each alert-worthy condition to an action. A signal with no action is a dashboard candidate, not a page.
7. State what is implemented now and what is a future OpenTelemetry export path.
8. For agent runs, record tool name, decision, and outcome. Do not record secret values or full untrusted payloads by default.

## Outputs

- A signal table: question, signal, source, and redaction rule.
- The correlation identifier used across logs and traces.
- Gaps between this design and the current implementation.

## Verification

- Each paged condition names the action an operator takes.
- High-cardinality identifiers are not metric labels.
- The design says whether export is implemented or only specified.

## Safety

- Do not enable verbose payload logging to make a review easier.
- Do not send production telemetry to an unapproved destination.
- Redact secrets before they reach a log, trace, or evaluation artifact.
