"""Skill evaluation harness tests. No model is called."""

from __future__ import annotations

import shlex
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))

from skill_evals import build_prompt, calibrate, load_rubric, rubric_cases, rubric_problems, run_responder, score


def case(case_id: str) -> dict:
    return next(item for item in rubric_cases(ROOT) if item["id"] == case_id)


class ScoringTests(unittest.TestCase):
    def test_repository_rubrics_are_calibrated(self) -> None:
        self.assertEqual(calibrate(ROOT), [])
        self.assertGreaterEqual(len(rubric_cases(ROOT)), 4)

    def test_check_kinds(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            fixture = root / "fx"
            fixture.mkdir()
            (fixture / "rubric.yaml").write_text(
                "prompt: p\ninput: in.txt\nchecks:\n"
                "  - id: one\n    any: ['alpha', 'beta']\n"
                "  - id: both\n    all: ['alpha', 'gamma']\n"
                "  - id: never\n    none: ['secret']\n",
                encoding="utf-8",
            )
            rubric = load_rubric(root, {"id": "demo", "skill": "x", "fixture": "fx"})
        results = {item.id: item.passed for item in score(rubric, "ALPHA and gamma")}
        self.assertEqual(results, {"one": True, "both": True, "never": True})
        results = {item.id: item.passed for item in score(rubric, "beta secret")}
        self.assertEqual(results, {"one": True, "both": False, "never": False})

    def test_bad_rubric_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "fx").mkdir()
            (root / "fx" / "rubric.yaml").write_text(
                "prompt: p\ninput: in.txt\nchecks:\n  - id: two\n    any: ['a']\n    none: ['b']\n", encoding="utf-8"
            )
            problems = rubric_problems(root, {"id": "demo", "skill": "missing", "fixture": "fx"})
        self.assertTrue(any("skill missing does not exist" in item for item in problems), problems)
        self.assertTrue(any("exactly one of" in item for item in problems), problems)


class PromptTests(unittest.TestCase):
    def test_skill_prompt_inlines_skill_and_linked_template(self) -> None:
        rubric = load_rubric(ROOT, case("eval-threat-model-webhook"))
        prompt = build_prompt(ROOT, rubric, with_skill=True)
        self.assertIn('<skill name="threat-modeling">', prompt)
        self.assertIn('<reference path="templates/threat-model.md">', prompt)
        self.assertIn("POST /hooks/github", prompt)

    def test_baseline_prompt_omits_skill(self) -> None:
        rubric = load_rubric(ROOT, case("eval-threat-model-webhook"))
        prompt = build_prompt(ROOT, rubric, with_skill=False)
        self.assertNotIn("<skill", prompt)
        self.assertNotIn("<reference", prompt)
        self.assertIn(rubric.prompt, prompt)


class ResponderTests(unittest.TestCase):
    def python(self, code: str) -> str:
        return f"{shlex.quote(sys.executable)} -c {shlex.quote(code)}"

    def test_reply_comes_from_stdout_and_prompt_from_stdin(self) -> None:
        text, problem = run_responder(self.python("import sys; print(sys.stdin.read().upper())"), "hello", 30)
        self.assertIsNone(problem)
        self.assertEqual(text.strip(), "HELLO")

    def test_failures_are_reported(self) -> None:
        _text, problem = run_responder(self.python("import sys; sys.exit(3)"), "x", 30)
        self.assertIn("exit 3", problem or "")
        _text, problem = run_responder("definitely-not-a-model-cli", "x", 30)
        self.assertIn("command not found", problem or "")
        _text, problem = run_responder(self.python("import time; time.sleep(5)"), "x", 0.5)
        self.assertIn("timed out", problem or "")


if __name__ == "__main__":
    unittest.main()
