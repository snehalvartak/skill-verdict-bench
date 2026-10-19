# Experiment 004: SkillScreen's test sets, under source shift

Plan: `docs/superpowers/plans/2026-10-19-exp004-skillscreen-cohorts.md`. Runner: `scripts/exp004_overnight.sh`.

## Pre-registration (committed before any 004 run; not edited afterwards)

**Question.** Do 003's findings hold on SkillScreen's test sets, in particular when the skills come from sources never seen in training or validation? Those findings were that targeted per-risk questions beat one generic question, and that a learned combination or AST04 alone beats the max. And where does `clef-flash` sit next to the methods SkillScreen published?

**Model and data.**
- Model: `clef-flash`, digest `0a2a05d6a581…`, the same as 003. It is Cloudflare's 9B decision model, served by Ollama through `/v1/systemone`.
- Data: MaliciousSkillBench at revision `d4b42ce`, with hashes checked; `svb.data verify` output is recorded before and after.
- Methods: `ast10-split` and `naive-llm`.

**Samples.**

| Part | `m_structural_disjoint` (MSD) | `source_disjoint` (SD) |
|---|---|---|
| train | 300, seed 0 | 300, seed 0 |
| validation | 400, seed 0 | 400, seed 0 |
| test | all 1,947 | all 1,384 |

**Combiners.** `max` of the five checks; `AST04` alone; `logreg`, a logistic regression on the five check scores fitted on that protocol's train run with `svb.score.fit_logreg` exactly as in 003 (unweighted, unregularised, raw scores, 2,000 steps at rate 0.5). `naive-llm` is the single-question baseline from the same model.

**Thresholds.** Each is chosen on that protocol's validation run:
- Youden's J;
- `tpr95`: the highest threshold with validation TPR ≥ 0.95;
- `fpr05`: the lowest threshold with validation FPR ≤ 0.05.

Ties at a threshold are flagged.

**Primary comparisons.**
- **P1:** on the full SD test set, AUROC of `logreg` minus `naive-llm`, both `clef-flash` on the same skills, with a 95% paired-bootstrap interval (2,000 resamples by skill).
- **P2:** the same on the full MSD test set.

**Secondary comparisons.**
- S1: `AST04` minus `naive-llm`, and `logreg` minus `max`, on both test sets.
- S2: AUROC and FPR at 99% recall (SkillScreen's rule) for each combiner, plus test TPR and FPR at each validation threshold, with 95% intervals.
- S3: on SD, flagged counts by source (SkillHarm, ATR, SkillFortifyBench) for `logreg` at `fpr05`, and for SkillScreen seed 42 at 0.5.
- S4: on SD, a cascade. SkillScreen seed 42 flags first, then `logreg` at `fpr05` must also flag. Recall and FPR are reported against SkillScreen alone.
- S5 (descriptive only, since these are different models): paired AUROC of each combiner against TypeSafe Jev 1.13, GPT-5.5 zero-shot and SkillScreen seed 42.

**Handling.**
- Unparseable scores are counted and never imputed. In SkillScreen-rule metrics a missing score counts as flagged.
- `compare` must report every cohort skill (1,384 and 1,947); a shortfall is investigated before any number is read.
- Nothing is re-run or re-tuned after a test result has been seen.

**Known weaknesses, stated in advance.**
- SD validation comes from the same sources as SD train, so thresholds chosen there may not transfer to the held-out test sources. This is measured, not corrected.
- Only one seed per sample.
- Only the text of `SKILL.md` is scored.
- Ollama's default context for this model is 16,384 tokens. The runner records how many tokens the model actually read for the longest test skill.

**Exploratory, before the main runs (004a).** A SkillHarm probe: 100 SkillHarm malicious skills (seed 0) and all 90 benign SkillFortifyBench skills, taken from the SD test set. Only AUROC and score distributions are read from it, and nothing is chosen from it. Because these skills are SD test skills, the probe looks at test data before the main run, and that is disclosed here.

## Results

To be filled from `runs/exp004/summary.md`. The pre-registered comparisons come first; exploratory results are labelled as such.
