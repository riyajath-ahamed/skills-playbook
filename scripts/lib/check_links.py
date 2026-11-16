"""Check internal Markdown links and relative frontmatter references."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from common import find_root, read_text, relative_markdown_links, resolve_link, split_frontmatter

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*$")
SKIP_DIRS = {".git", ".eit", "node_modules"}


def slug(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text


def anchors(path: Path) -> set[str]:
    counts: dict[str, int] = {}
    found: set[str] = set()
    in_fence = False
    for line in read_text(path).splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = HEADING_RE.match(line.strip())
        if not match:
            continue
        base = slug(match.group(2))
        count = counts.get(base, 0)
        counts[base] = count + 1
        found.add(base if count == 0 else f"{base}-{count}")
    return found


def iter_markdown(root: Path) -> list[Path]:
    files = []
    for path in root.rglob("*.md"):
        if any(part in SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        files.append(path)
    return sorted(files)


def check_related(path: Path, root: Path, errors: list[str]) -> None:
    meta, _body, problem = split_frontmatter(read_text(path))
    if problem or not meta:
        return
    related = meta.get("related")
    if not isinstance(related, list):
        return
    for item in related:
        if not isinstance(item, str) or "<" in item or ">" in item:
            continue
        candidate, _anchor, link_problem = resolve_link(path, item, root)
        if link_problem or candidate is None or not candidate.exists():
            errors.append(f"{path}: broken related path {item}")


def run(root: Path) -> list[str]:
    errors: list[str] = []
    files = iter_markdown(root)
    cache: dict[Path, set[str]] = {}
    for path in files:
        check_related(path, root, errors)
        for line, target in relative_markdown_links(read_text(path)):
            candidate, anchor, problem = resolve_link(path, target, root)
            if problem or candidate is None:
                errors.append(f"{path}:{line}: broken link {target} ({problem or 'unresolved'})")
                continue
            if not candidate.exists():
                errors.append(f"{path}:{line}: broken link {target}")
                continue
            if anchor:
                if candidate.suffix != ".md":
                    errors.append(f"{path}:{line}: anchor on non-markdown file {target}")
                    continue
                if candidate not in cache:
                    cache[candidate] = anchors(candidate)
                if slug(anchor) not in cache[candidate] and anchor not in cache[candidate]:
                    errors.append(f"{path}:{line}: missing anchor #{anchor}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Check internal links")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    errors = run(find_root(args.root))
    if errors:
        for item in errors:
            print(item, file=sys.stderr)
        print(f"{len(errors)} broken link(s)", file=sys.stderr)
        return 1
    print("internal links resolved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
