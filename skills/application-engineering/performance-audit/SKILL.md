---
name: performance-audit
description: >
  Find a performance or cost problem from measured evidence and a testable
  hypothesis. Use when latency, throughput, or resource use is outside its target.
metadata:
  version: "1.0.0"
  domain: application-engineering
  risk: medium
---

# Performance Audit

## When to use

- A user path or job misses a stated latency, throughput, or cost target.
- A change made a measured path slower and the cause is not identified.
- Capacity planning needs evidence rather than a guess.

## When not to use

- There is no baseline and no target. Establish the target before optimizing.
- The system is failing correctness checks. Fix correctness first.
- The request is to generate load against production without approval.

## Inputs

- The path or query and the target.
- A baseline measurement: where, when, and under what load.
- Recent changes that could explain a regression.
- The environment the measurement came from.

## Procedure

1. Restate the target and confirm the baseline is comparable to the current measurement.
2. Break the path into segments. Measure before changing anything.
3. Form one hypothesis that predicts a specific hotspot.
4. Test that hypothesis with a profile, query plan, or timing span. Discard it if the evidence disagrees.
5. Change the smallest responsible part. Avoid optimizations that hide a product bug.
6. Re-measure the same way as the baseline.
7. Record the residual limit and the next measurement that would reopen the conclusion.
8. Separate development measurements from production measurements. Do not extrapolate silently.

## Outputs

- Baseline, target, and environment.
- Hypothesis, evidence, and whether it held.
- Change and the measurement after it, or a blocked reason.

## Verification

- The conclusion cites a measurement, not only a code reading.
- The before and after methods match closely enough to compare.
- The report does not claim a production improvement from a local sample unless that limit is stated.

## Safety

- Do not run a load test against production without explicit authorization and a blast-radius limit.
- Do not log request or response bodies that contain personal data in order to time them.
- Stop if measurement requires a broader credential than read-only diagnostics.
