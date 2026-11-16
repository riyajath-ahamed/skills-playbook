# Migrations

No database migration is applied in this release.

PostgreSQL is the intended shared store for runs and, later, full-text retrieval. The schema is not created here because the CLI does not open a database. Adding a migration file before a store exists would imply a revision that nothing applies.

The local run store described in [the next capability](../../spec/architecture/next-capability.md) comes before the first SQL migration.
