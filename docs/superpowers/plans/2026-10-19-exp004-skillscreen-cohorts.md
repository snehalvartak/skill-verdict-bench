# Experiment 004: SkillScreen's test sets, under source shift

Draft by the cloud session for the local session, which runs it. Committing it as `docs/experiments/004-*.md` is the pre-registration: do that before any test run is scored, then leave that section untouched.

Spec: `docs/experiments/003-heldout-threshold.md` (limitations and exploratory notes), `docs/superpowers/plans/2026-10-18-work-split.md`.

## Why

Experiment 003 showed, on held-out `random`-split skills, that a learned combination of the five checks (AUC 0.833) and AST04 alone (0.852) both beat the max (0.776). Two things it could not show:

1. **Whether this holds when sources change.** In MaliciousSkillBench, source and label are tangled (MalSkillBench contributes 967 malicious and 0 benign skills to the structurally disjoint test set), so a random split lets source stand in for label. SkillScreen's `source_disjoint` test set holds out three whole sources. That is where its fine-tuned model flags all 90 benign SkillFortifyBench skills, and where zero-shot TypeSafe catches none of 728 SkillHarm attacks.
2. **Where `clef-flash` sits next to published methods.** This needs SkillScreen's exact test cohorts and metric rules, which `svb.skillscreen` now provides.

## Design

All runs use `--methods ast10-split naive-llm`, the 003 model digest (`0a2a05d6a581…`), and the pinned dataset (run `uv run python -m svb.data verify` first and record its output).

| Part | `m_structural_disjoint` (MSD) | `source_disjoint` (SD) | Use |
|---|---|---|---|
| train | 300 skills, seed 0 | 300 skills, seed 0 | fit the logistic regression |
| validation | 400 skills, seed 0 | 400 skills, seed 0 | choose thresholds |
| test | **all**, `--n 5000` (1,947 skills) | **all**, `--n 5000` (1,384 skills) | scored once |

Combiners, as in 003: `max`, `AST04`, and `logreg` (fitted on that protocol's train run). `naive-llm` is the within-model single-question baseline.

Thresholds, each chosen on that protocol's validation run:
- Youden's J (as in 003);
- the highest threshold with validation TPR ≥ 0.95 (high recall, which is how SkillScreen frames screening);
- the lowest threshold with validation FPR ≤ 0.05 (for use as a second stage).

**A known weakness, stated in advance:** SD validation comes from the same sources as SD train, not from the held-out test sources. Thresholds chosen there may not transfer to the test sources. That is part of what is being measured; do not work around it.

## Pre-registered comparisons

**Primary (P1).** On the full SD test set, test AUROC of `logreg` minus `naive-llm`, both `clef-flash` on the same skills, with a 95% paired-bootstrap interval (2,000 resamples). This asks whether per-risk questions beat one question when the sources are new.

**Primary (P2).** The same comparison on the full MSD test set.

**Secondary:**
- S1: `AST04` minus `naive-llm`, and `logreg` minus `max`, on both test sets (the 003 findings, under shift).
- S2: AUROC, FPR@99 and, at each validation threshold, recall and FPR for every combiner. Use SkillScreen's rules: tie-averaged AUROC, missing scores flagged.
- S3: on SD, flagged counts per source (SkillHarm, ATR, SkillFortifyBench), for `logreg` and SkillScreen seed 42.
- S4: on SD, a cascade. SkillScreen seed 42 flags first, then `logreg` must also flag, at the validation threshold with FPR ≤ 0.05. Report recall and FPR, against SkillScreen alone (96.1% / 35.4%).
- S5 (descriptive; different models, so not a test of the method): paired AUROC of `logreg` against TypeSafe Jev 1.13, GPT-5.5 zero-shot and SkillScreen seed 42, on both test sets.

Report unparseable rows and skills `compare` could not match. `Skills compared` must equal the cohort size (1,947 and 1,384). If it doesn't, stop and find out why before reading any other number.

## Before the main runs: SkillHarm probe (004a, exploratory)

Run it first. It is cheap and decides how 004 is written up.

```bash
uv run python -m svb.skillscreen probe --skillscreen ../SkillScreen --out probe-ids.txt        # 100 SkillHarm + 90 SkillFortifyBench benign
uv run python -m svb.run --split source_disjoint --part test --ids probe-ids.txt --methods ast10-split naive-llm
uv run python -m svb.skillscreen compare runs/<probe> --method ast10-split --combine AST04 --skillscreen ../SkillScreen --protocol sd --threshold 0.1
```

Read only AUROC on the probe set (SkillHarm malicious against SkillFortifyBench benign) and the score distributions, for `max`, `AST04`, `naive-llm` and `logreg` with 003's weights frozen (`--weights=-0.32,0.84,1.28,3.73,6.49,1.37`). Choose nothing from it. These probe skills are part of the SD test set, so say in the write-up that the probe looked at test data before the main run.

## Commands for the main runs

```bash
# one protocol shown; repeat with m_structural_disjoint / msd
uv run python -m svb.run --split source_disjoint --part train      --n 300  --seed 0 --methods ast10-split naive-llm
uv run python -m svb.run --split source_disjoint --part validation --n 400  --seed 0 --methods ast10-split naive-llm
# commit the pre-registration now
uv run python -m svb.run --split source_disjoint --part test       --n 5000 --seed 0 --methods ast10-split naive-llm
uv run python -m svb.heldout --train runs/<train> --val runs/<val> --test runs/<test>    # logreg weights, Youden thresholds, combiner comparisons
uv run python -m svb.skillscreen export runs/<test> --method naive-llm --out sd-naive.csv
uv run python -m svb.skillscreen compare runs/<test> --method ast10-split --combine logreg --weights=<from heldout> \
    --skillscreen ../SkillScreen --protocol sd --threshold <validation threshold> \
    --paired sd-naive.csv typesafe judge-gpt-5.5 direct-s42
```

## Tasks

| Task | Owner | Notes |
|---|---|---|
| `svb.run --ids FILE` and `--out DIR` | cloud | done; `ids_file` is written to `config.json` only when used |
| `svb.heldout`: `tpr95` and `fpr05` thresholds from validation, `--baseline naive-llm`, `--json` | cloud | done |
| `svb.skillscreen`: `--combine max\|AST01..AST05\|logreg`, `--weights`, `--paired` against SkillScreen files or our exported CSVs | cloud | done in this PR |
| Pre-registration (`docs/experiments/004-skillscreen-cohorts.md`) and the unattended runner (`scripts/exp004_overnight.sh`) | cloud | done; dry-run end to end against a fake model |
| Start the runner and report (`docs/superpowers/plans/2026-10-19-overnight-brief.md`) | local | about 19 hours of Ollama time in all (table below) |
| Results write-up | cloud | from `runs/exp004/summary.md` |
| Review PRs, write up results from the printed tables, update the comparison page | cloud | |

## Cost at 12 seconds per skill (`ast10-split`) plus about 2 for `naive-llm`

| Run | Skills | Hours |
|---|---|---|
| Probe | 190 | 0.7 |
| Train, both protocols | 600 | 2.3 |
| Validation, both protocols | 800 | 3.1 |
| Test, both protocols | 3,331 | 13.0 |
| **Total** | 4,921 | **about 19** |

Every run resumes with `--resume`. Score SD before MSD: SD answers the main question.

## Constraints

- No new dependencies. Tests stay offline.
- One model digest across every 004 run; `svb.heldout` and the resume check enforce it.
- SkillScreen's predictions are read from a local clone and never committed (CC BY 4.0).
- No session links in commits or PRs.
