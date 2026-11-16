# HTTP API

No HTTP server is implemented.

The future API should call the same in-process registry, planner, policy, and run packages as the CLI. It should not grow a second skill catalog or a second permission implementation.

[Platform boundaries](../../spec/architecture/platform-boundaries.md) name the packages a later server would use. This directory reserves that boundary.
