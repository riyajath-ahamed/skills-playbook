---
name: ui-architecture
description: >
  Structure a user interface around ownership of state, routing, and view
  boundaries. Use when adding a screen flow or reorganizing a frontend.
metadata:
  version: "1.0.0"
  domain: application-engineering
  risk: medium
---

# UI Architecture

## When to use

- A new multi-screen flow needs a place for state, data loading, and navigation.
- Shared UI state is being read by several routes and the owner is unclear.
- A frontend is about to gain a second source of truth for the same data.

## When not to use

- The task is a single-component visual tweak with no state or routing change.
- The task is an accessibility pass on an existing flow. Use `accessibility-review`.
- The task is a performance investigation. Use `performance-audit`.

## Inputs

- The user tasks and the routes or views that support them.
- The server data those views read and who is allowed to change it.
- Existing components and design-system constraints.
- Loading, empty, and error conditions the user can hit.

## Procedure

1. List the user tasks and the view that completes each one.
2. Assign each piece of client state an owner. Server data stays owned by the server contract.
3. Define how a view loads, fails, and recovers. Include the empty state.
4. Keep route and persistent state inspectable. Avoid hiding the source of a displayed value.
5. Reuse an existing design-system component before adding a local one.
6. Identify cross-route behavior that must stay consistent when shared state changes.
7. Note responsive behavior only where the layout change affects the task.
8. Defer a new frontend framework unless the current one blocks the requirement.

## Outputs

- View and state ownership table.
- Loading, empty, and error behavior for each primary task.
- Components that should be reused and components that need to be added.

## Verification

- Every displayed server value has a source and an error path.
- Shared state has one writer path.
- The note does not claim the UI was exercised unless a browser or equivalent check ran.

## Safety

- Do not collect personal data the task does not require.
- Do not put tokens or secrets in client-visible state, URLs, or storage.
- Keep authorization on the server. A hidden control is not an access boundary.
