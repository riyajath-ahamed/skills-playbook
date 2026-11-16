#!/usr/bin/env python3
"""Write .cursor/mcp.json for the local connectors. The file contains no secrets."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "mcp-servers"))

from common.env import find_root
from common.manifest import cursor_config, venv_python


def generate(root: Path, python: Path | None = None) -> Path:
    interpreter = (python or venv_python(root)).absolute()
    if not interpreter.is_file():
        raise FileNotFoundError(
            "missing .venv/bin/python. Create it with: "
            "python3 -m venv .venv && .venv/bin/pip install -r mcp-servers/requirements.txt"
        )
    destination = root / ".cursor" / "mcp.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Keep the venv path. resolve() would follow the interpreter symlink and drop the venv.
    payload = cursor_config(root, interpreter)
    destination.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return destination


def main(argv: list[str]) -> int:
    del argv
    root = find_root()
    try:
        path = generate(root)
    except FileNotFoundError as exc:
        print(exc, file=sys.stderr)
        return 1
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
