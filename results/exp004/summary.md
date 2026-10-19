# Experiment 004 results, 2026-10-19 12:57:55

Model: OpenRouter cloudflare/clef-flash on provider cloudflare, served as cloudflare/clef-flash|Cloudflare|unpinned, state sent as a string. Spent: $2.0143. Commit: fe4f43e.

## data-verify-after.txt

```
     match  primary.parquet
     match  splits/m_structural_disjoint.parquet
     match  splits/source_disjoint.parquet
```

## data-verify-before.txt

```
     match  primary.parquet
     match  splits/m_structural_disjoint.parquet
     match  splits/source_disjoint.parquet
```

## context-check.txt

```
source_disjoint: longest test skill sent as 44684 characters (cut at 60,000: False); model read 11169 input tokens
m_structural_disjoint: longest test skill (60000 characters) was refused: OpenRouter HTTP 422: {"error":{"message":"HTTP 422: {\"errors\":[{\"message\":\"AiError: AiError: Request requires 31548 tokens; the maximum is 24576 (bb6fe0f4-17c2-4c30-82e6-6ded8bc9f7d7)\",\"code\":3030}],\"success\":false,\"result\":{},\"messages\":[]}","code":422}} <- WARNING: long skills will be unscored
```

## probe-AST04.txt

```
Skills compared: 190 of SkillScreen's 1384. Ours cut at 0.1, theirs at 0.5.

| method | skills | AUROC | FPR@99 | recall | FPR |
|---|---|---|---|---|---|
| ours | 190 | 0.419 | 1.000 | 0.160 | 0.244 |
| direct-s1 | 190 | 0.653 | 1.000 | 0.950 | 1.000 |
| direct-s2 | 190 | 0.590 | 1.000 | 0.950 | 1.000 |
| direct-s3 | 190 | 0.468 | 1.000 | 0.940 | 1.000 |
| direct-s4 | 190 | 0.660 | 1.000 | 0.970 | 1.000 |
| direct-s42 | 190 | 0.570 | 1.000 | 0.940 | 1.000 |
| encoder-modernbert-large-s1 | 190 | 0.100 | 1.000 | 0.920 | 1.000 |
| encoder-modernbert-large-s3 | 190 | 0.493 | 1.000 | 0.970 | 1.000 |
| encoder-modernbert-large-s4 | 190 | 0.000 | 1.000 | 0.980 | 1.000 |
| encoder-modernbert-large-s42 | 190 | 0.006 | 1.000 | 0.920 | 1.000 |
| encoder-modernbert-large-s5 | 190 | 0.040 | 1.000 | 0.860 | 1.000 |
| judge-claude-haiku-4-5 | 190 | 0.358 | 1.000 | 0.200 | 0.000 |
| judge-gpt-5.4-mini | 190 | 0.848 | 1.000 | 0.100 | 0.000 |
| judge-gpt-5.5-fewshot-sd | 190 | 0.972 | 0.800 | 0.590 | 0.000 |
| judge-gpt-5.5-reasoning | 190 | 0.957 | 0.722 | 0.350 | 0.000 |
| judge-gpt-5.5 | 190 | 0.927 | 0.867 | 0.460 | 0.000 |
| judge-grok-4.3-sd | 190 | 0.405 | 1.000 | 0.230 | 0.322 |
| static | 190 | 0.599 | 1.000 | 0.300 | 0.122 |
| typesafe | 190 | 0.107 | 1.000 | 0.000 | 0.000 |
| untuned-r002 | 190 | 0.059 | 1.000 | 0.000 | 0.000 |
| word-svm-r002 | 190 | 0.907 | 0.978 | 0.630 | 0.000 |

| source | label | skills | ours flagged | direct-s42 flagged |
|---|---|---|---|---|
| SkillFortifyBench | benign | 90 | 22 | 90 |
| SkillHarm | malicious | 100 | 16 | 94 |

Cascade (direct-s42 flags, then ours must also flag): recall 0.150, FPR 0.244
```

## probe-generic.txt

```
Skills compared: 190 of SkillScreen's 1384. Ours cut at 0.1, theirs at 0.5.

| method | skills | AUROC | FPR@99 | recall | FPR |
|---|---|---|---|---|---|
| ours | 190 | 0.375 | 1.000 | 0.000 | 0.011 |
| direct-s1 | 190 | 0.653 | 1.000 | 0.950 | 1.000 |
| direct-s2 | 190 | 0.590 | 1.000 | 0.950 | 1.000 |
| direct-s3 | 190 | 0.468 | 1.000 | 0.940 | 1.000 |
| direct-s4 | 190 | 0.660 | 1.000 | 0.970 | 1.000 |
| direct-s42 | 190 | 0.570 | 1.000 | 0.940 | 1.000 |
| encoder-modernbert-large-s1 | 190 | 0.100 | 1.000 | 0.920 | 1.000 |
| encoder-modernbert-large-s3 | 190 | 0.493 | 1.000 | 0.970 | 1.000 |
| encoder-modernbert-large-s4 | 190 | 0.000 | 1.000 | 0.980 | 1.000 |
| encoder-modernbert-large-s42 | 190 | 0.006 | 1.000 | 0.920 | 1.000 |
| encoder-modernbert-large-s5 | 190 | 0.040 | 1.000 | 0.860 | 1.000 |
| judge-claude-haiku-4-5 | 190 | 0.358 | 1.000 | 0.200 | 0.000 |
| judge-gpt-5.4-mini | 190 | 0.848 | 1.000 | 0.100 | 0.000 |
| judge-gpt-5.5-fewshot-sd | 190 | 0.972 | 0.800 | 0.590 | 0.000 |
| judge-gpt-5.5-reasoning | 190 | 0.957 | 0.722 | 0.350 | 0.000 |
| judge-gpt-5.5 | 190 | 0.927 | 0.867 | 0.460 | 0.000 |
| judge-grok-4.3-sd | 190 | 0.405 | 1.000 | 0.230 | 0.322 |
| static | 190 | 0.599 | 1.000 | 0.300 | 0.122 |
| typesafe | 190 | 0.107 | 1.000 | 0.000 | 0.000 |
| untuned-r002 | 190 | 0.059 | 1.000 | 0.000 | 0.000 |
| word-svm-r002 | 190 | 0.907 | 0.978 | 0.630 | 0.000 |

| source | label | skills | ours flagged | direct-s42 flagged |
|---|---|---|---|---|
| SkillFortifyBench | benign | 90 | 1 | 90 |
| SkillHarm | malicious | 100 | 0 | 94 |

Cascade (direct-s42 flags, then ours must also flag): recall 0.000, FPR 0.011
```

## probe-logreg003.txt

```
Skills compared: 190 of SkillScreen's 1384. Ours cut at 0.5, theirs at 0.5.

| method | skills | AUROC | FPR@99 | recall | FPR |
|---|---|---|---|---|---|
| ours | 190 | 0.637 | 0.911 | 1.000 | 1.000 |
| direct-s1 | 190 | 0.653 | 1.000 | 0.950 | 1.000 |
| direct-s2 | 190 | 0.590 | 1.000 | 0.950 | 1.000 |
| direct-s3 | 190 | 0.468 | 1.000 | 0.940 | 1.000 |
| direct-s4 | 190 | 0.660 | 1.000 | 0.970 | 1.000 |
| direct-s42 | 190 | 0.570 | 1.000 | 0.940 | 1.000 |
| encoder-modernbert-large-s1 | 190 | 0.100 | 1.000 | 0.920 | 1.000 |
| encoder-modernbert-large-s3 | 190 | 0.493 | 1.000 | 0.970 | 1.000 |
| encoder-modernbert-large-s4 | 190 | 0.000 | 1.000 | 0.980 | 1.000 |
| encoder-modernbert-large-s42 | 190 | 0.006 | 1.000 | 0.920 | 1.000 |
| encoder-modernbert-large-s5 | 190 | 0.040 | 1.000 | 0.860 | 1.000 |
| judge-claude-haiku-4-5 | 190 | 0.358 | 1.000 | 0.200 | 0.000 |
| judge-gpt-5.4-mini | 190 | 0.848 | 1.000 | 0.100 | 0.000 |
| judge-gpt-5.5-fewshot-sd | 190 | 0.972 | 0.800 | 0.590 | 0.000 |
| judge-gpt-5.5-reasoning | 190 | 0.957 | 0.722 | 0.350 | 0.000 |
| judge-gpt-5.5 | 190 | 0.927 | 0.867 | 0.460 | 0.000 |
| judge-grok-4.3-sd | 190 | 0.405 | 1.000 | 0.230 | 0.322 |
| static | 190 | 0.599 | 1.000 | 0.300 | 0.122 |
| typesafe | 190 | 0.107 | 1.000 | 0.000 | 0.000 |
| untuned-r002 | 190 | 0.059 | 1.000 | 0.000 | 0.000 |
| word-svm-r002 | 190 | 0.907 | 0.978 | 0.630 | 0.000 |

| source | label | skills | ours flagged | direct-s42 flagged |
|---|---|---|---|---|
| SkillFortifyBench | benign | 90 | 90 | 90 |
| SkillHarm | malicious | 100 | 100 | 94 |

Cascade (direct-s42 flags, then ours must also flag): recall 0.940, FPR 1.000
```

## probe-max.txt

```
Skills compared: 190 of SkillScreen's 1384. Ours cut at 0.1, theirs at 0.5.

| method | skills | AUROC | FPR@99 | recall | FPR |
|---|---|---|---|---|---|
| ours | 190 | 0.698 | 0.933 | 0.790 | 0.533 |
| direct-s1 | 190 | 0.653 | 1.000 | 0.950 | 1.000 |
| direct-s2 | 190 | 0.590 | 1.000 | 0.950 | 1.000 |
| direct-s3 | 190 | 0.468 | 1.000 | 0.940 | 1.000 |
| direct-s4 | 190 | 0.660 | 1.000 | 0.970 | 1.000 |
| direct-s42 | 190 | 0.570 | 1.000 | 0.940 | 1.000 |
| encoder-modernbert-large-s1 | 190 | 0.100 | 1.000 | 0.920 | 1.000 |
| encoder-modernbert-large-s3 | 190 | 0.493 | 1.000 | 0.970 | 1.000 |
| encoder-modernbert-large-s4 | 190 | 0.000 | 1.000 | 0.980 | 1.000 |
| encoder-modernbert-large-s42 | 190 | 0.006 | 1.000 | 0.920 | 1.000 |
| encoder-modernbert-large-s5 | 190 | 0.040 | 1.000 | 0.860 | 1.000 |
| judge-claude-haiku-4-5 | 190 | 0.358 | 1.000 | 0.200 | 0.000 |
| judge-gpt-5.4-mini | 190 | 0.848 | 1.000 | 0.100 | 0.000 |
| judge-gpt-5.5-fewshot-sd | 190 | 0.972 | 0.800 | 0.590 | 0.000 |
| judge-gpt-5.5-reasoning | 190 | 0.957 | 0.722 | 0.350 | 0.000 |
| judge-gpt-5.5 | 190 | 0.927 | 0.867 | 0.460 | 0.000 |
| judge-grok-4.3-sd | 190 | 0.405 | 1.000 | 0.230 | 0.322 |
| static | 190 | 0.599 | 1.000 | 0.300 | 0.122 |
| typesafe | 190 | 0.107 | 1.000 | 0.000 | 0.000 |
| untuned-r002 | 190 | 0.059 | 1.000 | 0.000 | 0.000 |
| word-svm-r002 | 190 | 0.907 | 0.978 | 0.630 | 0.000 |

| source | label | skills | ours flagged | direct-s42 flagged |
|---|---|---|---|---|
| SkillFortifyBench | benign | 90 | 48 | 90 |
| SkillHarm | malicious | 100 | 79 | 94 |

Cascade (direct-s42 flags, then ours must also flag): recall 0.750, FPR 0.533
```

## sd-heldout.txt

```
train skills: 300, validation skills: 400, test skills: 1384 (839 malicious, 545 benign)

| combiner | threshold (from validation) | test AUC [95% CI] | test TPR [95% CI] | test FPR [95% CI] | unscored |
|---|---|---|---|---|---|
| max | 0.184 | 0.672 [0.642, 0.702] | 0.380 [0.347, 0.413] | 0.196 [0.162, 0.230] | 0 |
| AST04 | 0.078 | 0.615 [0.584, 0.644] | 0.391 [0.358, 0.423] | 0.272 [0.233, 0.310] | 0 |
| logreg | 0.752 | 0.658 [0.628, 0.688] | 0.309 [0.278, 0.341] | 0.138 [0.109, 0.165] | 0 |
| baseline | 0.079 | 0.518 [0.487, 0.549] | 0.117 [0.096, 0.138] | 0.013 [0.004, 0.022] | 0 |

| paired difference on test | AUC diff [95% CI] |
|---|---|
| logreg - max | -0.014 [-0.027, -0.002] |
| AST04 - max | -0.057 [-0.091, -0.026] |
| logreg - AST04 | +0.043 [+0.018, +0.070] |

| logreg weight | intercept | AST01 | AST02 | AST03 | AST04 | AST05 |
|---|---|---|---|---|---|---|
| value | -0.64 | +1.28 | +3.08 | +3.67 | +6.42 | +1.81 |

| combiner | threshold rule (on validation) | threshold | test TPR [95% CI] | test FPR [95% CI] |
|---|---|---|---|---|
| max | tpr95 | 0.085 | 0.889 [0.867, 0.910] | 0.721 [0.683, 0.757] |
| max | fpr05 | 0.264 | 0.238 [0.211, 0.267] | 0.086 [0.064, 0.109] |
| AST04 | tpr95 | 0.055 | 0.831 [0.806, 0.855] | 0.769 [0.734, 0.804] |
| AST04 | fpr05 | 0.132 | 0.172 [0.147, 0.197] | 0.040 [0.025, 0.058] |
| logreg | tpr95 | 0.589 | 0.878 [0.855, 0.901] | 0.725 [0.685, 0.761] |
| logreg | fpr05 | 0.852 | 0.169 [0.144, 0.196] | 0.046 [0.029, 0.064] |
| baseline | tpr95 | 0.021 | 0.827 [0.802, 0.853] | 0.888 [0.862, 0.914] |
| baseline | fpr05 | 0.071 | 0.120 [0.100, 0.142] | 0.026 [0.013, 0.040] |

Baseline generic-1q: test AUC 0.518 [0.487, 0.549]

| paired difference on test | AUC diff [95% CI] |
|---|---|
| logreg - generic-1q | +0.139 [+0.105, +0.172] |
| AST04 - generic-1q | +0.096 [+0.059, +0.130] |
| max - generic-1q | +0.154 [+0.117, +0.189] |
```

## sd-compare-AST04.txt

```
Skills compared: 1384 of SkillScreen's 1384. Ours cut at 0.1324, theirs at 0.5.

| method | skills | AUROC | FPR@99 | recall | FPR |
|---|---|---|---|---|---|
| ours | 1384 | 0.615 | 0.987 | 0.172 | 0.040 |
| direct-s1 | 1384 | 0.931 | 0.510 | 0.980 | 0.393 |
| direct-s2 | 1384 | 0.919 | 0.475 | 0.977 | 0.328 |
| direct-s3 | 1384 | 0.893 | 0.521 | 0.963 | 0.310 |
| direct-s4 | 1384 | 0.935 | 0.459 | 0.985 | 0.413 |
| direct-s42 | 1384 | 0.903 | 0.561 | 0.961 | 0.354 |
| encoder-modernbert-large-s1 | 1384 | 0.738 | 0.903 | 0.946 | 0.598 |
| encoder-modernbert-large-s3 | 1384 | 0.854 | 0.607 | 0.975 | 0.530 |
| encoder-modernbert-large-s4 | 1384 | 0.815 | 0.541 | 0.990 | 0.563 |
| encoder-modernbert-large-s42 | 1384 | 0.760 | 0.789 | 0.928 | 0.495 |
| encoder-modernbert-large-s5 | 1384 | 0.680 | 0.894 | 0.867 | 0.550 |
| judge-claude-haiku-4-5 | 1384 | 0.732 | 0.998 | 0.288 | 0.006 |
| judge-gpt-5.4-mini | 1384 | 0.768 | 1.000 | 0.230 | 0.009 |
| judge-gpt-5.5-fewshot-sd | 1384 | 0.941 | 0.798 | 0.604 | 0.022 |
| judge-gpt-5.5-reasoning | 1384 | 0.932 | 1.000 | 0.337 | 0.011 |
| judge-gpt-5.5 | 1384 | 0.914 | 1.000 | 0.428 | 0.009 |
| judge-grok-4.3-sd | 1384 | 0.614 | 0.976 | 0.364 | 0.213 |
| static | 1384 | 0.433 | 1.000 | 0.315 | 0.429 |
| typesafe | 1384 | 0.652 | 1.000 | 0.113 | 0.000 |
| untuned-r002 | 1384 | 0.568 | 0.998 | 0.006 | 0.000 |
| word-svm-r002 | 1384 | 0.809 | 0.822 | 0.620 | 0.183 |

| source | label | skills | ours flagged | direct-s42 flagged |
|---|---|---|---|---|
| ATR Skill Security Benchmark | malicious | 21 | 14 | 21 |
| ATR Skill Security Benchmark | benign | 455 | 10 | 103 |
| SkillFortifyBench | malicious | 90 | 71 | 90 |
| SkillFortifyBench | benign | 90 | 12 | 90 |
| SkillHarm | malicious | 728 | 59 | 695 |

Cascade (direct-s42 flags, then ours must also flag): recall 0.170, FPR 0.031
Paired AUROC, ours - runs/exp004/sd-generic.csv: 0.096 [0.059, 0.130] on 1384 skills
Paired AUROC, ours - typesafe: -0.037 [-0.069, -0.003] on 1384 skills
Paired AUROC, ours - judge-gpt-5.5: -0.300 [-0.332, -0.271] on 1384 skills
Paired AUROC, ours - direct-s42: -0.289 [-0.320, -0.259] on 1384 skills
```

## sd-compare-logreg.txt

```
Skills compared: 1384 of SkillScreen's 1384. Ours cut at 0.8524045530096916, theirs at 0.5.

| method | skills | AUROC | FPR@99 | recall | FPR |
|---|---|---|---|---|---|
| ours | 1384 | 0.658 | 0.971 | 0.169 | 0.046 |
| direct-s1 | 1384 | 0.931 | 0.510 | 0.980 | 0.393 |
| direct-s2 | 1384 | 0.919 | 0.475 | 0.977 | 0.328 |
| direct-s3 | 1384 | 0.893 | 0.521 | 0.963 | 0.310 |
| direct-s4 | 1384 | 0.935 | 0.459 | 0.985 | 0.413 |
| direct-s42 | 1384 | 0.903 | 0.561 | 0.961 | 0.354 |
| encoder-modernbert-large-s1 | 1384 | 0.738 | 0.903 | 0.946 | 0.598 |
| encoder-modernbert-large-s3 | 1384 | 0.854 | 0.607 | 0.975 | 0.530 |
| encoder-modernbert-large-s4 | 1384 | 0.815 | 0.541 | 0.990 | 0.563 |
| encoder-modernbert-large-s42 | 1384 | 0.760 | 0.789 | 0.928 | 0.495 |
| encoder-modernbert-large-s5 | 1384 | 0.680 | 0.894 | 0.867 | 0.550 |
| judge-claude-haiku-4-5 | 1384 | 0.732 | 0.998 | 0.288 | 0.006 |
| judge-gpt-5.4-mini | 1384 | 0.768 | 1.000 | 0.230 | 0.009 |
| judge-gpt-5.5-fewshot-sd | 1384 | 0.941 | 0.798 | 0.604 | 0.022 |
| judge-gpt-5.5-reasoning | 1384 | 0.932 | 1.000 | 0.337 | 0.011 |
| judge-gpt-5.5 | 1384 | 0.914 | 1.000 | 0.428 | 0.009 |
| judge-grok-4.3-sd | 1384 | 0.614 | 0.976 | 0.364 | 0.213 |
| static | 1384 | 0.433 | 1.000 | 0.315 | 0.429 |
| typesafe | 1384 | 0.652 | 1.000 | 0.113 | 0.000 |
| untuned-r002 | 1384 | 0.568 | 0.998 | 0.006 | 0.000 |
| word-svm-r002 | 1384 | 0.809 | 0.822 | 0.620 | 0.183 |

| source | label | skills | ours flagged | direct-s42 flagged |
|---|---|---|---|---|
| ATR Skill Security Benchmark | malicious | 21 | 18 | 21 |
| ATR Skill Security Benchmark | benign | 455 | 24 | 103 |
| SkillFortifyBench | malicious | 90 | 85 | 90 |
| SkillFortifyBench | benign | 90 | 1 | 90 |
| SkillHarm | malicious | 728 | 39 | 695 |

Cascade (direct-s42 flags, then ours must also flag): recall 0.169, FPR 0.011
Paired AUROC, ours - runs/exp004/sd-generic.csv: 0.139 [0.105, 0.172] on 1384 skills
Paired AUROC, ours - typesafe: 0.006 [-0.027, 0.039] on 1384 skills
Paired AUROC, ours - judge-gpt-5.5: -0.257 [-0.285, -0.229] on 1384 skills
Paired AUROC, ours - direct-s42: -0.246 [-0.279, -0.213] on 1384 skills
```

## sd-compare-max.txt

```
Skills compared: 1384 of SkillScreen's 1384. Ours cut at 0.2637, theirs at 0.5.

| method | skills | AUROC | FPR@99 | recall | FPR |
|---|---|---|---|---|---|
| ours | 1384 | 0.672 | 0.952 | 0.238 | 0.086 |
| direct-s1 | 1384 | 0.931 | 0.510 | 0.980 | 0.393 |
| direct-s2 | 1384 | 0.919 | 0.475 | 0.977 | 0.328 |
| direct-s3 | 1384 | 0.893 | 0.521 | 0.963 | 0.310 |
| direct-s4 | 1384 | 0.935 | 0.459 | 0.985 | 0.413 |
| direct-s42 | 1384 | 0.903 | 0.561 | 0.961 | 0.354 |
| encoder-modernbert-large-s1 | 1384 | 0.738 | 0.903 | 0.946 | 0.598 |
| encoder-modernbert-large-s3 | 1384 | 0.854 | 0.607 | 0.975 | 0.530 |
| encoder-modernbert-large-s4 | 1384 | 0.815 | 0.541 | 0.990 | 0.563 |
| encoder-modernbert-large-s42 | 1384 | 0.760 | 0.789 | 0.928 | 0.495 |
| encoder-modernbert-large-s5 | 1384 | 0.680 | 0.894 | 0.867 | 0.550 |
| judge-claude-haiku-4-5 | 1384 | 0.732 | 0.998 | 0.288 | 0.006 |
| judge-gpt-5.4-mini | 1384 | 0.768 | 1.000 | 0.230 | 0.009 |
| judge-gpt-5.5-fewshot-sd | 1384 | 0.941 | 0.798 | 0.604 | 0.022 |
| judge-gpt-5.5-reasoning | 1384 | 0.932 | 1.000 | 0.337 | 0.011 |
| judge-gpt-5.5 | 1384 | 0.914 | 1.000 | 0.428 | 0.009 |
| judge-grok-4.3-sd | 1384 | 0.614 | 0.976 | 0.364 | 0.213 |
| static | 1384 | 0.433 | 1.000 | 0.315 | 0.429 |
| typesafe | 1384 | 0.652 | 1.000 | 0.113 | 0.000 |
| untuned-r002 | 1384 | 0.568 | 0.998 | 0.006 | 0.000 |
| word-svm-r002 | 1384 | 0.809 | 0.822 | 0.620 | 0.183 |

| source | label | skills | ours flagged | direct-s42 flagged |
|---|---|---|---|---|
| ATR Skill Security Benchmark | malicious | 21 | 18 | 21 |
| ATR Skill Security Benchmark | benign | 455 | 45 | 103 |
| SkillFortifyBench | malicious | 90 | 85 | 90 |
| SkillFortifyBench | benign | 90 | 2 | 90 |
| SkillHarm | malicious | 728 | 97 | 695 |

Cascade (direct-s42 flags, then ours must also flag): recall 0.234, FPR 0.020
Paired AUROC, ours - runs/exp004/sd-generic.csv: 0.154 [0.117, 0.189] on 1384 skills
Paired AUROC, ours - typesafe: 0.020 [-0.016, 0.054] on 1384 skills
Paired AUROC, ours - judge-gpt-5.5: -0.243 [-0.271, -0.215] on 1384 skills
Paired AUROC, ours - direct-s42: -0.232 [-0.266, -0.197] on 1384 skills
```

## msd-heldout.txt

```
train skills: 300, validation skills: 400, test skills: 1947 (1500 malicious, 447 benign)

| combiner | threshold (from validation) | test AUC [95% CI] | test TPR [95% CI] | test FPR [95% CI] | unscored |
|---|---|---|---|---|---|
| max | 0.214 | 0.824 [0.805, 0.842] | 0.618 [0.592, 0.644] | 0.116 [0.089, 0.147] | 1 |
| AST04 | 0.091 | 0.826 [0.807, 0.844] | 0.680 [0.656, 0.702] | 0.141 [0.110, 0.174] | 1 |
| logreg | 0.755 | 0.831 [0.813, 0.849] | 0.638 [0.614, 0.663] | 0.107 [0.080, 0.137] | 1 |
| baseline | 0.068 | 0.703 [0.678, 0.725] | 0.382 [0.355, 0.407] | 0.040 [0.023, 0.059] | 1 |

| paired difference on test | AUC diff [95% CI] |
|---|---|
| logreg - max | +0.007 [-0.002, +0.016] |
| AST04 - max | +0.002 [-0.017, +0.022] |
| logreg - AST04 | +0.005 [-0.010, +0.020] |

| logreg weight | intercept | AST01 | AST02 | AST03 | AST04 | AST05 |
|---|---|---|---|---|---|---|
| value | -0.18 | +1.30 | +2.33 | +3.50 | +4.11 | +0.22 |

| combiner | threshold rule (on validation) | threshold | test TPR [95% CI] | test FPR [95% CI] |
|---|---|---|---|---|
| max | tpr95 | 0.099 | 0.904 [0.889, 0.918] | 0.588 [0.544, 0.633] |
| max | fpr05 | 0.265 | 0.552 [0.526, 0.578] | 0.063 [0.041, 0.085] |
| AST04 | tpr95 | 0.056 | 0.930 [0.916, 0.942] | 0.758 [0.720, 0.797] |
| AST04 | fpr05 | 0.154 | 0.480 [0.455, 0.506] | 0.025 [0.011, 0.040] |
| logreg | tpr95 | 0.637 | 0.923 [0.909, 0.935] | 0.691 [0.648, 0.733] |
| logreg | fpr05 | 0.775 | 0.600 [0.575, 0.624] | 0.067 [0.045, 0.091] |
| baseline | tpr95 | 0.020 | 0.930 [0.916, 0.942] | 0.924 [0.898, 0.947] |
| baseline | fpr05 | 0.071 | 0.372 [0.346, 0.395] | 0.038 [0.021, 0.057] |

Baseline generic-1q: test AUC 0.703 [0.678, 0.725]

| paired difference on test | AUC diff [95% CI] |
|---|---|
| logreg - generic-1q | +0.129 [+0.105, +0.152] |
| AST04 - generic-1q | +0.123 [+0.099, +0.150] |
| max - generic-1q | +0.121 [+0.096, +0.146] |
```

## msd-compare-AST04.txt

```
Skills compared: 1947 of SkillScreen's 1947. Ours cut at 0.1545, theirs at 0.5.

| method | skills | AUROC | FPR@99 | recall | FPR |
|---|---|---|---|---|---|
| ours | 1947 | 0.826 | 0.982 | 0.481 | 0.025 |
| direct-s1 | 1947 | 0.991 | 0.242 | 0.965 | 0.051 |
| direct-s2 | 1947 | 0.993 | 0.199 | 0.954 | 0.038 |
| direct-s3 | 1947 | 0.992 | 0.221 | 0.951 | 0.031 |
| direct-s4 | 1947 | 0.992 | 0.221 | 0.961 | 0.027 |
| direct | 1947 | 0.992 | 0.246 | 0.952 | 0.018 |
| encoder-modernbert-large-gpu-s1 | 1947 | 0.990 | 0.289 | 0.959 | 0.038 |
| encoder-modernbert-large-gpu-s2 | 1947 | 0.990 | 0.304 | 0.959 | 0.038 |
| encoder-modernbert-large-gpu-s3 | 1947 | 0.989 | 0.313 | 0.960 | 0.036 |
| encoder-modernbert-large-gpu-s4 | 1947 | 0.990 | 0.251 | 0.967 | 0.072 |
| encoder-modernbert-large-gpu-s42 | 1947 | 0.989 | 0.362 | 0.955 | 0.022 |
| judge-claude-haiku-4-5 | 1947 | 0.862 | 0.926 | 0.659 | 0.029 |
| judge-gpt-5.4-mini | 1947 | 0.862 | 1.000 | 0.563 | 0.025 |
| judge-gpt-5.5-fewshot | 1947 | 0.958 | 0.957 | 0.879 | 0.025 |
| judge-gpt-5.5-reasoning | 1947 | 0.953 | 0.868 | 0.711 | 0.013 |
| judge-gpt-5.5 | 1947 | 0.950 | 0.911 | 0.721 | 0.007 |
| judge-grok-4.3 | 1947 | 0.707 | 0.966 | 0.681 | 0.280 |
| static | 1947 | 0.618 | 1.000 | 0.494 | 0.322 |
| typesafe | 1947 | 0.841 | 1.000 | 0.338 | 0.002 |
| untuned | 1947 | 0.678 | 0.955 | 0.042 | 0.000 |
| word-svm | 1947 | 0.977 | 0.456 | 0.782 | 0.011 |

| source | label | skills | ours flagged | direct flagged |
|---|---|---|---|---|
| ATR Skill Security Benchmark | malicious | 5 | 3 | 4 |
| ATR Skill Security Benchmark | benign | 83 | 0 | 4 |
| Agent Skill Malware | malicious | 7 | 0 | 6 |
| AgentTrap | malicious | 22 | 2 | 11 |
| AgentTrap | benign | 11 | 0 | 1 |
| MalSkillBench | malicious | 967 | 646 | 938 |
| MaliciousAgentSkillsBench | malicious | 61 | 5 | 42 |
| SkillFortifyBench | malicious | 2 | 1 | 2 |
| SkillFortifyBench | benign | 13 | 1 | 0 |
| SkillHarm | malicious | 92 | 2 | 92 |
| SkillLeakBench | malicious | 9 | 2 | 1 |
| SkillSafetyBench | malicious | 11 | 2 | 10 |
| SkillTrojan | benign | 2 | 0 | 0 |
| SkillTrustBench | malicious | 324 | 58 | 322 |
| SkillTrustBench | benign | 338 | 10 | 3 |

Cascade (direct flags, then ours must also flag): recall 0.471, FPR 0.000
Paired AUROC, ours - runs/exp004/msd-generic.csv: 0.123 [0.099, 0.150] on 1946 skills
Paired AUROC, ours - typesafe: -0.015 [-0.034, 0.005] on 1946 skills
Paired AUROC, ours - judge-gpt-5.5: -0.124 [-0.142, -0.106] on 1946 skills
Paired AUROC, ours - direct: -0.166 [-0.184, -0.147] on 1946 skills
```

## msd-compare-logreg.txt

```
Skills compared: 1947 of SkillScreen's 1947. Ours cut at 0.7753830101820911, theirs at 0.5.

| method | skills | AUROC | FPR@99 | recall | FPR |
|---|---|---|---|---|---|
| ours | 1947 | 0.831 | 0.944 | 0.600 | 0.067 |
| direct-s1 | 1947 | 0.991 | 0.242 | 0.965 | 0.051 |
| direct-s2 | 1947 | 0.993 | 0.199 | 0.954 | 0.038 |
| direct-s3 | 1947 | 0.992 | 0.221 | 0.951 | 0.031 |
| direct-s4 | 1947 | 0.992 | 0.221 | 0.961 | 0.027 |
| direct | 1947 | 0.992 | 0.246 | 0.952 | 0.018 |
| encoder-modernbert-large-gpu-s1 | 1947 | 0.990 | 0.289 | 0.959 | 0.038 |
| encoder-modernbert-large-gpu-s2 | 1947 | 0.990 | 0.304 | 0.959 | 0.038 |
| encoder-modernbert-large-gpu-s3 | 1947 | 0.989 | 0.313 | 0.960 | 0.036 |
| encoder-modernbert-large-gpu-s4 | 1947 | 0.990 | 0.251 | 0.967 | 0.072 |
| encoder-modernbert-large-gpu-s42 | 1947 | 0.989 | 0.362 | 0.955 | 0.022 |
| judge-claude-haiku-4-5 | 1947 | 0.862 | 0.926 | 0.659 | 0.029 |
| judge-gpt-5.4-mini | 1947 | 0.862 | 1.000 | 0.563 | 0.025 |
| judge-gpt-5.5-fewshot | 1947 | 0.958 | 0.957 | 0.879 | 0.025 |
| judge-gpt-5.5-reasoning | 1947 | 0.953 | 0.868 | 0.711 | 0.013 |
| judge-gpt-5.5 | 1947 | 0.950 | 0.911 | 0.721 | 0.007 |
| judge-grok-4.3 | 1947 | 0.707 | 0.966 | 0.681 | 0.280 |
| static | 1947 | 0.618 | 1.000 | 0.494 | 0.322 |
| typesafe | 1947 | 0.841 | 1.000 | 0.338 | 0.002 |
| untuned | 1947 | 0.678 | 0.955 | 0.042 | 0.000 |
| word-svm | 1947 | 0.977 | 0.456 | 0.782 | 0.011 |

| source | label | skills | ours flagged | direct flagged |
|---|---|---|---|---|
| ATR Skill Security Benchmark | malicious | 5 | 5 | 4 |
| ATR Skill Security Benchmark | benign | 83 | 3 | 4 |
| Agent Skill Malware | malicious | 7 | 1 | 6 |
| AgentTrap | malicious | 22 | 2 | 11 |
| AgentTrap | benign | 11 | 0 | 1 |
| MalSkillBench | malicious | 967 | 789 | 938 |
| MaliciousAgentSkillsBench | malicious | 61 | 32 | 42 |
| SkillFortifyBench | malicious | 2 | 2 | 2 |
| SkillFortifyBench | benign | 13 | 0 | 0 |
| SkillHarm | malicious | 92 | 6 | 92 |
| SkillLeakBench | malicious | 9 | 3 | 1 |
| SkillSafetyBench | malicious | 11 | 1 | 10 |
| SkillTrojan | benign | 2 | 0 | 0 |
| SkillTrustBench | malicious | 324 | 59 | 322 |
| SkillTrustBench | benign | 338 | 27 | 3 |

Cascade (direct flags, then ours must also flag): recall 0.587, FPR 0.000
Paired AUROC, ours - runs/exp004/msd-generic.csv: 0.129 [0.105, 0.152] on 1946 skills
Paired AUROC, ours - typesafe: -0.010 [-0.028, 0.009] on 1946 skills
Paired AUROC, ours - judge-gpt-5.5: -0.119 [-0.137, -0.103] on 1946 skills
Paired AUROC, ours - direct: -0.161 [-0.179, -0.144] on 1946 skills
```

## msd-compare-max.txt

```
Skills compared: 1947 of SkillScreen's 1947. Ours cut at 0.2649, theirs at 0.5.

| method | skills | AUROC | FPR@99 | recall | FPR |
|---|---|---|---|---|---|
| ours | 1947 | 0.824 | 0.924 | 0.552 | 0.063 |
| direct-s1 | 1947 | 0.991 | 0.242 | 0.965 | 0.051 |
| direct-s2 | 1947 | 0.993 | 0.199 | 0.954 | 0.038 |
| direct-s3 | 1947 | 0.992 | 0.221 | 0.951 | 0.031 |
| direct-s4 | 1947 | 0.992 | 0.221 | 0.961 | 0.027 |
| direct | 1947 | 0.992 | 0.246 | 0.952 | 0.018 |
| encoder-modernbert-large-gpu-s1 | 1947 | 0.990 | 0.289 | 0.959 | 0.038 |
| encoder-modernbert-large-gpu-s2 | 1947 | 0.990 | 0.304 | 0.959 | 0.038 |
| encoder-modernbert-large-gpu-s3 | 1947 | 0.989 | 0.313 | 0.960 | 0.036 |
| encoder-modernbert-large-gpu-s4 | 1947 | 0.990 | 0.251 | 0.967 | 0.072 |
| encoder-modernbert-large-gpu-s42 | 1947 | 0.989 | 0.362 | 0.955 | 0.022 |
| judge-claude-haiku-4-5 | 1947 | 0.862 | 0.926 | 0.659 | 0.029 |
| judge-gpt-5.4-mini | 1947 | 0.862 | 1.000 | 0.563 | 0.025 |
| judge-gpt-5.5-fewshot | 1947 | 0.958 | 0.957 | 0.879 | 0.025 |
| judge-gpt-5.5-reasoning | 1947 | 0.953 | 0.868 | 0.711 | 0.013 |
| judge-gpt-5.5 | 1947 | 0.950 | 0.911 | 0.721 | 0.007 |
| judge-grok-4.3 | 1947 | 0.707 | 0.966 | 0.681 | 0.280 |
| static | 1947 | 0.618 | 1.000 | 0.494 | 0.322 |
| typesafe | 1947 | 0.841 | 1.000 | 0.338 | 0.002 |
| untuned | 1947 | 0.678 | 0.955 | 0.042 | 0.000 |
| word-svm | 1947 | 0.977 | 0.456 | 0.782 | 0.011 |

| source | label | skills | ours flagged | direct flagged |
|---|---|---|---|---|
| ATR Skill Security Benchmark | malicious | 5 | 4 | 4 |
| ATR Skill Security Benchmark | benign | 83 | 8 | 4 |
| Agent Skill Malware | malicious | 7 | 0 | 6 |
| AgentTrap | malicious | 22 | 2 | 11 |
| AgentTrap | benign | 11 | 1 | 1 |
| MalSkillBench | malicious | 967 | 728 | 938 |
| MaliciousAgentSkillsBench | malicious | 61 | 31 | 42 |
| SkillFortifyBench | malicious | 2 | 2 | 2 |
| SkillFortifyBench | benign | 13 | 0 | 0 |
| SkillHarm | malicious | 92 | 22 | 92 |
| SkillLeakBench | malicious | 9 | 3 | 1 |
| SkillSafetyBench | malicious | 11 | 0 | 10 |
| SkillTrojan | benign | 2 | 1 | 0 |
| SkillTrustBench | malicious | 324 | 36 | 322 |
| SkillTrustBench | benign | 338 | 18 | 3 |

Cascade (direct flags, then ours must also flag): recall 0.541, FPR 0.004
Paired AUROC, ours - runs/exp004/msd-generic.csv: 0.121 [0.096, 0.146] on 1946 skills
Paired AUROC, ours - typesafe: -0.017 [-0.038, 0.003] on 1946 skills
Paired AUROC, ours - judge-gpt-5.5: -0.126 [-0.144, -0.109] on 1946 skills
Paired AUROC, ours - direct: -0.168 [-0.188, -0.150] on 1946 skills
```

## Progress log

```
[2026-10-19 11:45:42] start
[2026-10-19 11:45:45] backend: OpenRouter cloudflare/clef-flash on provider cloudflare, served as cloudflare/clef-flash|Cloudflare|unpinned, state sent as a string
[2026-10-19 11:45:45] note: OpenRouter returned no dated version for cloudflare/clef-flash; a silent model change would not be detected
[2026-10-19 11:46:06] context check: source_disjoint: longest test skill sent as 44684 characters (cut at 60,000: False); model read 11169 input tokens m_structural_disjoint: longest test skill (60000 characters) was refused: OpenRouter HTTP 422: {"error":{"message":"HTTP 422: {\"errors\":[{\"message\":\"AiError: AiError: Request requires 31548 tokens; the maximum is 24576 (bb6fe0f4-17c2-4c30-82e6-6ded8bc9f7d7)\",\"code\":3030}],\"success\":false,\"result\":{},\"messages\":[]}","code":422}} <- WARNING: long skills will be unscored 
190 ids -> runs/exp004/probe-ids.txt
[2026-10-19 11:46:06] probe: running (spent so far $0)
runs/exp004/probe
[2026-10-19 11:49:50] probe: done (380 predictions, spent so far $0.0506)
[2026-10-19 11:49:51] sd-train: running (spent so far $0.0506)
runs/exp004/sd-train
[2026-10-19 11:53:26] sd-train: done (600 predictions, spent so far $0.1771)
[2026-10-19 11:53:26] sd-validation: running (spent so far $0.1771)
runs/exp004/sd-validation
[2026-10-19 11:58:08] sd-validation: done (800 predictions, spent so far $0.3528)
[2026-10-19 11:58:09] sd-test: running (spent so far $0.3528)
runs/exp004/sd-test
[2026-10-19 12:14:17] sd-test: done (2768 predictions, spent so far $0.9027)
[2026-10-19 12:20:14] sd: analysis written
[2026-10-19 12:20:14] msd-train: running (spent so far $0.9027)
runs/exp004/msd-train
[2026-10-19 12:24:04] msd-train: done (600 predictions, spent so far $1.0444)
[2026-10-19 12:24:05] msd-validation: running (spent so far $1.0444)
runs/exp004/msd-validation
[2026-10-19 12:28:25] msd-validation: done (800 predictions, spent so far $1.2048)
[2026-10-19 12:28:25] msd-test: running (spent so far $1.2048)
runs/exp004/msd-test
[2026-10-19 12:49:06] msd-test: done (3894 predictions, spent so far $2.0143)
[2026-10-19 12:57:54] msd: analysis written
```
