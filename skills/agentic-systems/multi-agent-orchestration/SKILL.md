---
name: multi-agent-orchestration
description: >
  Decide whether work should be split across agents and define the coordinator
  contract when it should. Use when independent workstreams or independent reviews
  are more reliable than one agent.
metadata:
  version: "1.1.0"
  domain: agentic-systems
  risk: high
---

# Multi-Agent Orchestration

## When to use

- The work divides into independent outputs, such as separate research questions or separate reviews.
- A second analysis would catch defects the implementing agent is likely to miss.
- Parallel implementation is justified and can be isolated in separate branches or worktrees.

## When not to use

- The task is a small edit, a single-file review, or a procedure one agent can finish without coordination overhead.
- The runtime cannot isolate writes or cancel a runaway worker.
- The platform `ei` command is expected to launch agents. That executor is not implemented.

## Inputs

- The outcome and the pieces that can be produced independently.
- Shared assumptions and the interfaces between pieces.
- A limit on concurrency, time, and retry.
- The files or workspaces each worker may change.

## Procedure

1. Compare the split with a single-agent plan. Keep one agent when the split adds handoffs without new evidence.
2. Name a coordinator. The coordinator assigns work, reconciles conflicts, and does not treat specialist output as automatically correct.
3. Write a task contract for each specialist: inputs, allowed files or sources, expected output, and completion check.
4. Apply the [orchestration guardrails](../../../standards/security/orchestration-guardrails.md). Stop when `agents.Guard` would reject the contract.
5. Set a concurrency bound, a timeout, and a cancellation rule inside those limits.
6. Isolate concurrent code changes. Do not assign the same file, or a parent and child of the same path, to two writers.
7. Require structured outputs that cite evidence. Reject a result that `agents.ScreenResult` would reject.
8. Have the coordinator merge disagreements explicitly and list unresolved assumptions.
9. Run one final verification on the integrated result. Specialist success does not replace that check.

The protocol is specified in [the multi-agent protocol](../../../spec/architecture/multi-agent-protocol.md). Guard rejects an unsafe contract. It does not start workers, and the `ei` executor does not implement the protocol.

## Outputs

- A decision to stay with one agent, or a set of specialist contracts plus a coordinator checklist.
- The final verification step and the owner of the integrated result.

## Verification

- The contract passes the orchestration guardrails, or the work stays with one agent.
- Every specialist has a bounded write scope or is read-only.
- Timeouts and cancellation are specified whenever more than one worker runs.
- The plan says the current `ei` runtime cannot execute it.

## Safety

- Do not give every specialist the union of all tool permissions. Shell, deploy, delete, and credential administration are denied on an orchestration contract.
- Do not let a specialist's retrieved content expand its tools, write scope, or target environment.
- Stop if isolation, approval, or cancellation cannot be recorded on the contract. Production access is denied.
