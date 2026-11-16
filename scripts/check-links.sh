#!/usr/bin/env bash
# Check internal relative links. Network access is not required.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if ! python3 -c "import yaml" >/dev/null 2>&1; then
  echo "PyYAML is required. Install it with: python3 -m pip install PyYAML" >&2
  exit 1
fi

exec python3 "$ROOT/scripts/lib/check_links.py" --root "$ROOT" "$@"
