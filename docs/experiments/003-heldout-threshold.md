# Experiment 003: Held-out threshold and learned combination

Date: <date of the runs>. Method: `ast10-split`. Model: `clef-flash`, digest `0a2a05d6a581…` (all three runs share it; `svb.heldout` checks).

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

## Conclusions

## Limitations

## Notes on the run
