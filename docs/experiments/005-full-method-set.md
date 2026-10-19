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
