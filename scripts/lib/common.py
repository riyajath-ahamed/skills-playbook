"""Shared parsing helpers for repository validators."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT_MARKERS = ("AGENTS.md", "mcp/catalog.yaml")


def fail(message: str) -> None:
    print(message, file=sys.stderr)


def require_yaml() -> None:
    if yaml is None:  # pragma: no cover - import would have failed first
        fail("PyYAML is required. Install it with: python3 -m pip install PyYAML")
        raise SystemExit(1)


def find_root(start: Path) -> Path:
    current = start.resolve()
    for candidate in [current, *current.parents]:
        if all((candidate / marker).exists() for marker in ROOT_MARKERS):
            return candidate
    fail(f"repository root not found from {start}")
    raise SystemExit(1)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def split_frontmatter(text: str) -> tuple[dict | None, str, str | None]:
    """Return frontmatter, body, and an error message."""
    if not text.startswith("---\n"):
        return None, text, "missing YAML frontmatter"
    end = text.find("\n---\n", 4)
    if end == -1:
        return None, text, "frontmatter is not closed with ---"
    raw = text[4:end]
    body = text[end + 5 :]
    try:
        loaded = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        return None, body, f"frontmatter YAML is invalid: {exc}"
    if not isinstance(loaded, dict):
        return None, body, "frontmatter must be a mapping"
    return loaded, body, None


def heading_set(body: str) -> set[str]:
    found = set()
    for line in body.splitlines():
        if line.startswith("## "):
            found.add(line[3:].strip())
    return found


def relative_markdown_links(body: str) -> list[tuple[int, str]]:
    """Return line numbers and link targets, skipping fenced code and URLs."""
    links: list[tuple[int, str]] = []
    in_fence = False
    for number, line in enumerate(body.splitlines(), start=1):
        stripped = line.lstrip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        cursor = 0
        while True:
            start = line.find("](", cursor)
            if start == -1:
                break
            if start > 0 and line[start - 1] == "!":
                cursor = start + 2
                continue
            end = line.find(")", start + 2)
            if end == -1:
                break
            target = line[start + 2 : end].strip()
            if target and not target.startswith(("http://", "https://", "mailto:")):
                links.append((number, target))
            cursor = end + 1
    return links


def resolve_link(source: Path, target: str, root: Path) -> tuple[Path | None, str | None, str | None]:
    """Return file path, anchor, and error."""
    target = target.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    if " " in target:
        target = target.split(" ", 1)[0]
    if target.startswith(("#",)):
        return source, target[1:], None
    path_part, anchor = (target.split("#", 1) + [None])[:2] if "#" in target else (target, None)
    if path_part.startswith("/"):
        return None, anchor, "absolute path"
    candidate = (source.parent / path_part).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None, anchor, "path escapes the repository"
    return candidate, anchor, None
