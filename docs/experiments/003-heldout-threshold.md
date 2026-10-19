# Experiment 003: Held-out threshold and learned combination

Date: 2026-10-18. Method: `ast10-split`. Model: `clef-flash`, digest `0a2a05d6a581…` (all three runs share it; `svb.heldout` checks).

**Model change.** 001 and 002 used digest `2aa4d39fd93b…`. Ollama 0.40.6 no longer loads that download, so the model was re-pulled on 2026-10-18 and the digest changed. 003's numbers are internally consistent but are not directly comparable with 001 and 002: a difference from them may come from the model, not from the held-out method.

## Question

Experiments 001 and 002 chose thresholds and suggested combinations on the same 200 test skills they reported on. Do those findings hold when the threshold and the combination are chosen on separate data and measured on skills nobody has looked at?

## Pre-registration (committed before the test run was scored)

- Train: 200 skills from `random/train`, seed 0. Validation: 200 skills from `random/validation`, seed 0. Test: 200 skills from `random/test`, seed 1, excluding the 200 skills used in 001 and 002 (`--exclude runs/20261003-115058`).
- Combiners: `max` of the five check scores (current method); `AST04` alone (from 002, conclusion 4); logistic regression on the five scores, fitted on train.
- Each threshold is Youden's J on validation. Test is scored once; nothing is changed after seeing it.
- Primary comparison: test AUC of `logreg` minus `max`, with a paired-bootstrap 95% CI. Secondary: `AST04` minus `max`, and the TPR and FPR of each combiner at its validation threshold, with 95% CIs.
- Unparseable scores are skipped and counted, not imputed.

## Results

Runs: train `runs/20261018-181300`, validation `runs/20261018-185156`, test `runs/20261018-193117`. Each has 200 skills (154 malicious, 46 benign). The test sample shares no skills with 001 and 002. Reproduce with `python -m svb.heldout --train <train> --val <validation> --test <test>`.

| combiner | threshold (from validation) | test AUC [95% CI] | test TPR [95% CI] | test FPR [95% CI] | unscored |
|---|---|---|---|---|---|
| max | 0.156 | 0.776 [0.709, 0.839] | 0.636 [0.561, 0.710] | 0.196 [0.089, 0.312] | 0 |
| AST04 | 0.084 | 0.852 [0.792, 0.902] | 0.623 [0.548, 0.699] | 0.087 [0.020, 0.178] | 0 |
| logreg | 0.670 | 0.833 [0.772, 0.888] | 0.786 [0.720, 0.846] | 0.239 [0.122, 0.372] | 0 |

| paired difference on test | AUC diff [95% CI] |
|---|---|
| logreg - max | +0.057 [+0.028, +0.087] |
| AST04 - max | +0.076 [+0.010, +0.141] |
| logreg - AST04 | -0.019 [-0.067, +0.030] |

Logistic regression weights, fitted on train (scores are in [0, 1]):

| intercept | AST01 | AST02 | AST03 | AST04 | AST05 |
|---|---|---|---|---|---|
| -0.32 | +0.84 | +1.28 | +3.73 | +6.49 | +1.37 |

## Conclusions

Pre-registered comparisons:

1. **Primary: a learned combination beats the max.** On skills that played no part in fitting or tuning, the logistic regression's AUC is 0.057 higher than the max of the five checks, and the interval (+0.028 to +0.087) excludes zero. Experiment 002's suspicion that the max is a poor way to combine the checks holds up on held-out data.
2. **Secondary: AST04 alone also beats the max**, by 0.076 (+0.010 to +0.141). This was the post hoc observation in 002 (conclusion 4), and it survives a test on fresh skills.
3. **Secondary: operating points chosen on validation carry over unevenly.** At its validation threshold, `AST04` catches 62% of malicious skills at 9% false positives; the max catches 64% at 20%; the logistic regression catches 79% at 24%. The false-positive intervals are wide (46 benign skills) and all three overlap, so these operating points are not yet separated from each other.

Exploratory (not pre-registered):

- The logistic regression and `AST04` alone are not distinguishable (difference -0.019, interval -0.067 to +0.030). The regression gives AST04 by far the largest weight and AST03 the next, so most of what it learned is "trust AST04". With 200 training skills it does not yet add anything measurable on top of AST04.
- Youden's J put the two combiners at different points on similar curves: `AST04` at a low-false-positive point, `logreg` at a high-recall one. Which is better depends on the cost of a missed malicious skill against a wrongly blocked benign one, which this experiment does not settle.

## Limitations

- 46 benign skills in test (and in validation, which sets the thresholds), so false-positive rates are uncertain by about ±10 points.
- One sample per part, one seed. The `random` split mixes sources, so this says nothing yet about skills from unseen sources (`source_disjoint` is the next test).
- Different model digest from 001 and 002 (see the note at the top), so the 003 numbers are not a re-measurement of theirs.
- Text of `SKILL.md` only; bundled scripts are not seen.
- The logistic regression is unweighted and unregularised, fitted on 200 skills. A larger train set or class weights might separate it from `AST04`.
- The local `random` split file has no pinned hash, so the exact samples may not reproduce from a fresh download.

## Notes on the run

600 predictions, 0 unparseable, no failed calls. Train took 39 minutes, validation about 39, test about 37 (about 12 seconds per skill for `ast10-split`). A first train attempt (`runs/20261018-180217`) failed every call with HTTP 400 because Ollama 0.40.6 could not load the old model download; it was discarded, the model was re-pulled, and `svb.run` now stops after 10 failed calls in a row so this can't silently fill a run again.
