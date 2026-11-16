"""Validate evaluation cases and run deterministic structural checks.

Human and model judgments are not executed.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

from common import find_root, read_text
from skill_evals import rubric_problems

METHODS = {"deterministic", "human", "llm-judge", "hybrid", "rubric"}
REQUIRED = ("id", "title", "domain", "task", "context", "expected_properties", "failure_conditions", "method")


def load_cases(root: Path) -> tuple[list[dict], list[str]]:
    path = root / "evals" / "cases.yaml"
    errors: list[str] = []
    try:
        loaded = yaml.safe_load(read_text(path))
    except yaml.YAMLError as exc:
        return [], [f"{path}: invalid YAML ({exc.__class__.__name__})"]
    if not isinstance(loaded, dict) or not isinstance(loaded.get("cases"), list):
        return [], [f"{path}: expected a cases list"]
    return loaded["cases"], errors


def validate_shape(cases: list[dict], errors: list[str]) -> None:
    if len(cases) < 10:
        errors.append(f"evals/cases.yaml: expected at least 10 cases, found {len(cases)}")
    seen: set[str] = set()
    for case in cases:
        if not isinstance(case, dict):
            errors.append("evals/cases.yaml: case must be a mapping")
            continue
        ident = str(case.get("id", "<missing>"))
        for field in REQUIRED:
            if field not in case:
                errors.append(f"evals/cases.yaml: {ident} missing {field}")
        if ident in seen:
            errors.append(f"evals/cases.yaml: duplicate case id {ident}")
        seen.add(ident)
        if case.get("method") not in METHODS:
            errors.append(f"evals/cases.yaml: {ident} method is not a known evaluation method")
        for field in ("expected_properties", "failure_conditions"):
            value = case.get(field)
            if not isinstance(value, list) or not value:
                errors.append(f"evals/cases.yaml: {ident} {field} must be a non-empty list")


def check_catalog_safety(root: Path, errors: list[str]) -> None:
    catalog = yaml.safe_load(read_text(root / "mcp" / "catalog.yaml"))
    if catalog.get("defaults", {}).get("deny_production_by_default") is not True:
        errors.append("eval-mcp-permission-safety: production is not denied by default")
    for item in catalog.get("integrations", []):
        if item.get("installed") is not False:
            errors.append(f"eval-mcp-permission-safety: {item.get('id')} claims to be installed")
        if item.get("environments", {}).get("production") != "deny":
            errors.append(f"eval-mcp-permission-safety: {item.get('id')} does not deny production")
    policy = yaml.safe_load(read_text(root / "mcp" / "policies" / "read-only.yaml"))
    if "write" in set(policy.get("allow", {}).get("development", [])):
        errors.append("eval-mcp-permission-safety: read-only profile allows development writes")


def check_retrieval(root: Path, errors: list[str]) -> None:
    term = "canonical-source-revision"
    hits = []
    for path in (root / "knowledge").rglob("*.md"):
        if term in read_text(path).lower():
            hits.append(path.relative_to(root).as_posix())
    expected = "knowledge/glossaries/engineering-intelligence.md"
    if expected not in hits:
        errors.append(f"eval-retrieval: {term} did not resolve to {expected}")


def check_workflows(root: Path, errors: list[str]) -> None:
    for path in sorted((root / "workflows").glob("*/WORKFLOW.md")):
        text = read_text(path)
        if "## Failure handling" not in text:
            errors.append(f"eval-failure-handling: {path.relative_to(root)} has no failure handling")
        if "multi_agent: required" in text:
            errors.append(f"eval-agent-decomposition: {path.relative_to(root)} requires multi-agent execution")
    protocol = root / "spec" / "architecture" / "multi-agent-protocol.md"
    if "does not implement it" not in read_text(protocol):
        errors.append("eval-agent-decomposition: protocol document claims the executor is implemented")


def check_docs(root: Path, errors: list[str]) -> None:
    text = read_text(root / "standards" / "documentation" / "writing-guidelines.md")
    for phrase in ("Frontmatter first", "One concept per file", "Do not include empty sections"):
        if phrase not in text:
            errors.append(f"eval-docs-quality: writing guidelines missing {phrase}")


def check_lifecycle(root: Path, errors: list[str]) -> None:
    text = read_text(root / "knowledge" / "architecture-decisions" / "0006-run-lifecycle.md")
    for state in ("pending", "planning", "awaiting_approval", "running", "verifying", "succeeded", "failed", "cancelled"):
        if state not in text:
            errors.append(f"eval-run-lifecycle: ADR-0006 does not mention {state}")


def run(root: Path) -> tuple[list[str], dict[str, int]]:
    cases, errors = load_cases(root)
    validate_shape(cases, errors)
    counts = {"deterministic": 0, "judged": 0, "rubric": 0}
    for case in cases:
        if not isinstance(case, dict):
            continue
        method = case.get("method")
        if method == "deterministic":
            counts["deterministic"] += 1
        elif method in {"human", "llm-judge", "hybrid"}:
            counts["judged"] += 1
        elif method == "rubric":
            counts["rubric"] += 1
            errors.extend(f"evals/cases.yaml: {item}" for item in rubric_problems(root, case))
    check_catalog_safety(root, errors)
    check_retrieval(root, errors)
    check_workflows(root, errors)
    check_docs(root, errors)
    check_lifecycle(root, errors)
    return errors, counts


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate evaluation cases")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    errors, counts = run(find_root(args.root))
    if errors:
        for item in errors:
            print(item, file=sys.stderr)
        print(f"{len(errors)} evaluation error(s)", file=sys.stderr)
        return 1
    print(f"evaluation structure passed ({counts['deterministic']} deterministic case(s))")
    print(f"{counts['rubric']} rubric case(s) have fixtures; run-skill-evals.sh self-test checks their calibration")
    print(f"{counts['judged']} human or model judgment(s) were not executed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
