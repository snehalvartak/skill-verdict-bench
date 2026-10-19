# 001 — Baseline on a 200-skill sample

Date: 2026-10-03. Run: `runs/20261003-115058` (git-ignored; reproducible from the config below).

Method names: `generic-1q` and `generic-5q` were called `naive-llm` and `naive-x5` when this ran; the run files keep the old names, and the scorers read them under the new ones.

## Hypothesis

Splitting detection into one question per checkable OWASP AST10 risk (`ast10`) finds more malicious skills than a single "is this malicious?" question (`generic-1q`), without more false positives. A keyword scanner (`regex`) is the floor.

## Setup

- Model: `clef-flash`, digest `2aa4d39fd93b`, via `POST /v1/systemone` (see 000).
- Data: MaliciousSkillBench, `random` split, `test` part (1,947 skills with exact text). Sample of 200, label-stratified, seed 0: **154 malicious, 46 benign**. Mean skill length 5,772 characters in the sample (6,963 across the whole test split); none truncated (limit 60,000).
- Methods: `ast10` = 5 questions (AST01 to AST05) in one call, flagged if any score is at least the threshold; `generic-1q` = 1 question; `regex` = 5 keyword patterns.
- The model returns P(true) in [0, 1] (the `noul` score). Default threshold 0.5.
- Prompt hashes are in the run's `config.json`.

## Results at the pre-set threshold (0.5)

| method | precision | recall | F1 | TP | FP | FN | TN |
|---|---|---|---|---|---|---|---|
| ast10 | 1.00 | 0.25 | 0.40 | 39 | 0 | 115 | 46 |
| generic-1q | 1.00 | 0.14 | 0.24 | 21 | 0 | 133 | 46 |
| regex | 0.91 | 0.14 | 0.24 | 21 | 2 | 133 | 44 |

Neither LLM method produced a false positive, and both missed most malicious skills. The model is conservative: its scores rarely reach 0.5.

## Threshold-free view (AUC of the max score)

The AUC and threshold-sweep tables were first computed ad hoc from `predictions.jsonl`. `score.py` now prints both (AUC of the max score per method, AUC per check, and the sweep below), so they can be regenerated from the run directory.

| method | AUC |
|---|---|
| ast10 | 0.80 |
| generic-1q | 0.63 |

Per check (AUC, malicious vs benign): AST03 over-privileged 0.75, AST04 insecure metadata 0.68, AST02 supply chain 0.64, AST01 malicious 0.58, AST05 external instructions 0.54.

## Threshold sweep (post hoc, tuned on this same sample, so optimistic)

| threshold | ast10 P / R / F1 | generic-1q P / R / F1 |
|---|---|---|
| 0.5 | 1.00 / 0.25 / 0.40 | 1.00 / 0.14 / 0.24 |
| 0.3 | 0.98 / 0.40 / 0.57 | 1.00 / 0.18 / 0.30 |
| 0.2 | 0.94 / 0.51 / 0.66 | 0.97 / 0.21 / 0.34 |
| 0.1 | 0.84 / 0.90 / 0.87 | 0.97 / 0.25 / 0.40 |
| 0.05 | 0.77 / 1.00 / 0.87 | 0.91 / 0.38 / 0.54 |

At 0.1, `ast10` reaches F1 0.87 and recall 0.90 while still clearing 19 of 46 benign skills. Because 77% of the sample is malicious, flagging everything gives P 0.77 and F1 0.87, so F1 alone hides this. AUC is the fairer number here.

## Recall by attack category (`ast10`, threshold 0.5)

Strongest: Resource / Availability Abuse (1.00), Persistence / Control (0.60). Weakest: Credential Access, Defense Evasion, Supply-Chain Abuse, Integrity (all 0.00), Instruction / Memory Manipulation (0.03). Several categories have very few samples at n=200, so these are indicative only.

## Observations

1. The score is the real output. Judged at 0.5 the model looks useless (recall 0.14 to 0.25); ranked by score, `ast10` separates the classes reasonably (AUC 0.80). The threshold needs to be chosen on held-out data, not on this sample.
2. `ast10` beat `generic-1q` on AUC (0.80 vs 0.63), supporting the hypothesis. This comparison is confounded: `ast10` takes the max of five scores, which raises the score of any input, and it asks five differently worded questions. A control (max over five copies of the generic question, or five unrelated questions) is needed before crediting the AST10 content.
3. The checks are uneven. AST03 (over-privilege) is the most informative; AST05 (external instructions) is near chance (0.54).
4. Batching changes scores. In the smoke test the same text scored 0.29 alone and 0.55 next to another question (000). `ast10` batches five questions, so its scores may differ from one call per check.
5. The regex baseline is as good as `generic-1q` at 0.5 (both recall 0.14) and has two false positives.

## Incident: silent failures

The first complete pass reported 46 benign skills as unparseable for both LLM methods, which made precision look perfect and TN zero. A direct call on a benign skill worked (score 0.038), so the cause was a transient Ollama failure hidden by a silent `except` in `ask()`. Fixes: failures are now logged to stderr, and `--resume` retries unparseable rows (tests added). The numbers above are from the clean re-run: 600 predictions, 0 unparseable. Runtime was about 26 seconds per skill (all three methods), far above the 9 seconds seen on the first 10 skills, and the one-hour background limit killed the run once; that is why runs are now resumable.

## Limitations

- One sample, one seed, 46 benign skills: confidence intervals are wide.
- Text of `SKILL.md` only; scripts in the packages are not seen.
- The dataset is about 77% malicious and partly template-generated; scores may not transfer to real skill registries.
- Threshold and aggregation choices above were looked at on the same data.

## Next experiments

1. Held-out threshold: pick the threshold on `validation`, report on `test`.
2. Controls for observation 2: max over five copies of the generic question; one call per check instead of batched.
3. `--split source_disjoint` to test shift across sources; then raise `--n`.
4. Only then, rewrite weak checks (AST05, AST01) and re-measure.
