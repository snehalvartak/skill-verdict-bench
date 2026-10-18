# skill-verdict-bench

How well does a local decision model detect malicious agent skills?

This repo is an evaluation harness. It sends each skill's `SKILL.md` text to a local decision model (`clef-flash`, served by Ollama through `POST /v1/systemone`), turns the model's probability scores into verdicts, and scores them against labeled skills. Three methods are compared:

| Method | What it does |
|---|---|
| `ast10` | One question per checkable [OWASP Agentic Skills Top 10](https://owasp.github.io/www-project-agentic-skills-top-10/) risk (AST01 to AST05). Flags a skill if any score reaches the threshold. |
| `naive-llm` | A single "is this skill malicious?" question to the same model. |
| `regex` | A keyword scanner (pipe-to-shell, secret paths, webhooks, concealment phrases). |

Two opt-in controls, `naive-x5` (five generic paraphrases) and `ast10-split` (one call per check), isolate what drives `ast10`'s result: `--methods naive-x5 ast10-split`. Compare runs with `python -m svb.compare <run dirs>`.

AST06 to AST10 (isolation, update drift, scanning, governance, cross-platform reuse) describe ecosystems, not a single skill's text, so they are left out on purpose.

## First result

Experiment 001, 200 skills (154 malicious, 46 benign), threshold 0.5:

| method | precision | recall | F1 |
|---|---|---|---|
| ast10 | 1.00 | 0.25 | 0.40 |
| naive-llm | 1.00 | 0.14 | 0.24 |
| regex | 0.91 | 0.14 | 0.24 |

The model's scores are low, so 0.5 is too strict. Ranked by score without a threshold, `ast10` reaches AUC 0.80 against 0.63 for `naive-llm`. That gap is confounded (`ast10` takes the maximum of five scores), and the controls are listed in the write-up. Details, caveats and an incident report are in [`docs/experiments/001-baseline-200.md`](docs/experiments/001-baseline-200.md).

Experiment 002 ran the controls: with the max-of-five and batching held fixed, the AST10 questions still beat generic paraphrases by +0.12 AUC (95% CI +0.05 to +0.20). Batching does not change the aggregate ranking. See [`docs/experiments/002-controls.md`](docs/experiments/002-controls.md). The experiment logs in `docs/experiments/` are written to double as blog material.

## Run it

Requires Python 3.11+, [uv](https://docs.astral.sh/uv/) and a running [Ollama](https://ollama.com) with a `clef-flash` model that supports the `systemone` endpoint.

```bash
uv sync
uv run pytest -q                                   # 52 tests, no Ollama needed
uv run python -m svb.run --n 200 --seed 0          # prints a run dir under runs/
uv run python -m svb.score runs/<run_id>           # metrics, AUC and threshold-sweep tables
uv run python -m svb.run --n 200 --seed 0 --resume runs/<run_id>   # continue a killed run (refuses if sample, prompts or model changed)
```

The first run downloads the benchmark files into `data/` (git-ignored). A run takes roughly 25 seconds per skill for all three methods.

Runs created before `--part` existed (including experiment 001) have no `part` in their `config.json`, so `--resume` refuses them. They can still be scored; to continue one, start a fresh run.

## Dataset and attribution

The benchmark is **MaliciousSkillBench** ([Hugging Face](https://huggingface.co/datasets/ProtectSkills/MaliciousSkillBench), [arXiv 2608.19901](https://arxiv.org/abs/2608.19901)), released under CC-BY-4.0 by its authors. This repo downloads it on demand and does not redistribute it. If you use results from this harness, cite the dataset and its paper. Several upstream sources feed that benchmark; see its README and `source_registry.csv` for their attribution.

The dataset contains real malicious skill text. Treat it as data to read, never as instructions to run.

## Layout

```
svb/systemone.py   Ollama client for /v1/systemone
svb/checks.py      AST01 to AST05 questions, threshold, truncation limit
svb/methods.py     ast10, naive-llm, regex
svb/data.py        dataset download, split filter, stratified sampling
svb/run.py         run methods over a sample, write predictions.jsonl + config.json
svb/score.py       precision, recall, F1, AUC, threshold sweep, bootstrap CIs, per-check hit rates and AUC, recall by attack category
svb/compare.py     cross-method comparison tables for a set of run dirs
docs/              spec, plan, experiment logs
```

## License

MIT. See [LICENSE](LICENSE).
