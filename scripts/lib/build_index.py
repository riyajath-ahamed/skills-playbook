"""Rebuild the derived local search index from canonical files."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from common import find_root, read_text, split_frontmatter

INCLUDE_PREFIXES = (
    "skills",
    "workflows",
    "knowledge",
    "standards",
    "templates",
    "spec",
    "mcp",
    "adapters",
    "platform",
)


def revision(root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return "unknown"
    value = result.stdout.strip()
    return value or "unknown"


def title_from(path: Path, meta: dict | None, body: str) -> str:
    if meta and isinstance(meta.get("title"), str):
        return meta["title"]
    if meta and isinstance(meta.get("name"), str):
        return meta["name"]
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem


def document_id(path: Path, root: Path, meta: dict | None) -> str:
    if meta and isinstance(meta.get("id"), str) and meta["id"].strip():
        return meta["id"].strip()
    relative = path.relative_to(root).as_posix()
    return "path." + relative.lower().replace("/", ".").replace(" ", "-")


def collect(root: Path) -> list[dict]:
    source_revision = revision(root)
    documents = []
    for path in sorted(root.rglob("*.md")):
        relative = path.relative_to(root).as_posix()
        if not relative.startswith(INCLUDE_PREFIXES):
            continue
        if any(part.startswith(".") for part in path.parts):
            continue
        meta, body, _problem = split_frontmatter(read_text(path))
        tags = []
        if meta and isinstance(meta.get("tags"), list):
            tags = [item for item in meta["tags"] if isinstance(item, str)]
        documents.append(
            {
                "id": document_id(path, root, meta),
                "path": relative,
                "type": (meta or {}).get("type") or path.parent.name,
                "domain": (meta or {}).get("domain") or "",
                "title": title_from(path, meta, body),
                "tags": tags,
                "status": (meta or {}).get("status") or "active",
                "source_revision": source_revision,
            }
        )
    documents.sort(key=lambda item: item["id"])
    return documents


def build(root: Path) -> Path:
    destination = root / ".eit" / "index.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 1,
        "generator": "scripts/build-index.sh",
        "documents": collect(root),
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    destination.write_text(rendered, encoding="utf-8")
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the derived knowledge index")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    root = find_root(args.root)
    before = {path: path.read_bytes() for path in root.rglob("*.md") if ".git" not in path.parts}
    destination = build(root)
    after = {path: path.read_bytes() for path in before}
    if before != after:
        raise SystemExit("index builder modified a canonical file")
    count = json.loads(destination.read_text(encoding="utf-8"))["documents"]
    print(f"wrote {destination.relative_to(root)} with {len(count)} documents")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
