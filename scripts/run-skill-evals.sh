#!/usr/bin/env bash
# Calibrate skill rubrics, or score skill outputs from a model command. See evals/fixtures/README.md.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if ! python3 -c "import yaml" >/dev/null 2>&1; then
  echo "PyYAML is required. Install it with: python3 -m pip install PyYAML" >&2
  exit 1
fi

exec python3 "$ROOT/scripts/lib/skill_evals.py" --root "$ROOT" "$@"
