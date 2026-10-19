# Experiment 004: SkillScreen's test sets, under source shift

Plan: `docs/superpowers/plans/2026-10-19-exp004-skillscreen-cohorts.md`. Runner: `scripts/exp004_overnight.sh`.

## Pre-registration (committed before any 004 run; not edited afterwards)

**Question.** Do 003's findings hold on SkillScreen's test sets, in particular when the skills come from sources never seen in training or validation? Those findings were that targeted per-risk questions beat one generic question, and that a learned combination or AST04 alone beats the max. And where does `clef-flash` sit next to the methods SkillScreen published?

**Model and data.**
- Model: `clef-flash`, digest `0a2a05d6a581…`, the same as 003. It is Cloudflare's 9B decision model, served by Ollama through `/v1/systemone`.
- Data: MaliciousSkillBench at revision `d4b42ce`, with hashes checked; `svb.data verify` output is recorded before and after.
- Methods: `ast10-split` and `generic-1q`.

**Samples.**

| Part | `m_structural_disjoint` (MSD) | `source_disjoint` (SD) |
|---|---|---|
| train | 300, seed 0 | 300, seed 0 |
| validation | 400, seed 0 | 400, seed 0 |
| test | all 1,947 | all 1,384 |

**Combiners.** `max` of the five checks; `AST04` alone; `logreg`, a logistic regression on the five check scores fitted on that protocol's train run with `svb.score.fit_logreg` exactly as in 003 (unweighted, unregularised, raw scores, 2,000 steps at rate 0.5). `generic-1q` is the single-question baseline from the same model.

**Thresholds.** Each is chosen on that protocol's validation run:
- Youden's J;
- `tpr95`: the highest threshold with validation TPR ≥ 0.95;
- `fpr05`: the lowest threshold with validation FPR ≤ 0.05.

Ties at a threshold are flagged.

**Primary comparisons.**
- **P1:** on the full SD test set, AUROC of `logreg` minus `generic-1q`, both `clef-flash` on the same skills, with a 95% paired-bootstrap interval (2,000 resamples by skill).
- **P2:** the same on the full MSD test set.

**Secondary comparisons.**
- S1: `AST04` minus `generic-1q`, and `logreg` minus `max`, on both test sets.
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

## Amendment 1 (2026-10-19, before any 004 run was scored)

**What changed: the model.** The local run could not go ahead, so 004 uses the **hosted** `cloudflare/clef-flash` through OpenRouter (`POST /api/alpha/decisions`), not the local Ollama build with digest `0a2a05d6a581…`. Everything else above is unchanged:
- samples and methods;
- combiners and thresholds;
- comparisons, handling and known weaknesses.

**What the runner records.** It probes the hosted model before any run and writes `runs/exp004/backend.txt`, holding:
- **the version OpenRouter serves** (the dated slug and provider, which also becomes every run's `model_digest`);
- **how the skill text is sent** (a plain string, as in 001 to 003, or `{"skill_md": text}` if the string form is refused).

Both are fixed for the whole experiment. If the served version changes between runs, the runner stops instead of mixing versions. If OpenRouter returns no dated version, the runner says so, and a silent change could not be detected.

**Consequences, stated in advance:**
- **Not a re-measurement of 001 to 003.** The hosted model may use different weights or precision from the local Q8 build, so 004 says nothing about the local model's numbers.
- **The probe's frozen 003 weights** (`probe-logreg003`) were fitted on the local model's scores, so that row is indicative only.
- **Context window.** The hosted context is reported as 24,576 tokens, against our cap of 60,000 characters (about 15,000 tokens). The runner records what the model reads for the longest test skill.
- **Budget.** At about $0.038 per million input tokens, the planned runs should cost about $2 to $5. The runner logs the cost OpenRouter reports for every call, and stops at $5 per run step or $15 in total.

## Amendment 2 (2026-10-19, before any 004 run was scored)

**What changed: one provider for the whole experiment.** OpenRouter serves `cloudflare/clef-flash` through three providers (Cloudflare, DeepInfra, PrimeIntellect) and routed calls between them. They handle long skills differently. Cloudflare and DeepInfra refuse a skill over 24,576 tokens, while PrimeIntellect cut the longest m_structural_disjoint test skill (31,548 tokens) to 16,384 tokens without an error. So every 004 call goes to **Cloudflare**, with fallback to other providers turned off:
- the runner sends `provider: {"only": ["cloudflare"], "allow_fallbacks": false}` on every call;
- a reply from any other provider counts as unscored, never as a score;
- the provider is saved in each run's `config.json`, and `--resume` refuses a different one.

**Consequence, stated in advance:** a skill over 24,576 tokens is refused and left unscored, and the unscored count is reported as for any failed call. Skills are not cut further to fit. Length counts before the run: 5 of the 1,947 m_structural_disjoint test skills are over 46,000 characters, and none of the 1,384 source_disjoint test skills are.

## Results

Run on 2026-10-19 by `scripts/exp004_overnight.sh` from commit `fe4f43e`, on hosted `cloudflare/clef-flash` served by Cloudflare only. Raw output is in `results/exp004/` and an interactive view in `site/` (the dashboard). Every planned skill was scored; one MSD test skill is over the 24,576-token context and has no score (amendment 2). Data hashes matched before and after the run.

### Primary comparisons

| | SD test (1,384: 839 malicious, 545 benign) | MSD test (1,947: 1,500 malicious, 447 benign) |
|---|---|---|
| `logreg` AUROC | 0.658 [0.628, 0.688] | 0.831 [0.813, 0.849] |
| `generic-1q` AUROC | 0.518 [0.487, 0.549] | 0.703 [0.678, 0.725] |
| **P1 / P2: `logreg` − `generic-1q`** | **+0.139 [+0.105, +0.172]** | **+0.129 [+0.105, +0.152]** |

### Secondary comparisons

**S1, combiners.**

| paired AUROC difference | SD | MSD |
|---|---|---|
| `AST04` − `generic-1q` | +0.096 [+0.059, +0.130] | +0.123 [+0.099, +0.150] |
| `max` − `generic-1q` | +0.154 [+0.117, +0.189] | +0.121 [+0.096, +0.146] |
| `logreg` − `max` | −0.014 [−0.027, −0.002] | +0.007 [−0.002, +0.016] |
| `AST04` − `max` | −0.057 [−0.091, −0.026] | +0.002 [−0.017, +0.022] |

Logistic regression weights (intercept, AST01 to AST05): SD −0.64, +1.28, +3.08, +3.67, +6.42, +1.81; MSD −0.18, +1.30, +2.33, +3.50, +4.11, +0.22.

**S2, operating points.** FPR at 99% recall is 0.971 (SD) and 0.944 (MSD) for `logreg`: no combiner reaches SkillScreen's high-recall rule at a usable false-positive rate. At the validation `fpr05` thresholds, on test:

| combiner | SD TPR | SD FPR | MSD TPR | MSD FPR |
|---|---|---|---|---|
| `max` | 0.238 | 0.086 | 0.552 | 0.063 |
| `AST04` | 0.172 | 0.040 | 0.480 | 0.025 |
| `logreg` | 0.169 | 0.046 | 0.600 | 0.067 |
| `generic-1q` | 0.120 | 0.026 | 0.372 | 0.038 |

**S3, SD flagged by source** (`logreg` at `fpr05`; SkillScreen seed 42 at 0.5):

| source | label | skills | `logreg` | SkillScreen |
|---|---|---|---|---|
| SkillHarm | malicious | 728 | 39 | 695 |
| SkillFortifyBench | malicious | 90 | 85 | 90 |
| ATR Skill Security Benchmark | malicious | 21 | 18 | 21 |
| ATR Skill Security Benchmark | benign | 455 | 24 | 103 |
| SkillFortifyBench | benign | 90 | 1 | 90 |

**S4, SD cascade** (SkillScreen seed 42 flags, then `logreg` at `fpr05` must also flag): recall 0.169, FPR 0.011, against SkillScreen alone at recall 0.961, FPR 0.354.

**S5, against SkillScreen's methods** (descriptive; paired AUROC, `logreg` minus each):

| | SD | MSD |
|---|---|---|
| TypeSafe Jev 1.13 (0.652 SD, 0.841 MSD) | +0.006 [−0.027, +0.039] | −0.010 [−0.028, +0.009] |
| GPT-5.5 zero-shot (0.914, 0.950) | −0.257 [−0.285, −0.229] | −0.119 [−0.137, −0.103] |
| SkillScreen seed 42 (0.903, 0.992) | −0.246 [−0.279, −0.213] | −0.161 [−0.179, −0.144] |

### 004a probe (exploratory)

100 SkillHarm malicious skills against the 90 benign SkillFortifyBench skills. AUROC: `max` 0.698, `logreg` with 003's frozen weights 0.637, `AST04` 0.419, `generic-1q` 0.375. `AST04` and `generic-1q` rank these benign skills above these malicious ones.

## Conclusions

Pre-registered comparisons:

1. **P1 and P2: targeted checks beat one generic question on both held-out test sets.** `logreg` is ahead of `generic-1q` by 0.139 on source-disjoint skills and 0.129 on structurally disjoint ones, and both intervals exclude zero. 003's main finding holds on SkillScreen's test sets, including skills from sources never seen in training or validation. On unseen sources the generic question is at chance (0.518).
2. **S1: 003's combiner finding does not carry over.** In 003 a learned combination and `AST04` alone both beat the max. Here, on SD, the max beats `logreg` (−0.014) and `AST04` (−0.057); on MSD the three are indistinguishable. Weights fitted on one set of sources do not help on new ones, and the max is the safer default.
3. **S2: validation thresholds hold their false-positive rate but not a useful recall on new sources.** The `fpr05` thresholds give test FPRs of 2.5% to 8.6%, close to target. Recall at those thresholds is 17% to 24% on SD against 48% to 60% on MSD.
4. **S3: SkillHarm is where the checks fail.** On SD, `logreg` at `fpr05` catches 85 of 90 SkillFortifyBench and 18 of 21 ATR malicious skills, but only 39 of 728 SkillHarm ones; SkillHarm is 87% of SD's malicious skills. The same holds on MSD (6 of 92). At that threshold the checks flag far fewer benign skills than SkillScreen does (1 of 90 SkillFortifyBench benign against 90 of 90).
5. **S4: as a second stage after SkillScreen, the checks cut false positives sharply but lose most recall** on SD (FPR 0.354 to 0.011, recall 0.961 to 0.169), because they miss SkillHarm.
6. **S5: `clef-flash` with targeted checks is level with TypeSafe Jev 1.13** (intervals include zero on both sets) and well behind SkillScreen's fine-tuned model and GPT-5.5 zero-shot.

Exploratory (not pre-registered):

- **The SkillHarm gap is not only a threshold effect.** At SkillScreen's own SD false-positive rate (0.354), `max` catches 376 of 728 SkillHarm skills (52%) and `logreg` 350 (48%), against SkillScreen's 695 (95%). On ATR and SkillFortifyBench the checks are close to SkillScreen at that rate (19 of 21 and 87 to 88 of 90).
- **Why SkillHarm is missed is untested.** Its attacks may fall outside the five AST risks asked about, or may not be visible in `SKILL.md` text alone. Breaking the missed skills down by `attack_categories` would be the next step.

## Limitations

- One seed per sample; the train and validation samples are 300 and 400 skills.
- Hosted model: OpenRouter returned no dated version, so a silent model change during the run would not be detected, and the numbers are not a re-measurement of the local Q8 build used in 001 to 003.
- One MSD test skill is unscored (over 24,576 tokens). Long skills are sent whole up to 60,000 characters; nothing is cut further.
- Only `SKILL.md` text is scored; bundled scripts and resources are not seen.
- SkillScreen's methods are different models scored by their authors, so S5 is descriptive.
- The 004a probe and the matched-FPR source breakdown look at test data and are exploratory.

## Notes on the run

9,842 predictions for $2.01 in about 72 minutes (8 workers, about 2.3 predictions per second). The only failed calls are the six for the one over-length MSD skill (five checks plus the generic question). An earlier unpinned probe showed OpenRouter routing `cloudflare/clef-flash` across three providers, one of which cut long skills to 16,384 tokens without an error; amendment 2 pinned Cloudflare before any run.
