# Experiment 005 results

Raw output of `scripts/exp005_overnight.sh`, copied from `runs/exp005/` (which git ignores). Run on 2026-10-19: hosted `cloudflare/clef-flash` through OpenRouter, provider `cloudflare`. Cost $2.37. Write-up: [`docs/experiments/005-full-method-set.md`](../../docs/experiments/005-full-method-set.md).

Rows hold benchmark ids, labels, scores and per-call cost only, never skill text. Join on `benchmark_id` with MaliciousSkillBench (revision pinned in `svb/data.py`) for the text.

| Path | What it is |
|---|---|
| `summary.md` | everything below in one file, plus the progress log |
| `{sd,msd}-{train,validation,test}/` | one run each, methods `ast10-split`, `ast10`, `generic-1q`: `config.json` and `predictions.jsonl` |
| `{sd,msd}-heldout.{txt,json}` | held-out tables for `ast10-split`; `-heldout-ast10.*` for the batched `ast10` |
| `{sd,msd}-compare-{max,AST04,logreg,ast10}.txt` | SkillScreen comparisons and paired AUROCs |
| `{sd,msd}-reproduce.txt` | R1: 004 against 005 on the same skills |
| `*-generic.csv`, `*-ast10.csv` | scores in SkillScreen's CSV format |
| `backend.txt`, `context-check.txt`, `data-verify-*.txt`, `progress.log` | served model, context check, dataset hashes, runner log |
