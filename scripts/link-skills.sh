#!/usr/bin/env bash
# Print or create symlinks from a host skill directory to canonical skills.
# Default is a dry run. --apply writes links only under the requested target.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APPLY=0
TARGET=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --apply)
      APPLY=1
      shift
      ;;
    --target)
      TARGET="${2:-}"
      shift 2
      ;;
    *)
      echo "unknown argument: $1" >&2
      echo "usage: scripts/link-skills.sh [--apply --target DIR]" >&2
      exit 2
      ;;
  esac
done

if [[ "$APPLY" -eq 1 && -z "$TARGET" ]]; then
  echo "--apply requires --target" >&2
  exit 2
fi

if [[ "$APPLY" -eq 0 ]]; then
  echo "Dry run. Re-run with --apply --target <dir> to create symlinks."
fi

while IFS= read -r skill; do
  name="$(basename "$(dirname "$skill")")"
  if [[ "$APPLY" -eq 1 ]]; then
    mkdir -p "$TARGET"
    ln -sfn "$(dirname "$skill")" "$TARGET/$name"
    echo "linked $TARGET/$name"
  else
    echo "$name -> $skill"
  fi
done < <(find "$ROOT/skills" -name SKILL.md | sort)
