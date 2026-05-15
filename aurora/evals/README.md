# Aurora Regression Eval Suite

Regression eval suite added in v1.7.8 to verify that the runtime
principles introduced in v1.7.7 (specific-board confirmation, deployment
method question, Question Rule with recommendations, Language Rule for
deliverables) actually hold against realistic prompts — not just against
the principle-pinning pytests.

The pytests in `aurora/tests/test_v177_principles.py` check that the
**rules are written down** in SKILL.md and souls. This eval suite checks
that an actual subagent **runs** the rules correctly when handed a real
prompt.

## What's here

- `evals.json` — three test prompts plus assertions per prompt.
- `grade.py` — runs assertions against eval outputs and writes
  `grading.json` per run and a `grading-summary.json` per iteration.
- `README.md` — this file.

## How to run

Each invocation needs paired subagent runs (with-skill + baseline).
Spawn them in parallel; both write to `aurora-workspace/iteration-N/`
which is gitignored.

1. Create the iteration workspace:

   ```
   mkdir -p aurora-workspace/iteration-N/eval-1-vague-board-triggers-question/{with_skill,without_skill}/outputs
   # repeat per eval id in evals.json
   ```

2. Spawn the subagents. Each receives the eval prompt plus a save path.
   See `aurora-workspace/iteration-1/` for the directory layout the
   grader expects.

3. Grade:

   ```
   python aurora/evals/grade.py aurora-workspace/iteration-N
   ```

   Writes `grading.json` next to each run's `outputs/` folder and a
   `grading-summary.json` at the iteration root. Each assertion fails
   loud if the rule it pins regresses.

## Eval design

Each eval is intentionally narrow — one prompt, 3-4 assertions tied to
specific Iron Laws or Communication Rules. Surface coverage matters
more than depth. A passing eval is not proof that Aurora is perfect for
that scenario; it is proof that the rule the assertion pins did not
silently regress.

| Eval | Tests | Pinned rules |
|------|-------|--------------|
| 1. vague-board-triggers-question | User names only the chip family; agent must ask for specific board and deployment method, with Recommended: format | Iron Law 1, Iron Law 8 deployment-method, Question Rule |
| 2. swedish-prompt-swedish-deliverables | User typed Swedish, gave full context; agent must produce Swedish README + INSTALL while keeping YAML keys, entity_ids, and attribution banner in English | Language Rule for Deliverables |
| 3. complete-context-no-extra-questions | User specified board, sensor, wiring, deployment method; agent must NOT re-ask, must use the local-CLI INSTALL template | Volt Iron Law 8 conditional deliverables, install-cli.md template |

## Why the workspace is gitignored

Run outputs (response.md, project folders, grading.json) are large and
specific to a single iteration. Committing them would inflate the repo
and create merge conflicts between independent runs. The eval suite
itself (evals.json + grade.py + README.md) is committed; the runs are
not.

## Iteration-1 baseline (v1.7.7 vs no-skill)

First run captured 2026-05-15 against commit `03d8ef8` (v1.7.7).
Numbers reproducible by running the suite again on the same commit.

| Eval | with_skill | without_skill | delta |
|------|------------|---------------|-------|
| 1. vague-board | 2/3 | 1/3 | +33 pp |
| 2. swedish | 4/4 | 2/4 | +50 pp |
| 3. complete-context | 3/4 | 3/4 | 0 pp |
| **Total** | **9/11 (82%)** | **6/11 (55%)** | **+27 pp** |

The eval-3 tie comes from both runs missing the same assertion (the
INSTALL template's literal "pip install esphome" phrasing); the
with_skill agent adapted the template language but kept the flow. The
eval-2 difference comes from the baseline omitting INSTALL.md entirely
and skipping the attribution banner — both gaps the v1.7.7 Iron Laws
catch.
