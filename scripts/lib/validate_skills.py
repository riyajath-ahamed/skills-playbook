"""Validate skill and workflow definitions."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from common import find_root, heading_set, read_text, relative_markdown_links, resolve_link, split_frontmatter

DOMAINS = {
    "architecture",
    "agentic-systems",
    "platform-engineering",
    "application-engineering",
    "software-engineering",
    "documentation",
    "research",
    "learning",
    "security",
}
RISKS = {"low", "medium", "high", "critical"}
SKILL_SECTIONS = {
    "When to use",
    "When not to use",
    "Inputs",
    "Procedure",
    "Outputs",
    "Verification",
    "Safety",
}
WORKFLOW_SECTIONS = {
    "Purpose",
    "Activation",
    "Inputs",
    "Steps",
    "Outputs",
    "Verification",
    "Failure handling",
    "Approval gates",
    "Completion",
}
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SKILL_LINE = re.compile(r"^- Skill: ([a-z0-9]+(?:-[a-z0-9]+)*)$", re.MULTILINE)
README_COUNTS = re.compile(r"(\d+) skills and (\d+) sequential workflows")


def error(errors: list[str], path: Path, message: str) -> None:
    errors.append(f"{path}: {message}")


def check_links(errors: list[str], path: Path, body: str, root: Path) -> None:
    for line, target in relative_markdown_links(body):
        candidate, _anchor, problem = resolve_link(path, target, root)
        if problem or candidate is None or not candidate.exists():
            error(errors, path, f"broken link on line {line}: {target}")


def validate_skill(path: Path, root: Path, names: dict[str, Path], errors: list[str]) -> None:
    text = read_text(path)
    meta, body, problem = split_frontmatter(text)
    if problem or meta is None:
        error(errors, path, problem or "missing frontmatter")
        return
    name = meta.get("name")
    if not isinstance(name, str) or not NAME_RE.match(name):
        error(errors, path, "name must be a lowercase hyphenated string")
    elif path.parent.name != name:
        error(errors, path, f"name {name!r} does not match directory {path.parent.name!r}")
    elif name in names:
        error(errors, path, f"duplicate skill name {name}; also defined in {names[name]}")
    else:
        names[name] = path
    description = meta.get("description")
    if not isinstance(description, str) or not description.strip():
        error(errors, path, "description is required")
    elif len(description.strip()) > 1024:
        error(errors, path, "description exceeds 1024 characters")
    metadata = meta.get("metadata")
    if not isinstance(metadata, dict):
        error(errors, path, "metadata mapping is required")
        metadata = {}
    version = metadata.get("version")
    if not isinstance(version, str) or not version:
        error(errors, path, "metadata.version must be a non-empty string")
    domain = metadata.get("domain")
    if domain not in DOMAINS:
        error(errors, path, f"metadata.domain must be one of: {', '.join(sorted(DOMAINS))}")
    elif path.parent.parent.name != domain:
        error(errors, path, f"metadata.domain {domain} does not match {path.parent.parent.name}")
    if metadata.get("risk") not in RISKS:
        error(errors, path, "metadata.risk must be low, medium, high, or critical")
    status = metadata.get("status", "active")
    if status not in {"active", "draft", "deprecated"}:
        error(errors, path, "metadata.status must be active, draft, or deprecated when set")
    for field in ("tools", "outputs"):
        value = metadata.get(field)
        if value is not None and not (isinstance(value, list) and all(isinstance(item, str) for item in value)):
            error(errors, path, f"metadata.{field} must be a list of strings when set")
    missing = SKILL_SECTIONS - heading_set(body)
    for section in sorted(missing):
        error(errors, path, f"missing section {section}")
    check_links(errors, path, body, root)


def validate_workflow(path: Path, root: Path, skill_names: set[str], errors: list[str]) -> None:
    text = read_text(path)
    meta, body, problem = split_frontmatter(text)
    if problem or meta is None:
        error(errors, path, problem or "missing frontmatter")
        return
    name = meta.get("name")
    if not isinstance(name, str) or path.parent.name != name:
        error(errors, path, "name must match the workflow directory")
    if not isinstance(meta.get("description"), str) or not str(meta.get("description")).strip():
        error(errors, path, "description is required")
    if meta.get("execution") != "sequential":
        error(errors, path, "execution must be sequential")
    multi = meta.get("multi_agent", "disabled")
    if multi not in {"optional", "disabled"}:
        error(errors, path, "multi_agent must be optional or disabled")
    declared = meta.get("skills")
    if not isinstance(declared, list) or not declared or not all(isinstance(item, str) for item in declared):
        error(errors, path, "skills must be a non-empty list of skill names")
        declared = []
    used = SKILL_LINE.findall(body)
    if not used:
        error(errors, path, "steps must include at least one '- Skill: <name>' line")
    for skill in declared:
        if skill not in skill_names:
            error(errors, path, f"skills list references unknown skill {skill}")
        if skill not in used:
            error(errors, path, f"skills list includes {skill} but no step uses it")
    for skill in used:
        if skill not in declared:
            error(errors, path, f"step uses {skill} but skills frontmatter does not list it")
        if skill not in skill_names:
            error(errors, path, f"step references unknown skill {skill}")
    missing = WORKFLOW_SECTIONS - heading_set(body)
    for section in sorted(missing):
        error(errors, path, f"missing section {section}")
    check_links(errors, path, body, root)


def check_readme_counts(root: Path, skills: int, workflows: int, errors: list[str]) -> None:
    readme = root / "README.md"
    if not readme.is_file():
        return
    match = README_COUNTS.search(read_text(readme))
    if match is None:
        return
    stated = (int(match.group(1)), int(match.group(2)))
    if stated != (skills, workflows):
        error(errors, readme, f"states {stated[0]} skills and {stated[1]} workflows; found {skills} and {workflows}")


def run(root: Path) -> list[str]:
    errors: list[str] = []
    names: dict[str, Path] = {}
    skill_files = sorted(root.joinpath("skills").glob("*/*/SKILL.md"))
    if not skill_files:
        errors.append(f"{root / 'skills'}: no SKILL.md files found")
    for path in skill_files:
        validate_skill(path, root, names, errors)
    workflow_files = sorted(root.joinpath("workflows").glob("*/WORKFLOW.md"))
    if len(workflow_files) < 7:
        errors.append(f"{root / 'workflows'}: expected at least 7 workflows, found {len(workflow_files)}")
    for path in workflow_files:
        validate_workflow(path, root, set(names), errors)
    check_readme_counts(root, len(skill_files), len(workflow_files), errors)
    return errors


def self_test() -> None:
    import tempfile

    with tempfile.TemporaryDirectory() as raw:
        root = Path(raw)
        (root / "AGENTS.md").write_text("agent\n", encoding="utf-8")
        (root / "mcp").mkdir()
        (root / "mcp/catalog.yaml").write_text("version: 1\n", encoding="utf-8")
        skill = root / "skills" / "documentation" / "example" / "SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text(
            "---\nname: example\ndescription: Example skill for the self test.\n"
            "metadata:\n  version: \"1.0.0\"\n  domain: documentation\n  risk: low\n---\n\n"
            "## When to use\n\n- x\n\n## When not to use\n\n- y\n\n## Inputs\n\n- z\n\n"
            "## Procedure\n\n1. Do the task.\n\n## Outputs\n\n- out\n\n## Verification\n\n- check\n\n## Safety\n\n- safe\n",
            encoding="utf-8",
        )
        broken = root / "skills" / "documentation" / "broken" / "SKILL.md"
        broken.parent.mkdir(parents=True)
        broken.write_text("---\nname: [broken\n", encoding="utf-8")
        workflow = root / "workflows" / "example" / "WORKFLOW.md"
        workflow.parent.mkdir(parents=True)
        workflow.write_text(
            "---\nname: example\ndescription: Example.\nexecution: sequential\nmulti_agent: required\nskills:\n  - missing\n---\n\n"
            "## Purpose\n\n## Activation\n\n## Inputs\n\n## Steps\n\n- Skill: missing\n\n"
            "## Outputs\n\n## Verification\n\n## Failure handling\n\n## Approval gates\n\n## Completion\n",
            encoding="utf-8",
        )
        (root / "README.md").write_text("- 9 skills and 1 sequential workflows.\n", encoding="utf-8")
        errors = run(root)
        joined = "\n".join(errors)
        assert any("states 9 skills and 1 workflows; found 2 and 1" in item for item in errors), joined
        assert any("broken" in item and "frontmatter" in item for item in errors), joined
        assert any("multi_agent" in item for item in errors), joined
        assert any("unknown skill missing" in item for item in errors), joined
        assert not any("example/SKILL.md" in item and "missing section" in item for item in errors), joined


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate skills and workflows")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        print("skill validator self-test passed")
        return 0
    root = find_root(args.root)
    errors = run(root)
    if errors:
        for item in errors:
            print(item, file=sys.stderr)
        print(f"{len(errors)} skill or workflow error(s)", file=sys.stderr)
        return 1
    skill_count = len(list(root.joinpath("skills").glob("*/*/SKILL.md")))
    workflow_count = len(list(root.joinpath("workflows").glob("*/WORKFLOW.md")))
    print(f"validated {skill_count} skills and {workflow_count} workflows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
