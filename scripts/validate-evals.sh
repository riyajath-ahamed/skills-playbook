#!/usr/bin/env bash
# Validate evaluation-case structure and deterministic safety checks.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if ! python3 -c "import yaml" >/dev/null 2>&1; then
  echo "PyYAML is required. Install it with: python3 -m pip install PyYAML" >&2
  exit 1
fi

exec python3 "$ROOT/scripts/lib/validate_evals.py" --root "$ROOT" "$@"
