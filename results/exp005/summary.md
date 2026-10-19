# Experiment 005 results, 2026-10-19 11:51:28

Model: OpenRouter cloudflare/clef-flash on provider cloudflare, served as cloudflare/clef-flash|Cloudflare|unpinned, state sent as a string. Spent: $2.367. Commit: 41c4805.

## data-verify-after.txt

```
     match  primary.parquet
     match  splits/m_structural_disjoint.parquet
not pinned  splits/random.parquet
     match  splits/source_disjoint.parquet
```

## data-verify-before.txt

```
     match  primary.parquet
     match  splits/m_structural_disjoint.parquet
not pinned  splits/random.parquet
     match  splits/source_disjoint.parquet
```

## context-check.txt

```
source_disjoint: longest test skill sent as 44684 characters (cut at 60,000: False); model read 11169 input tokens
m_structural_disjoint: longest test skill (60000 characters) was refused: OpenRouter HTTP 422: {"error":{"message":"HTTP 422: {\"errors\":[{\"message\":\"AiError: AiError: Request requires 31548 tokens; the maximum is 24576 (6aff1130-a84f-40a3-bef6-c8c825d0ad49)\",\"code\":3030}],\"success\":false,\"result\":{},\"messages\":[]}","code":422}} <- WARNING: long skills will be unscored
```

## sd-heldout-ast10.txt

```
train skills: 300, validation skills: 400, test skills: 1384 (839 malicious, 545 benign)

| combiner | threshold (from validation) | test AUC [95% CI] | test TPR [95% CI] | test FPR [95% CI] | unscored |
|---|---|---|---|---|---|
| max | 0.215 | 0.656 [0.628, 0.685] | 0.324 [0.291, 0.357] | 0.128 [0.100, 0.156] | 0 |
| AST04 | 0.094 | 0.524 [0.492, 0.554] | 0.195 [0.168, 0.223] | 0.145 [0.116, 0.175] | 0 |
| logreg | 0.711 | 0.584 [0.554, 0.615] | 0.496 [0.463, 0.529] | 0.420 [0.379, 0.462] | 0 |
| baseline | 0.079 | 0.518 [0.488, 0.549] | 0.117 [0.095, 0.139] | 0.013 [0.004, 0.023] | 0 |

| paired difference on test | AUC diff [95% CI] |
|---|---|
| logreg - max | -0.073 [-0.092, -0.054] |
| AST04 - max | -0.132 [-0.179, -0.085] |
| logreg - AST04 | +0.060 [+0.020, +0.099] |

| logreg weight | intercept | AST01 | AST02 | AST03 | AST04 | AST05 |
|---|---|---|---|---|---|---|
| value | -0.53 | +2.70 | +3.25 | +3.20 | +5.85 | +1.89 |

| combiner | threshold rule (on validation) | threshold | test TPR [95% CI] | test FPR [95% CI] |
|---|---|---|---|---|
| max | tpr95 | 0.104 | 0.912 [0.892, 0.930] | 0.787 [0.752, 0.824] |
| max | fpr05 | 0.238 | 0.293 [0.263, 0.326] | 0.097 [0.072, 0.123] |
| AST04 | tpr95 | 0.051 | 0.920 [0.901, 0.939] | 0.888 [0.861, 0.914] |
| AST04 | fpr05 | 0.146 | 0.082 [0.064, 0.102] | 0.011 [0.004, 0.021] |
| logreg | tpr95 | 0.651 | 0.883 [0.861, 0.904] | 0.815 [0.780, 0.848] |
| logreg | fpr05 | 0.823 | 0.162 [0.138, 0.188] | 0.040 [0.025, 0.057] |
| baseline | tpr95 | 0.021 | 0.827 [0.800, 0.853] | 0.888 [0.862, 0.913] |
| baseline | fpr05 | 0.071 | 0.120 [0.098, 0.143] | 0.026 [0.013, 0.039] |

Baseline generic-1q: test AUC 0.518 [0.488, 0.549]

| paired difference on test | AUC diff [95% CI] |
|---|---|
| logreg - generic-1q | +0.066 [+0.031, +0.104] |
| AST04 - generic-1q | +0.006 [-0.036, +0.048] |
| max - generic-1q | +0.138 [+0.102, +0.177] |
```

## sd-heldout.txt

```
train skills: 300, validation skills: 400, test skills: 1384 (839 malicious, 545 benign)

| combiner | threshold (from validation) | test AUC [95% CI] | test TPR [95% CI] | test FPR [95% CI] | unscored |
|---|---|---|---|---|---|
| max | 0.184 | 0.672 [0.642, 0.699] | 0.380 [0.345, 0.413] | 0.196 [0.165, 0.232] | 0 |
| AST04 | 0.078 | 0.615 [0.583, 0.643] | 0.391 [0.358, 0.424] | 0.272 [0.236, 0.310] | 0 |
| logreg | 0.752 | 0.658 [0.628, 0.685] | 0.309 [0.279, 0.338] | 0.138 [0.110, 0.168] | 0 |
| baseline | 0.079 | 0.518 [0.488, 0.549] | 0.117 [0.095, 0.139] | 0.013 [0.004, 0.023] | 0 |

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
| max | tpr95 | 0.085 | 0.889 [0.867, 0.910] | 0.721 [0.682, 0.760] |
| max | fpr05 | 0.264 | 0.238 [0.210, 0.268] | 0.086 [0.064, 0.110] |
| AST04 | tpr95 | 0.055 | 0.831 [0.805, 0.856] | 0.769 [0.733, 0.805] |
| AST04 | fpr05 | 0.132 | 0.172 [0.146, 0.196] | 0.040 [0.025, 0.057] |
| logreg | tpr95 | 0.589 | 0.878 [0.855, 0.900] | 0.725 [0.687, 0.763] |
| logreg | fpr05 | 0.852 | 0.169 [0.144, 0.195] | 0.046 [0.029, 0.064] |
| baseline | tpr95 | 0.021 | 0.827 [0.800, 0.853] | 0.888 [0.862, 0.913] |
| baseline | fpr05 | 0.071 | 0.120 [0.098, 0.143] | 0.026 [0.013, 0.039] |

Baseline generic-1q: test AUC 0.518 [0.488, 0.549]

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
Paired AUROC, ours - runs/exp005/sd-generic.csv: 0.096 [0.059, 0.130] on 1384 skills
Paired AUROC, ours - typesafe: -0.037 [-0.069, -0.003] on 1384 skills
Paired AUROC, ours - judge-gpt-5.5: -0.300 [-0.332, -0.271] on 1384 skills
Paired AUROC, ours - direct-s42: -0.289 [-0.320, -0.259] on 1384 skills
```

## sd-compare-ast10.txt

```
Skills compared: 1384 of SkillScreen's 1384. Ours cut at 0.238, theirs at 0.5.

| method | skills | AUROC | FPR@99 | recall | FPR |
|---|---|---|---|---|---|
| ours | 1384 | 0.656 | 0.961 | 0.293 | 0.097 |
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
| ATR Skill Security Benchmark | malicious | 21 | 17 | 21 |
| ATR Skill Security Benchmark | benign | 455 | 53 | 103 |
| SkillFortifyBench | malicious | 90 | 85 | 90 |
| SkillFortifyBench | benign | 90 | 0 | 90 |
| SkillHarm | malicious | 728 | 144 | 695 |

Cascade (direct-s42 flags, then ours must also flag): recall 0.278, FPR 0.015
Paired AUROC, ours - runs/exp005/sd-generic.csv: 0.138 [0.102, 0.177] on 1384 skills
Paired AUROC, ours - typesafe: 0.005 [-0.035, 0.043] on 1384 skills
Paired AUROC, ours - judge-gpt-5.5: -0.258 [-0.288, -0.229] on 1384 skills
Paired AUROC, ours - direct-s42: -0.247 [-0.283, -0.212] on 1384 skills
```

## sd-compare-logreg.txt

```
Skills compared: 1384 of SkillScreen's 1384. Ours cut at 0.8524045530096918, theirs at 0.5.

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
Paired AUROC, ours - runs/exp005/sd-generic.csv: 0.139 [0.105, 0.172] on 1384 skills
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
Paired AUROC, ours - runs/exp005/sd-ast10.csv: 0.015 [-0.009, 0.038] on 1384 skills
Paired AUROC, ours - runs/exp005/sd-generic.csv: 0.154 [0.117, 0.189] on 1384 skills
Paired AUROC, ours - typesafe: 0.020 [-0.016, 0.054] on 1384 skills
Paired AUROC, ours - judge-gpt-5.5: -0.243 [-0.271, -0.215] on 1384 skills
Paired AUROC, ours - direct-s42: -0.232 [-0.266, -0.197] on 1384 skills
```

## sd-reproduce.txt

```
ast10-split: 1384 skills in common; Spearman 1.0000; largest score difference 0.0000; AUROC 0.6719 vs 0.6719
generic-1q: 1384 skills in common; Spearman 1.0000; largest score difference 0.0000; AUROC 0.5182 vs 0.5182
```

## msd-heldout-ast10.txt

```
train skills: 300, validation skills: 400, test skills: 1947 (1500 malicious, 447 benign)

| combiner | threshold (from validation) | test AUC [95% CI] | test TPR [95% CI] | test FPR [95% CI] | unscored |
|---|---|---|---|---|---|
| max | 0.192 | 0.806 [0.785, 0.825] | 0.614 [0.589, 0.638] | 0.114 [0.085, 0.143] | 1 |
| AST04 | 0.091 | 0.739 [0.716, 0.760] | 0.522 [0.498, 0.548] | 0.123 [0.095, 0.156] | 1 |
| logreg | 0.769 | 0.814 [0.794, 0.833] | 0.586 [0.561, 0.610] | 0.063 [0.042, 0.085] | 1 |
| baseline | 0.068 | 0.703 [0.678, 0.725] | 0.382 [0.357, 0.406] | 0.040 [0.023, 0.060] | 2 |

| paired difference on test | AUC diff [95% CI] |
|---|---|
| logreg - max | +0.008 [-0.002, +0.017] |
| AST04 - max | -0.067 [-0.095, -0.039] |
| logreg - AST04 | +0.075 [+0.051, +0.099] |

| logreg weight | intercept | AST01 | AST02 | AST03 | AST04 | AST05 |
|---|---|---|---|---|---|---|
| value | -0.27 | +2.25 | +2.34 | +3.38 | +4.07 | +1.88 |

| combiner | threshold rule (on validation) | threshold | test TPR [95% CI] | test FPR [95% CI] |
|---|---|---|---|---|
| max | tpr95 | 0.100 | 0.939 [0.927, 0.951] | 0.803 [0.765, 0.839] |
| max | fpr05 | 0.224 | 0.540 [0.515, 0.566] | 0.043 [0.024, 0.061] |
| AST04 | tpr95 | 0.047 | 0.957 [0.946, 0.967] | 0.937 [0.915, 0.958] |
| AST04 | fpr05 | 0.133 | 0.376 [0.351, 0.400] | 0.027 [0.013, 0.043] |
| logreg | tpr95 | 0.667 | 0.931 [0.918, 0.944] | 0.765 [0.726, 0.803] |
| logreg | fpr05 | 0.786 | 0.545 [0.520, 0.570] | 0.034 [0.018, 0.050] |
| baseline | tpr95 | 0.020 | 0.930 [0.917, 0.942] | 0.924 [0.899, 0.947] |
| baseline | fpr05 | 0.071 | 0.371 [0.346, 0.395] | 0.038 [0.021, 0.058] |

Baseline generic-1q: test AUC 0.703 [0.678, 0.725]

| paired difference on test | AUC diff [95% CI] |
|---|---|
| logreg - generic-1q | +0.111 [+0.087, +0.135] |
| AST04 - generic-1q | +0.036 [+0.008, +0.067] |
| max - generic-1q | +0.103 [+0.078, +0.128] |
```

## msd-heldout.txt

```
train skills: 300, validation skills: 400, test skills: 1947 (1500 malicious, 447 benign)

| combiner | threshold (from validation) | test AUC [95% CI] | test TPR [95% CI] | test FPR [95% CI] | unscored |
|---|---|---|---|---|---|
| max | 0.214 | 0.824 [0.804, 0.842] | 0.619 [0.595, 0.643] | 0.116 [0.086, 0.145] | 1 |
| AST04 | 0.091 | 0.826 [0.808, 0.844] | 0.680 [0.656, 0.704] | 0.141 [0.110, 0.174] | 2 |
| logreg | 0.755 | 0.831 [0.813, 0.848] | 0.638 [0.613, 0.662] | 0.107 [0.079, 0.137] | 3 |
| baseline | 0.068 | 0.703 [0.678, 0.727] | 0.382 [0.358, 0.408] | 0.040 [0.023, 0.061] | 2 |

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
| max | tpr95 | 0.099 | 0.904 [0.889, 0.918] | 0.588 [0.542, 0.633] |
| max | fpr05 | 0.265 | 0.552 [0.528, 0.578] | 0.063 [0.041, 0.085] |
| AST04 | tpr95 | 0.056 | 0.930 [0.917, 0.943] | 0.758 [0.718, 0.796] |
| AST04 | fpr05 | 0.154 | 0.481 [0.456, 0.507] | 0.025 [0.011, 0.039] |
| logreg | tpr95 | 0.637 | 0.923 [0.909, 0.935] | 0.691 [0.649, 0.733] |
| logreg | fpr05 | 0.775 | 0.600 [0.575, 0.625] | 0.067 [0.044, 0.092] |
| baseline | tpr95 | 0.020 | 0.930 [0.917, 0.943] | 0.924 [0.898, 0.948] |
| baseline | fpr05 | 0.071 | 0.372 [0.347, 0.396] | 0.038 [0.021, 0.058] |

Baseline generic-1q: test AUC 0.703 [0.678, 0.727]

| paired difference on test | AUC diff [95% CI] |
|---|---|
| logreg - generic-1q | +0.128 [+0.104, +0.153] |
| AST04 - generic-1q | +0.123 [+0.098, +0.148] |
| max - generic-1q | +0.121 [+0.094, +0.147] |
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
| MalSkillBench | malicious | 967 | 647 | 938 |
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
Paired AUROC, ours - runs/exp005/msd-generic.csv: 0.124 [0.099, 0.148] on 1944 skills
Paired AUROC, ours - typesafe: -0.015 [-0.034, 0.005] on 1945 skills
Paired AUROC, ours - judge-gpt-5.5: -0.124 [-0.142, -0.106] on 1945 skills
Paired AUROC, ours - direct: -0.166 [-0.184, -0.148] on 1945 skills
```

## msd-compare-ast10.txt

```
Skills compared: 1947 of SkillScreen's 1947. Ours cut at 0.2235, theirs at 0.5.

| method | skills | AUROC | FPR@99 | recall | FPR |
|---|---|---|---|---|---|
| ours | 1947 | 0.806 | 0.937 | 0.541 | 0.043 |
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
| ATR Skill Security Benchmark | benign | 83 | 9 | 4 |
| Agent Skill Malware | malicious | 7 | 1 | 6 |
| AgentTrap | malicious | 22 | 2 | 11 |
| AgentTrap | benign | 11 | 1 | 1 |
| MalSkillBench | malicious | 967 | 665 | 938 |
| MaliciousAgentSkillsBench | malicious | 61 | 39 | 42 |
| SkillFortifyBench | malicious | 2 | 2 | 2 |
| SkillFortifyBench | benign | 13 | 0 | 0 |
| SkillHarm | malicious | 92 | 56 | 92 |
| SkillLeakBench | malicious | 9 | 4 | 1 |
| SkillSafetyBench | malicious | 11 | 0 | 10 |
| SkillTrojan | benign | 2 | 0 | 0 |
| SkillTrustBench | malicious | 324 | 38 | 322 |
| SkillTrustBench | benign | 338 | 9 | 3 |

Cascade (direct flags, then ours must also flag): recall 0.530, FPR 0.004
Paired AUROC, ours - runs/exp005/msd-generic.csv: 0.103 [0.077, 0.127] on 1945 skills
Paired AUROC, ours - typesafe: -0.035 [-0.057, -0.014] on 1946 skills
Paired AUROC, ours - judge-gpt-5.5: -0.145 [-0.164, -0.126] on 1946 skills
Paired AUROC, ours - direct: -0.187 [-0.206, -0.168] on 1946 skills
```

## msd-compare-logreg.txt

```
Skills compared: 1947 of SkillScreen's 1947. Ours cut at 0.7753830101820911, theirs at 0.5.

| method | skills | AUROC | FPR@99 | recall | FPR |
|---|---|---|---|---|---|
| ours | 1947 | 0.831 | 0.944 | 0.601 | 0.067 |
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
| MalSkillBench | malicious | 967 | 790 | 938 |
| MaliciousAgentSkillsBench | malicious | 61 | 32 | 42 |
| SkillFortifyBench | malicious | 2 | 2 | 2 |
| SkillFortifyBench | benign | 13 | 0 | 0 |
| SkillHarm | malicious | 92 | 6 | 92 |
| SkillLeakBench | malicious | 9 | 3 | 1 |
| SkillSafetyBench | malicious | 11 | 1 | 10 |
| SkillTrojan | benign | 2 | 0 | 0 |
| SkillTrustBench | malicious | 324 | 59 | 322 |
| SkillTrustBench | benign | 338 | 27 | 3 |

Cascade (direct flags, then ours must also flag): recall 0.588, FPR 0.000
Paired AUROC, ours - runs/exp005/msd-generic.csv: 0.128 [0.106, 0.154] on 1943 skills
Paired AUROC, ours - typesafe: -0.010 [-0.029, 0.008] on 1944 skills
Paired AUROC, ours - judge-gpt-5.5: -0.119 [-0.137, -0.103] on 1944 skills
Paired AUROC, ours - direct: -0.161 [-0.178, -0.143] on 1944 skills
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
Paired AUROC, ours - runs/exp005/msd-ast10.csv: 0.018 [0.004, 0.032] on 1946 skills
Paired AUROC, ours - runs/exp005/msd-generic.csv: 0.121 [0.096, 0.145] on 1945 skills
Paired AUROC, ours - typesafe: -0.017 [-0.038, 0.003] on 1946 skills
Paired AUROC, ours - judge-gpt-5.5: -0.126 [-0.144, -0.109] on 1946 skills
Paired AUROC, ours - direct: -0.168 [-0.188, -0.150] on 1946 skills
```

## msd-reproduce.txt

```
ast10-split: 1946 skills in common; Spearman 1.0000; largest score difference 0.0000; AUROC 0.8239 vs 0.8239
generic-1q: 1945 skills in common; Spearman 1.0000; largest score difference 0.0000; AUROC 0.7026 vs 0.7026
```

## Progress log

```
[2026-10-19 10:43:06] start
[2026-10-19 10:43:07] backend: OpenRouter cloudflare/clef-flash on provider cloudflare, served as cloudflare/clef-flash|Cloudflare|unpinned, state sent as a string
[2026-10-19 10:43:07] note: OpenRouter returned no dated version for cloudflare/clef-flash; a silent model change would not be detected
[2026-10-19 10:43:12] context check: source_disjoint: longest test skill sent as 44684 characters (cut at 60,000: False); model read 11169 input tokens m_structural_disjoint: longest test skill (60000 characters) was refused: OpenRouter HTTP 422: {"error":{"message":"HTTP 422: {\"errors\":[{\"message\":\"AiError: AiError: Request requires 31548 tokens; the maximum is 24576 (6aff1130-a84f-40a3-bef6-c8c825d0ad49)\",\"code\":3030}],\"success\":false,\"result\":{},\"messages\":[]}","code":422}} <- WARNING: long skills will be unscored 
[2026-10-19 10:43:13] sd-train: running (spent so far $0)
runs/exp005/sd-train
[2026-10-19 10:47:08] sd-train: done (     900 predictions, spent so far $0.1525)
[2026-10-19 10:47:08] sd-validation: running (spent so far $0.1525)
runs/exp005/sd-validation
[2026-10-19 10:52:48] sd-validation: done (    1200 predictions, spent so far $0.364)
[2026-10-19 10:52:48] sd-test: running (spent so far $0.364)
runs/exp005/sd-test
[2026-10-19 11:10:42] sd-test: done (    4152 predictions, spent so far $1.0283)
[2026-10-19 11:13:28] sd: analysis written
[2026-10-19 11:13:28] msd-train: running (spent so far $1.0283)
runs/exp005/msd-train
[2026-10-19 11:17:29] msd-train: done (     900 predictions, spent so far $1.1985)
[2026-10-19 11:17:29] msd-validation: running (spent so far $1.1985)
runs/exp005/msd-validation
[2026-10-19 11:22:47] msd-validation: done (    1200 predictions, spent so far $1.3922)
[2026-10-19 11:22:47] msd-test: running (spent so far $1.3922)
runs/exp005/msd-test
[2026-10-19 11:47:36] msd-test: done (    5841 predictions, spent so far $2.367)
[2026-10-19 11:51:28] msd: analysis written
```
