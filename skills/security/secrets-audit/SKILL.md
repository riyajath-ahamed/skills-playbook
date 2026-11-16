---
name: secrets-audit
description: >
  Find credentials and secret material in a change or repository without
  revealing the secret values. Use before commit, review, or publication.
metadata:
  version: "1.0.0"
  domain: security
  risk: high
---

# Secrets Audit

## When to use

- A diff or repository may contain a token, key, password, or connection string.
- A catalog, example, or log snippet is about to be committed.
- An agent or script prints environment or configuration values.

## When not to use

- The task is to rotate a credential in production. That requires a separate authorized procedure.
- The task is to review tool permissions rather than stored secrets. Use `tool-permission-review`.
- A detector reports a known test fixture that is already documented as fake and non-reusable.

## Inputs

- The paths or diff to inspect.
- The patterns or detector available in the environment.
- A list of allowed placeholder formats, such as `${SECRET_NAME}` or a documented example value that cannot authenticate.

## Procedure

1. Search the scoped paths for private keys, cloud access keys, personal access tokens, bearer tokens, and connection strings with embedded passwords.
2. Inspect high-risk filenames such as `.env`, key files, and credential JSON. Do not print their contents.
3. When a match is a real secret, report the path, the field or line, and the secret type. Do not report the value or a unique prefix long enough to use.
4. When a match is a placeholder or a test vector, say why it is not usable.
5. Recommend removal from the tree and from history when a real secret was committed. Do not rewrite history unless the owner asks.
6. Recommend rotation by the owner. Do not rotate it yourself without authorization.
7. Check that logs and error examples redact the same classes of value.

## Outputs

- Findings with path, location, type, and whether the value was withheld.
- Recommended owner actions: remove, rotate, or dismiss as a placeholder.
- Detectors that were run and scopes that were not searched.

## Verification

- The report contains no usable secret material.
- A placeholder is not reported as a live credential without a reason.
- A dismissed finding explains why it cannot authenticate.

## Safety

- Do not copy the secret into the report, the chat summary, or a new file.
- Do not use a discovered credential to test whether it works.
- Do not broaden the search into an unrelated production secret store.
