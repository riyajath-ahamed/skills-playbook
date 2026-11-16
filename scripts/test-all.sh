#!/usr/bin/env bash
# Run repository validators, rubric calibration, the Python tests, and the Go test suite.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -x "$ROOT/.venv/bin/python3" ]]; then
  export PATH="$ROOT/.venv/bin:$PATH"
fi

if ! python3 -c "import httpx, mcp, yaml" >/dev/null 2>&1; then
  echo "Python test dependencies are missing. Install them with: python3 -m pip install -r mcp-servers/requirements.txt" >&2
  exit 1
fi

"$ROOT/scripts/validate-skills.sh" --self-test
"$ROOT/scripts/validate-catalog.sh" --self-test
"$ROOT/scripts/validate-skills.sh"
"$ROOT/scripts/validate-catalog.sh"
"$ROOT/scripts/check-links.sh"
"$ROOT/scripts/validate-evals.sh"
"$ROOT/scripts/run-skill-evals.sh" self-test
"$ROOT/scripts/build-index.sh"

python3 -m unittest discover -s "$ROOT/mcp-servers/tests"
python3 -m unittest discover -s "$ROOT/scripts/tests"

if command -v go >/dev/null 2>&1; then
  (cd "$ROOT/platform" && go test ./... && go vet ./...)
else
  echo "go is not installed; platform tests were not run" >&2
  exit 1
fi
