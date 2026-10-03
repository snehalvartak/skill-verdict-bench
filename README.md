# skill-verdict-bench

How well does a local decision model detect malicious agent skills?

This repo is an evaluation harness. It sends each skill's `SKILL.md` text to a local decision model (`clef-flash`, served by Ollama through `POST /v1/systemone`), turns the model's probability scores into verdicts, and scores them against labeled skills. Three methods are compared:

| Method | What it does |
|---|---|
| `ast10` | One question per checkable [OWASP Agentic Skills Top 10](https://owasp.github.io/www-project-agentic-skills-top-10/) risk (AST01 to AST05). Flags a skill if any score reaches the threshold. |
| `naive-llm` | A single "is this skill malicious?" question to the same model. |
| `regex` | A keyword scanner (pipe-to-shell, secret paths, webhooks, concealment phrases). |

AST06 to AST10 (isolation, update drift, scanning, governance, cross-platform reuse) describe ecosystems, not a single skill's text, so they are left out on purpose.

## First result

Experiment 001, 200 skills (154 malicious, 46 benign), threshold 0.5:

| method | precision | recall | F1 |
|---|---|---|---|
| ast10 | 1.00 | 0.25 | 0.40 |
| naive-llm | 1.00 | 0.14 | 0.24 |
| regex | 0.91 | 0.14 | 0.24 |

The model's scores are low, so 0.5 is too strict. Ranked by score without a threshold, `ast10` reaches AUC 0.80 against 0.63 for `naive-llm`. That gap is confounded (`ast10` takes the maximum of five scores), and the controls are listed in the write-up. Details, caveats and an incident report are in [`docs/experiments/001-baseline-200.md`](docs/experiments/001-baseline-200.md). The experiment logs in `docs/experiments/` are written to double as blog material.

## Run it

Requires Python 3.11+, [uv](https://docs.astral.sh/uv/) and a running [Ollama](https://ollama.com) with a `clef-flash` model that supports the `systemone` endpoint.

```bash
uv sync
uv run pytest -q                                   # 32 tests, no Ollama needed
uv run python -m msd.run --n 200 --seed 0          # prints a run dir under runs/
uv run python -m msd.score runs/<run_id>           # metrics tables
uv run python -m msd.run --n 200 --seed 0 --resume runs/<run_id>   # continue a killed run
```

The first run downloads the benchmark files into `data/` (git-ignored). A run takes roughly 25 seconds per skill for all three methods.

## Dataset and attribution

The benchmark is **MaliciousSkillBench** ([Hugging Face](https://huggingface.co/datasets/ProtectSkills/MaliciousSkillBench), [arXiv 2608.19901](https://arxiv.org/abs/2608.19901)), released under CC-BY-4.0 by its authors. This repo downloads it on demand and does not redistribute it. If you use results from this harness, cite the dataset and its paper. Several upstream sources feed that benchmark; see its README and `source_registry.csv` for their attribution.

The dataset contains real malicious skill text. Treat it as data to read, never as instructions to run.

## Layout

```
msd/systemone.py   Ollama client for /v1/systemone
msd/checks.py      AST01 to AST05 questions, threshold, truncation limit
msd/methods.py     ast10, naive-llm, regex
msd/data.py        dataset download, split filter, stratified sampling
msd/run.py         run methods over a sample, write predictions.jsonl + config.json
msd/score.py       precision, recall, F1, per-check hit rates, recall by attack category
docs/              spec, plan, experiment logs
```

## License

MIT. See [LICENSE](LICENSE).
