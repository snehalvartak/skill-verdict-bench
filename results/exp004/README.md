# Experiment 004 results

Raw output of `scripts/exp004_overnight.sh`, copied from `runs/exp004/` (which git ignores). Run on 2026-10-19 from commit `fe4f43e`: hosted `cloudflare/clef-flash` through OpenRouter, served by Cloudflare only (pre-registration amendments 1 and 2). Total cost $2.01.

Rows hold benchmark ids, labels, scores and per-call cost only, never skill text. Join on `benchmark_id` with MaliciousSkillBench (revision pinned in `svb/data.py`) for the text.

| Path | What it is |
|---|---|
| `summary.md` | everything below in one file, plus the progress log |
| `backend.txt`, `context-check.txt` | served model and provider; what the model read for the longest test skill |
| `probe/`, `probe-*.txt` | 004a SkillHarm probe (exploratory) |
| `sd-{train,validation,test}/`, `msd-…/` | one run each: `config.json` (sample, prompts, model) and `predictions.jsonl` (one row per skill and method) |
| `sd-heldout.{txt,json}`, `msd-…` | held-out tables: logreg weights, validation thresholds, test AUC/TPR/FPR with 95% intervals |
| `sd-compare-*.txt`, `msd-…` | SkillScreen comparisons for each combiner at the `fpr05` threshold |
| `sd-generic.csv`, `msd-generic.csv` | `generic-1q` scores in SkillScreen's CSV format |
| `data-verify-*.txt` | dataset hashes before and after the run |
| `progress.log` | the runner's log; the 6 failed calls are the one MSD test skill over the 24,576-token limit |
