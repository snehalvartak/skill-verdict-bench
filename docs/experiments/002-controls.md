# 002 — Is it the AST10 content, the max of five scores, or batching?

Date: 2026-10-03. Runs: `runs/20261003-115058` (001: `ast10`, `naive-llm`, `regex`) and `runs/20261003-161714` (this experiment: `naive-x5`, `ast10-split`). Same 200 skills, same seed, same model digest as 001 (154 malicious, 46 benign). Reproduce the tables with `python -m msd.compare <both run dirs>`.

## Question

In 001, `ast10` reached AUC 0.80 against 0.63 for `naive-llm`, but it differs in three ways: it asks AST10-specific questions, it takes the maximum of five scores, and it sends the five questions in one batched call. Which of these produces the gap?

## Controls

- **`naive-x5`:** five differently worded generic questions ("is this malicious?", "would installing it put the user at risk?", ...), batched in one call, scored as the max. Same max-of-five and batching as `ast10`, no AST10 content. (Five identical copies would be useless: repeated identical calls return identical scores to every digit, checked first.)
- **`ast10-split`:** the same five AST10 questions, one call each. Same content and max as `ast10`, no batching.

## Results

AUC of the max score, with paired-bootstrap 95% intervals on differences (2,000 resamples of the 200 skills, paired by skill):

| method | AUC | Youden threshold | TPR | FPR |
|---|---|---|---|---|
| ast10 | 0.796 | 0.155 | 0.62 | 0.15 |
| ast10-split | 0.795 | 0.117 | 0.80 | 0.35 |
| naive-x5 | 0.677 | 0.123 | 0.53 | 0.17 |
| naive-llm | 0.631 | 0.079 | 0.29 | 0.02 |

| paired difference | AUC diff, 95% CI |
|---|---|
| ast10 - naive-llm | +0.165 [+0.074, +0.256] |
| ast10 - naive-x5 | +0.120 [+0.046, +0.197] |
| naive-x5 - naive-llm | +0.045 [-0.016, +0.106] |
| ast10-split - ast10 | -0.001 [-0.042, +0.039] |
| ast10-split - naive-x5 | +0.119 [+0.045, +0.190] |

Per check, AUC when batched (001) and when asked alone:

| check | batched | alone |
|---|---|---|
| AST01 malicious | 0.584 | 0.646 |
| AST02 supply chain | 0.638 | 0.699 |
| AST03 over-privileged | 0.754 | 0.775 |
| AST04 insecure metadata | 0.677 | 0.823 |
| AST05 external instructions | 0.538 | 0.573 |

The five generic paraphrases score between 0.62 and 0.67 each.

## Conclusions

1. **The AST10 content helps.** With the max-of-five and the batching held fixed, the AST10 questions beat generic paraphrases by +0.12 AUC, and the interval excludes zero. This supports the original hypothesis.
2. **The max-of-five accounts for a small part.** Moving from one generic question to the max of five generic ones adds +0.045, about a quarter of the 0.165 gap, and that interval includes zero.
3. **Batching does not change the aggregate ranking.** `ast10` and `ast10-split` have the same AUC (difference -0.001, interval within about +/-0.04). Asking alone does raise individual scores (mean AST04 score 0.12 batched, 0.20 alone) and every check's AUC, but the max-of-five hides it.
4. **The max is probably not the best way to combine the checks.** AST04 alone (0.823) scores above the max of all five (0.795). That is a point estimate picked after looking at the data, so it needs a held-out test, but it suggests learning the combination.
5. **Operating point still matters.** At the Youden-optimal thresholds, `ast10` catches 62% of malicious skills at 15% false positives; `ast10-split` catches 80% at 35%. Thresholds are chosen on the same sample, so these are optimistic.

## Reading F1 correctly

At threshold 0.1, `ast10` has F1 0.87, but flagging every skill gives precision 0.77, recall 1.00 and also F1 0.87 on this 77% malicious sample. F1 is not evidence of skill here; AUC and the TPR/FPR pair are.

## Limitations

- Same 200 skills as 001, with only 46 benign. The intervals are wide; differences under about 0.05 are not resolved.
- `naive-x5` uses one set of five paraphrases written by me. Another set might score differently, so conclusion 2 is one draw.
- Per-check comparisons (conclusion 4) are exploratory.
- Text of `SKILL.md` only; no bundled scripts.
- No train or validation runs yet, so no honestly chosen threshold and no learned combination.

## Notes on the run

400 predictions, 0 unparseable, no failed calls. The run was killed once by the two-hour background limit after 130 of 200 skills and resumed without loss. About 30 seconds per skill for both methods together.

## Next

1. Score about 100 skills each of `train` and `validation` with `ast10-split`, then fit the logistic regression on the five scores and choose the threshold on validation (the code is in `msd/score.py`).
2. Include the bundled scripts, which the Hugging Face copy omits and the GitHub `packages/` archives hold.
3. `--split source_disjoint` and a larger `--n`.
