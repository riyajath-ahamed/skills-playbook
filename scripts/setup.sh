#!/usr/bin/env bash
# Report required and optional local prerequisites. Does not install packages.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
missing=0

check_required() {
  local name="$1"
  shift
  if "$@" >/dev/null 2>&1; then
    echo "[ok] $name"
  else
    echo "[missing] $name (required)"
    missing=1
  fi
}

check_optional() {
  local name="$1"
  shift
  if "$@" >/dev/null 2>&1; then
    echo "[ok] $name"
  else
    echo "[missing] $name (optional)"
  fi
}

check_required "git" git --version
check_required "python3" python3 --version
check_required "PyYAML" python3 -c "import yaml"
check_required "go" go version
check_optional "node" node --version
check_optional "docker" docker --version
check_optional "uv" uv --version

if [[ -f "$ROOT/AGENTS.md" && -f "$ROOT/mcp/catalog.yaml" ]]; then
  echo "[ok] repository root $ROOT"
else
  echo "[missing] repository root markers"
  missing=1
fi

exit "$missing"
