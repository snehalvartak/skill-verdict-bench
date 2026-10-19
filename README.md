# skill-verdict-bench

How well does a local decision model detect malicious agent skills?

This repo is an evaluation harness. It sends each skill's `SKILL.md` text to a local decision model (`clef-flash`, served by Ollama through `POST /v1/systemone`), turns the model's probability scores into verdicts, and scores them against labeled skills. Three methods are compared:

| Method | What it does |
|---|---|
| `ast10` | One question per checkable [OWASP Agentic Skills Top 10](https://owasp.github.io/www-project-agentic-skills-top-10/) risk (AST01 to AST05). Flags a skill if any score reaches the threshold. |
| `generic-1q` | A single "is this skill malicious?" question to the same model. |
| `regex` | A keyword scanner (pipe-to-shell, secret paths, webhooks, concealment phrases). |

Two opt-in controls, `generic-5q` (five generic paraphrases) and `ast10-split` (one call per check), isolate what drives `ast10`'s result: `--methods generic-5q ast10-split`. Runs made before 2026-10-19 call these `naive-llm` and `naive-x5`; the scorers read them under the new names. Compare runs with `python -m svb.compare <run dirs>`.

AST06 to AST10 (isolation, update drift, scanning, governance, cross-platform reuse) describe ecosystems, not a single skill's text, so they are left out on purpose.

## First result

Experiment 001, 200 skills (154 malicious, 46 benign), threshold 0.5:

| method | precision | recall | F1 |
|---|---|---|---|
| ast10 | 1.00 | 0.25 | 0.40 |
| generic-1q | 1.00 | 0.14 | 0.24 |
| regex | 0.91 | 0.14 | 0.24 |

The model's scores are low, so 0.5 is too strict. Ranked by score without a threshold, `ast10` reaches AUC 0.80 against 0.63 for `generic-1q`. That gap is confounded (`ast10` takes the maximum of five scores), and the controls are listed in the write-up. Details, caveats and an incident report are in [`docs/experiments/001-baseline-200.md`](docs/experiments/001-baseline-200.md).

Experiment 002 ran the controls: with the max-of-five and batching held fixed, the AST10 questions still beat generic paraphrases by +0.12 AUC (95% CI +0.05 to +0.20). Batching does not change the aggregate ranking. See [`docs/experiments/002-controls.md`](docs/experiments/002-controls.md). The experiment logs in `docs/experiments/` are written to double as blog material.

## Run it

Requires Python 3.11+, [uv](https://docs.astral.sh/uv/) and a running [Ollama](https://ollama.com) with a `clef-flash` model that supports the `systemone` endpoint.

```bash
uv sync
uv run pytest -q                                   # 119 tests, no Ollama needed
uv run python -m svb.run --n 200 --seed 0          # prints a run dir under runs/
uv run python -m svb.score runs/<run_id>           # metrics, AUC and threshold-sweep tables
uv run python -m svb.heldout --train runs/<train> --val runs/<val> --test runs/<test>   # held-out evaluation
uv run python -m svb.run --n 200 --seed 0 --resume runs/<run_id>   # continue a killed run (refuses if sample, prompts or model changed)
```

The first run downloads the benchmark files into `data/` (git-ignored). A run takes roughly 25 seconds per skill for all three methods.

To score a run with SkillScreen's rules and set it beside SkillScreen's published methods, clone [SkillScreen](https://github.com/JerroldH/SkillScreen) next to this repo, then:

```bash
uv run python -m svb.data verify                   # cached files vs the pinned dataset revision
uv run python -m svb.skillscreen compare runs/<run_id> --method ast10 --skillscreen ../SkillScreen --protocol sd --threshold <t>
uv run python -m svb.skillscreen export runs/<run_id> --method ast10 --out ast10.csv   # SkillScreen's CSV format
# score by AST04 alone or a fitted logistic regression instead of the max, and test AUROC against another method:
uv run python -m svb.skillscreen compare runs/<run_id> --method ast10-split --combine logreg --weights=<from svb.heldout> --skillscreen ../SkillScreen --protocol sd --threshold <t> --paired typesafe
```

Hosted decision models run through OpenRouter with the same methods. The key is read from `OPENROUTER_API_KEY`; the served model version and per-call cost are recorded in each run. Hosted runs are separate from local ones and are never pooled with them. Models, estimated costs and the order of work are in `docs/superpowers/plans/2026-10-19-hosted-models.md`.

```bash
OPENROUTER_API_KEY=... uv run python -m svb.run --backend openrouter --model cloudflare/clef-flash \
  --methods ast10 generic-1q --workers 8 --max-cost 1 --n 200 --seed 0
```

Experiment 004 runs unattended on hosted `cloudflare/clef-flash` (pre-registration amendment 1): export `OPENROUTER_API_KEY`, then `bash scripts/exp004_overnight.sh` (start it with `nohup`; see `docs/superpowers/plans/2026-10-19-overnight-brief.md`). It resumes where it stopped and writes `runs/exp004/summary.md`.

Runs created before `--part` existed (including experiment 001) have no `part` in their `config.json`, so `--resume` refuses them. They can still be scored; to continue one, start a fresh run.

## Related work

[SkillScreen](https://arxiv.org/abs/2610.17727) (Huang et al., 2026) evaluates detectors on the same benchmark, on its structurally disjoint and source-disjoint splits: a fine-tuned 2B decision model (AUROC 0.992 and 0.916), ModernBERT, a word SVM, LLM judges and static scanners. Its TypeSafe Jev 1.13 baseline asks one fixed question through the same `/v1/systemone` interface, so it is the published counterpart of `generic-1q` here.

The numbers in experiments 001 and 002 come from 200 skills of the `random` split and are not comparable with SkillScreen's. What this repo adds is the per-risk decomposition: one question per OWASP AST risk, scored and compared separately. `svb.skillscreen` scores runs with SkillScreen's rules (tie-averaged AUROC, FPR at 99% recall, missing scores flagged) and compares them skill by skill with its released predictions, which are CC BY 4.0 © SkillScreen contributors and are read from a local clone, not copied here. If you use that comparison, cite SkillScreen too:

```bibtex
@article{huang2026skillscreen,
  title   = {SkillScreen: High-Recall Screening of Malicious Agent Skills with Decision Models},
  author  = {Huang, Jerrold and Quan, Junwei and Lyu, Saiyue and Guo, Zihan and Ge, Yingqiang},
  journal = {arXiv preprint arXiv:2610.17727},
  year    = {2026}
}
```

## Dataset and attribution

The benchmark is **MaliciousSkillBench** ([Hugging Face](https://huggingface.co/datasets/ProtectSkills/MaliciousSkillBench), [arXiv 2608.19901](https://arxiv.org/abs/2608.19901)), released under CC-BY-4.0 by its authors. This repo downloads it on demand, pinned to revision `d4b42ce` (the one SkillScreen uses) with sha256 checks on new downloads, and does not redistribute it. Files cached before the pin are not re-checked automatically; `python -m svb.data verify` reports whether they match. If you use results from this harness, cite the dataset and its paper. Several upstream sources feed that benchmark; see its README and `source_registry.csv` for their attribution.

The dataset contains real malicious skill text. Treat it as data to read, never as instructions to run.

## Layout

```
svb/systemone.py   decision-model client: local Ollama /v1/systemone or hosted OpenRouter /api/alpha/decisions
svb/checks.py      AST01 to AST05 questions, threshold, truncation limit
svb/methods.py     ast10, generic-1q, regex, and the controls generic-5q and ast10-split
svb/data.py        pinned dataset download and hash check, split filter, stratified sampling
svb/run.py         run methods over a sample, write predictions.jsonl + config.json
svb/score.py       precision, recall, F1, AUC, threshold sweep, bootstrap CIs, per-check hit rates and AUC, recall by attack category
svb/compare.py     cross-method comparison tables for a set of run dirs
svb/heldout.py     threshold and check combination chosen on validation, reported on test with CIs
svb/skillscreen.py SkillScreen's metric rules, CSV export, comparison with its released predictions, probe sample
docs/              spec, plan, experiment logs
```

## License

MIT. See [LICENSE](LICENSE).
