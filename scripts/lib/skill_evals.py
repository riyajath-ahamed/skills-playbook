"""Score skill outputs against fixture rubrics and run a model command over the fixtures.

`self-test` needs no model. Each rubric must pass its reference pass response and fail its
reference fail response, so a rubric that cannot tell a good answer from a bad one fails CI.
`run` sends each prompt to a command on stdin, with and without the skill, and scores stdout.
"""

from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

import yaml

from common import find_root, read_text, relative_markdown_links, resolve_link, split_frontmatter

CHECK_KINDS = ("any", "all", "none")
RESPONSE_FILES = ("pass.txt", "fail.txt")
REFERENCE_BUDGET = 20000
REFERENCE_SUFFIXES = {".md", ".yaml", ".yml"}


@dataclass
class Check:
    id: str
    description: str
    kind: str
    patterns: list[re.Pattern[str]]


@dataclass
class Rubric:
    case_id: str
    skill: str
    prompt: str
    input_path: Path
    directory: Path
    checks: list[Check]


@dataclass
class CheckResult:
    id: str
    description: str
    passed: bool


def rubric_cases(root: Path) -> list[dict]:
    loaded = yaml.safe_load(read_text(root / "evals" / "cases.yaml"))
    cases = loaded.get("cases") if isinstance(loaded, dict) else None
    return [case for case in cases or [] if isinstance(case, dict) and case.get("method") == "rubric"]


def skill_path(root: Path, skill: str) -> Path | None:
    matches = sorted(root.glob(f"skills/*/{skill}/SKILL.md"))
    return matches[0] if matches else None


def _parse_check(raw: object, where: str) -> Check:
    if not isinstance(raw, dict) or not isinstance(raw.get("id"), str):
        raise ValueError(f"{where}: each check needs an id")
    kinds = [kind for kind in CHECK_KINDS if kind in raw]
    if len(kinds) != 1:
        raise ValueError(f"{where}: check {raw['id']} needs exactly one of {', '.join(CHECK_KINDS)}")
    patterns = raw[kinds[0]]
    if not isinstance(patterns, list) or not patterns or not all(isinstance(item, str) for item in patterns):
        raise ValueError(f"{where}: check {raw['id']} patterns must be a non-empty list of strings")
    try:
        compiled = [re.compile(item, re.IGNORECASE | re.MULTILINE) for item in patterns]
    except re.error as exc:
        raise ValueError(f"{where}: check {raw['id']} has an invalid pattern ({exc})") from exc
    return Check(raw["id"], str(raw.get("description", "")), kinds[0], compiled)


def load_rubric(root: Path, case: dict) -> Rubric:
    case_id = str(case.get("id"))
    directory = root / str(case.get("fixture", ""))
    path = directory / "rubric.yaml"
    if not path.is_file():
        raise ValueError(f"{case_id}: missing {path.relative_to(root)}")
    raw = yaml.safe_load(read_text(path))
    if not isinstance(raw, dict) or not isinstance(raw.get("prompt"), str) or not isinstance(raw.get("input"), str):
        raise ValueError(f"{case_id}: rubric needs prompt and input")
    checks = [_parse_check(item, case_id) for item in raw.get("checks") or []]
    if not checks:
        raise ValueError(f"{case_id}: rubric needs at least one check")
    if len({check.id for check in checks}) != len(checks):
        raise ValueError(f"{case_id}: check ids must be unique")
    return Rubric(case_id, str(case.get("skill")), raw["prompt"].strip(), directory / raw["input"], directory, checks)


def rubric_problems(root: Path, case: dict) -> list[str]:
    case_id = str(case.get("id"))
    problems = []
    if skill_path(root, str(case.get("skill"))) is None:
        problems.append(f"{case_id}: skill {case.get('skill')} does not exist")
    try:
        rubric = load_rubric(root, case)
    except ValueError as exc:
        return problems + [str(exc)]
    if not rubric.input_path.is_file():
        problems.append(f"{case_id}: missing input {rubric.input_path.relative_to(root)}")
    for name in RESPONSE_FILES:
        if not (rubric.directory / "responses" / name).is_file():
            problems.append(f"{case_id}: missing responses/{name}")
    return problems


def score(rubric: Rubric, text: str) -> list[CheckResult]:
    results = []
    for check in rubric.checks:
        hits = [bool(pattern.search(text)) for pattern in check.patterns]
        passed = {"any": any(hits), "all": all(hits), "none": not any(hits)}[check.kind]
        results.append(CheckResult(check.id, check.description, passed))
    return results


def _references(root: Path, path: Path, body: str) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    budget = REFERENCE_BUDGET
    for _line, target in relative_markdown_links(body):
        candidate, _anchor, problem = resolve_link(path, target, root)
        if problem or candidate is None or not candidate.is_file() or candidate.suffix not in REFERENCE_SUFFIXES:
            continue
        relative = candidate.relative_to(root.resolve()).as_posix()
        text = read_text(candidate)
        if relative in {name for name, _ in found} or len(text) > budget:
            continue
        found.append((relative, text))
        budget -= len(text)
    return found


def build_prompt(root: Path, rubric: Rubric, with_skill: bool) -> str:
    parts = []
    if with_skill:
        path = skill_path(root, rubric.skill)
        if path is None:
            raise ValueError(f"{rubric.case_id}: skill {rubric.skill} does not exist")
        _meta, body, _problem = split_frontmatter(read_text(path))
        parts.append(f"Follow this skill. It is the procedure for the task.\n\n<skill name=\"{rubric.skill}\">\n{body.strip()}\n</skill>")
        for name, text in _references(root, path, body):
            parts.append(f"<reference path=\"{name}\">\n{text.strip()}\n</reference>")
    parts.append(f"Task:\n{rubric.prompt}")
    parts.append(f"<input name=\"{rubric.input_path.name}\">\n{read_text(rubric.input_path).rstrip()}\n</input>")
    parts.append("You have no tools and cannot run commands. Reply with the deliverable only.")
    return "\n\n".join(parts) + "\n"


def run_responder(command: str, prompt: str, timeout: float) -> tuple[str, str | None]:
    try:
        completed = subprocess.run(
            shlex.split(command), input=prompt, capture_output=True, text=True, timeout=timeout, check=False
        )
    except FileNotFoundError:
        return "", f"command not found: {shlex.split(command)[0]}"
    except subprocess.TimeoutExpired:
        return "", f"timed out after {timeout:g}s"
    if completed.returncode != 0:
        return completed.stdout, f"exit {completed.returncode}: {completed.stderr.strip()[-500:]}"
    return completed.stdout, None


def calibrate(root: Path) -> list[str]:
    problems: list[str] = []
    cases = rubric_cases(root)
    if not cases:
        return ["evals/cases.yaml: no rubric cases"]
    for case in cases:
        found = rubric_problems(root, case)
        if found:
            problems.extend(found)
            continue
        rubric = load_rubric(root, case)
        responses = rubric.directory / "responses"
        failed = [item.id for item in score(rubric, read_text(responses / "pass.txt")) if not item.passed]
        if failed:
            problems.append(f"{rubric.case_id}: reference pass response fails {', '.join(failed)}")
        if all(item.passed for item in score(rubric, read_text(responses / "fail.txt"))):
            problems.append(f"{rubric.case_id}: reference fail response passes every check")
    return problems


def _summary(results: list[CheckResult]) -> str:
    passed = sum(1 for item in results if item.passed)
    missing = [item.id for item in results if not item.passed]
    verdict = "PASS" if not missing else f"FAIL ({', '.join(missing)})"
    return f"{passed}/{len(results)} {verdict}"


def _select(root: Path, wanted: list[str]) -> list[Rubric]:
    cases = rubric_cases(root)
    known = {str(case.get("id")) for case in cases}
    unknown = [item for item in wanted if item not in known]
    if unknown:
        raise SystemExit(f"unknown rubric case: {', '.join(unknown)}")
    return [load_rubric(root, case) for case in cases if not wanted or case.get("id") in wanted]


def command_run(root: Path, args: argparse.Namespace) -> int:
    out = Path(args.out) if args.out else Path(tempfile.mkdtemp(prefix="skill-evals-"))
    out.mkdir(parents=True, exist_ok=True)
    variants = [("skill", True)] + ([("baseline", False)] if args.baseline else [])
    report = []
    failed = False
    for rubric in _select(root, args.case):
        line = [rubric.case_id]
        for label, with_skill in variants:
            text, problem = run_responder(args.responder, build_prompt(root, rubric, with_skill), args.timeout)
            (out / f"{rubric.case_id}.{label}.txt").write_text(text, encoding="utf-8")
            results = score(rubric, text) if problem is None else []
            verdict = f"ERROR ({problem})" if problem else _summary(results)
            if label == "skill" and (problem or not all(item.passed for item in results)):
                failed = True
            line.append(f"{label}: {verdict}")
            report.append({"case": rubric.case_id, "variant": label, "error": problem, "checks": [asdict(item) for item in results]})
        print("  ".join(line))
    (out / "results.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"responses and results.json written to {out}")
    return 1 if failed else 0


def command_score(root: Path, args: argparse.Namespace) -> int:
    rubric = _select(root, [args.case])[0]
    results = score(rubric, read_text(Path(args.response)))
    for item in results:
        print(f"{'ok  ' if item.passed else 'MISS'} {item.id}: {item.description}")
    print(_summary(results))
    return 0 if all(item.passed for item in results) else 1


def command_self_test(root: Path, _args: argparse.Namespace) -> int:
    problems = calibrate(root)
    for item in problems:
        print(item, file=sys.stderr)
    if problems:
        print(f"{len(problems)} rubric calibration error(s)", file=sys.stderr)
        return 1
    print(f"calibrated {len(rubric_cases(root))} rubric case(s); no model was called")
    return 0


def command_list(root: Path, _args: argparse.Namespace) -> int:
    for rubric in _select(root, []):
        print(f"{rubric.case_id}  skill={rubric.skill}  checks={len(rubric.checks)}")
    return 0


def command_prompt(root: Path, args: argparse.Namespace) -> int:
    sys.stdout.write(build_prompt(root, _select(root, [args.case])[0], not args.baseline))
    return 0


def parser() -> argparse.ArgumentParser:
    main_parser = argparse.ArgumentParser(description="Skill evaluation harness")
    main_parser.add_argument("--root", type=Path, default=Path.cwd())
    commands = main_parser.add_subparsers(dest="command", required=True)
    commands.add_parser("self-test", help="check that every rubric separates its reference responses")
    commands.add_parser("list", help="list rubric cases")
    prompt = commands.add_parser("prompt", help="print the prompt for one case")
    prompt.add_argument("case")
    prompt.add_argument("--baseline", action="store_true", help="omit the skill")
    scored = commands.add_parser("score", help="score a saved response")
    scored.add_argument("case")
    scored.add_argument("response")
    run = commands.add_parser("run", help="send prompts to a model command and score the replies")
    run.add_argument("--responder", required=True, help="command that reads the prompt on stdin and prints the reply")
    run.add_argument("--case", action="append", default=[], help="limit to this case; repeatable")
    run.add_argument("--baseline", action="store_true", help="also run each case without the skill")
    run.add_argument("--out", help="directory for replies and results.json; defaults to a new temp directory")
    run.add_argument("--timeout", type=float, default=600.0)
    return main_parser


COMMANDS = {
    "self-test": command_self_test,
    "list": command_list,
    "prompt": command_prompt,
    "score": command_score,
    "run": command_run,
}


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    return COMMANDS[args.command](find_root(args.root), args)


if __name__ == "__main__":
    raise SystemExit(main())
