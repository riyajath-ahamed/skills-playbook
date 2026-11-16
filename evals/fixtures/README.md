# Evaluation fixtures

Each directory here backs one `rubric` case in [`../cases.yaml`](../cases.yaml). The case names the skill under test.

| File | Contents |
|---|---|
| `input.*` | The material the skill works on, such as a diff or a design. Not Markdown, so search and the index skip it |
| `rubric.yaml` | The task prompt, the input file name, and the checks |
| `responses/pass.txt` | A hand-written answer that should pass every check |
| `responses/fail.txt` | A hand-written answer that should fail at least one check |

The reference responses are written by people to calibrate the rubric. They are not model outputs. Model replies from `run` go to a directory outside the repository.

## Checks

Each check has an `id`, a `description`, and exactly one of these pattern lists. Patterns are case-insensitive Python regular expressions, and `^` matches at line starts.

- `any`: at least one pattern matches.
- `all`: every pattern matches.
- `none`: no pattern matches. Use it for leaked values and false claims.

A rubric is keyword evidence, not a judgment of quality. A pass shows the answer mentions what a good answer must mention and avoids what it must not say. Keep human review for cases where that is not enough.

## Commands

```bash
scripts/run-skill-evals.sh self-test                      # each rubric passes pass.txt and fails fail.txt; no model
scripts/run-skill-evals.sh list
scripts/run-skill-evals.sh prompt eval-review-findings    # add --baseline to omit the skill
scripts/run-skill-evals.sh score eval-review-findings reply.txt
scripts/run-skill-evals.sh run --responder "<command>" --baseline
```

`run` sends each prompt to the responder command on stdin and scores its stdout. The command can be any non-interactive model CLI that reads a prompt from stdin and prints the reply. With `--baseline`, each case also runs without the skill, so the result shows what the skill adds. The exit status reflects the skill runs only. Replies and `results.json` go to `--out`, or to a new temporary directory.

## Add a case

1. Add a directory named after the case id with the four files above.
2. Add the case to `../cases.yaml` with `method: rubric`, `skill`, and `fixture`.
3. Run `scripts/run-skill-evals.sh self-test`. Make `fail.txt` a plausible near miss, not only an empty answer.
4. Do not put a usable credential in a fixture. Use invented values that no system issues.
