# Experiment 005: every method on SkillScreen's test skills

Runner: `scripts/exp005_overnight.sh`. Same cohorts, metric rules and model route as 004; this file is the pre-registration. Commit it before any 005 run is scored, then leave this section untouched.

## Pre-registration

**Question.** 004 scored two methods (`ast10-split`, `generic-1q`) on SkillScreen's test sets. 001 to 003 scored other methods on other skills and, at times, another model version, so no skill has a score from every method and results across experiments cannot be set side by side. With the three LLM methods run on the same skills, the same hosted model and SkillScreen's own test sets: (a) does the 002 finding on batching hold under source shift, and (b) does 004 reproduce?

**Model and data.** Hosted `cloudflare/clef-flash` through OpenRouter, pinned to provider `cloudflare`, as in 004 (amendments 1 and 2 there apply unchanged, including the one structurally disjoint test skill that exceeds the context and stays unscored). Dataset pinned and hash-checked with `svb.data verify`, before and after.

**Methods, all on the same skills.** 002's other control (`generic-5q`) and the keyword scanner are left out: the first has no validation-chosen threshold under `svb.heldout`, the second has no score.

| Method | What it is | Calls per skill |
|---|---|---|
| `ast10-split` | five AST questions, one call each | 5 |
| `ast10` | the same five questions batched in one call | 1 |
| `generic-1q` | one generic question | 1 |

**Samples.** As in 004, per protocol: train 300 (seed 0), validation 400 (seed 0), test all (1,384 source-disjoint, 1,947 structurally disjoint). All methods are run on all three parts, so one model version scores everything. 004's runs are not reused for any 005 number.

**Combiners and thresholds.** As in 004 for `ast10-split`: `max`, `AST04`, `logreg` (fitted on that protocol's train run), thresholds Youden, `tpr95` and `fpr05` chosen on validation. `ast10` is treated the same way with `max`, through `svb.heldout --method ast10`.

**Primary comparisons.** Test AUROC differences with 95% paired bootstraps (2,000 resamples by skill), on each protocol:
- **P1, P2 (replication of 004):** `ast10-split` `logreg` minus `generic-1q`. The 005 difference and its interval are reported next to 004's. They are the same model route and skills, so the question is how much the estimate moves between runs.
- **P3:** `ast10-split` `max` minus `ast10` `max`. 002 found that batching does not change the aggregate ranking; this tests it under source shift.

**Secondary.**
- **R1, reproducibility:** for `ast10-split` and `generic-1q`, 004 against 005 on the same skills: Spearman correlation of scores, largest absolute score difference, and the AUROC difference. A silent model change, which OpenRouter's unpinned slug cannot rule out, would show here.
- **R2:** AUROC, FPR at 99% recall (SkillScreen's rule) and recall and FPR at each validation threshold for every method.
- **R3:** every method against TypeSafe Jev 1.13, GPT-5.5 zero-shot and SkillScreen seed 42: paired AUROC, descriptive only since the models differ.
- **R4:** flagged counts per source on the source-disjoint set for every method.

**Handling.** As in 004: unparseable scores are counted and never imputed; a missing score counts as flagged in SkillScreen-rule metrics; each `compare` must report the full cohort (1,384 and 1,947) or the shortfall is investigated before any number is read; nothing is re-run or re-tuned after a test result is seen.

**Known weaknesses, stated in advance.**
- Hosted model version is unpinned, so R1 is the only check on silent change.
- One seed per sample; the 300 and 400 train and validation samples are smaller than SkillScreen's own training data.
- Source-disjoint validation shares sources with train, so thresholds may not transfer (measured, not corrected).
- Only `SKILL.md` text is scored.
- Comparisons with SkillScreen, GPT-5.5 and Jev are descriptive: different models.

**Budget.** About 33,000 model calls at 004's per-call cost (004 spent $2.01 for about 28,000), so roughly $2.40. The runner stops at $3 per step and $10 in total.

## Run

```bash
export OPENROUTER_API_KEY=...        # never written to a file or log
caffeinate -is nohup bash scripts/exp005_overnight.sh > /dev/null 2>&1 &    # macOS; drop caffeinate on Linux
tail -n 5 runs/exp005/progress.log
```

Re-running is always safe: finished steps are skipped and partial runs resume. Result: `runs/exp005/summary.md`.

## After the run

The dashboard build reads `runs/exp005` and writes ids and scores only. Because every skill now has every LLM method's score beside SkillScreen's, the explorer's side-by-side shows one skill across methods and the published models, which was not possible across 001 to 004.

## Results

Run on 2026-10-19 from commit `41c4805`, hosted `cloudflare/clef-flash` on provider `cloudflare`, served as `cloudflare/clef-flash|Cloudflare|unpinned`. Cost $2.37. Raw output is in [`results/exp005/`](../../results/exp005/); the figures are explorable on the [dashboard](https://snehalvartak.github.io/skill-verdict-bench/). SD is the source-disjoint test set (1,384 skills), MSD the structurally disjoint one (1,947; one skill unscored for context length).

**R1, reproducibility.** For `ast10-split` and `generic-1q`, 005 scores equal 004's on every skill in both protocols: Spearman 1.0000, largest absolute difference 0.0000, identical AUROC. No sign that the served model changed between the runs. The check cannot rule out a change that happened before 004.

**P1, P2 (replication).** `ast10-split` `logreg` minus `generic-1q`, test AUROC: SD +0.139 [0.105, 0.172] (004: +0.139), MSD +0.128 [0.106, 0.154] (004: +0.129). Same direction and size as 004, as expected from identical scores.

**P3 (batching).** `ast10-split` `max` minus `ast10` `max`: SD +0.015 [-0.009, +0.038], MSD +0.018 [+0.004, +0.032]. Test AUROCs: split 0.672 and 0.824, batched 0.656 and 0.806. Five separate calls are not distinguishable from one call on SD and slightly better on MSD. 002's finding that batching changes little holds on SD and weakens on MSD, where the interval excludes zero by a small margin.

**R2, R3 (descriptive).**

| Test set | Method | AUROC |
|---|---|---|
| SD | `ast10-split` max / logreg | 0.672 / 0.658 |
| SD | `ast10` max | 0.656 |
| SD | `generic-1q` | 0.518 |
| SD | TypeSafe / GPT-5.5 / SkillScreen seed 42 | 0.652 / 0.914 / 0.903 |
| MSD | `ast10-split` max / logreg | 0.824 / 0.831 |
| MSD | `ast10` max | 0.806 |
| MSD | `generic-1q` | 0.703 |
| MSD | TypeSafe / GPT-5.5 / SkillScreen | 0.841 / 0.950 / 0.992 |

Paired against TypeSafe, `logreg` is level on both sets (SD +0.006 [-0.027, +0.039], MSD -0.010 [-0.029, +0.008]). GPT-5.5 and SkillScreen are well ahead (SD about -0.25, MSD -0.12 to -0.16).

**Threshold transfer.** Thresholds chosen on validation for 5% false positives gave test false-positive rates of 4.0% to 8.6% on SD and recall of 17% to 24%, so they held on false positives but caught few malicious skills.

**Exploratory, after the results (not pre-registered): without SkillHarm.** SkillHarm is 728 of the 839 malicious skills in SD. Removing it (111 malicious and 545 benign skills remain), test AUROC is `generic-1q` 0.961, `ast10-split` `max` 0.953, `logreg` 0.970, batched `ast10` 0.959. Paired differences from `generic-1q`: `logreg` +0.008 [-0.009, +0.028], `max` -0.008 [-0.027, +0.012]. The SD advantage of the targeted questions over the generic question (+0.139 and +0.154 above) therefore comes from SkillHarm alone. On MSD without SkillHarm (1,404 malicious, 447 benign) the advantage holds: `logreg` minus `generic-1q` +0.120 [+0.098, +0.144], `max` minus `generic-1q` +0.099 [+0.075, +0.124]. Both intervals are percentile bootstraps over skills (1,000 resamples). Caveats: the SD remainder is small and its benign skills come from few sources, so source style may make it easy. SkillScreen's own scope is also `SKILL.md` only.

**R4 (flagged counts per source)** is available per source in the dashboard's failure heat map; the table was not written up here. On SkillHarm (728 malicious skills in SD) the `max` combiner at its `fpr05` threshold flags 97 and SkillScreen 695. A reading of 20 sampled SkillHarm misses found 18 where `SKILL.md` only points the agent to a mandatory preflight or setup step in a file that is not in the dataset. The sample was chosen by score, and the label, not the text, says these skills are harmful. SkillHarm has no benign skills in the SD test set, so SkillScreen's overall AUROC there may partly reflect source style.

**Limits unchanged from the pre-registration:** unpinned hosted model, one seed, small train and validation samples, only `SKILL.md` text scored, comparisons with other models descriptive only.
