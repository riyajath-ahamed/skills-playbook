"""Load the repository .env without printing values."""

from __future__ import annotations

import os
from pathlib import Path

SECRET_MARKERS = ("TOKEN", "SECRET", "PASSWORD", "API_KEY", "ACCESS_TOKEN")


def find_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / "mcp" / "catalog.yaml").is_file():
            return candidate
    raise FileNotFoundError("repository root not found")


def parse_env(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        if key:
            values[key] = value
    return values


def read_env(root: Path) -> dict[str, str]:
    path = root / ".env"
    file_values = parse_env(path.read_text(encoding="utf-8")) if path.is_file() else {}
    merged = dict(file_values)
    merged.update({key: value for key, value in os.environ.items() if value})
    return merged


def load_env(root: Path | None = None) -> Path:
    repo = root or find_root()
    path = repo / ".env"
    if path.is_file():
        for key, value in parse_env(path.read_text(encoding="utf-8")).items():
            if not os.environ.get(key):
                os.environ[key] = value
    return repo


def redact(text: str, env: dict[str, str] | None = None) -> str:
    source = env if env is not None else os.environ
    redacted = text
    for key, value in source.items():
        if not value or len(value) < 8:
            continue
        if any(marker in key.upper() for marker in SECRET_MARKERS):
            redacted = redacted.replace(value, "[redacted]")
    return redacted
