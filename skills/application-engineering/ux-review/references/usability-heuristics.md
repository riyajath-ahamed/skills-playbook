---
title: Usability heuristics
type: standard
domain: application-engineering
status: active
id: skill.ux-review.heuristics
tags:
  - ux
  - review
---

# Heuristic matrix

Rate each heuristic `Strong`, `Mixed`, `Weak`, or `Not observed` across the journeys that were walked. `Not observed` means no journey exercised it. It is not a pass.

| Id | Heuristic | Check |
|---|---|---|
| H1 | Visibility of system status | The page shows what is happening: loading, saved, empty, or error. |
| H2 | Match between system and the real world | Words and order follow the user's task, not internal system names. |
| H3 | User control and freedom | The user can undo, cancel, or go back without losing work. |
| H4 | Consistency and standards | The same action looks and behaves the same way across the journey. |
| H5 | Error prevention | The interface stops a likely mistake before it happens. |
| H6 | Recognition rather than recall | Options, labels, and recent context are visible instead of remembered. |
| H7 | Flexibility and efficiency of use | A repeat user has a shorter path that does not block a first-time user. |
| H8 | Aesthetic and minimalist design | The page focuses on the task instead of competing calls to action. |
| H9 | Help users recognize, diagnose, and recover from errors | An error says what went wrong and how to fix it in plain language. |
| H10 | Help and documentation | Help is findable at the moment of need and specific to the step. |

# Cognitive walkthrough

Ask these at each step. A "no" is a failure candidate. Cite the question number.

1. Will the user try to achieve the right effect at this step?
2. Will the user notice that the correct action is available?
3. Will the user associate that action with the effect they want?
4. After the action, will the user see progress toward the goal?

# Task success

Record per journey from the step log only.

| Measure | Values |
|---|---|
| Completed | `Yes`, `Partial`, or `No` |
| Steps | Actions taken against the ideal count in the approved plan |
| Backtracks | Returns to an earlier screen or undone actions |
| Errors | Visible error states, blocking failed requests, or wrong-path clicks |
| Dead ends | Steps with no obvious next action |

# Lenses

Judge the same evidence through the lenses the requester named. The default set is first-time user, returning power user, administrator, and narrow viewport. A finding names the lens it hurts. A lens with no evidence is `Not observed`.

# Severity

Severity applies to failures. A strength is labelled `Strength`.

| Level | Meaning |
|---|---|
| `Block` | The task cannot be finished on this path. |
| `Major` | The task finishes only after a significant detour, confusion, or a risk of data loss. |
| `Minor` | Friction with a clear workaround. |
| `Cosmetic` | Polish that does not change task success. |
