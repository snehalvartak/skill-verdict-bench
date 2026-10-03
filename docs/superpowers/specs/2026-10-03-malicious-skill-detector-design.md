# Malicious Skill Detector — Design

Date: 2026-10-03

## Intent

An evaluation harness that measures how well a local model (`clef-flash:latest` via Ollama: 9.1B qwen35, Q8, 256k ctx, capability `decision`) classifies agent skills as malicious or benign. OWASP Agentic Skills Top 10 (AST10) risks become per-risk prompts ("checks"). A public labeled dataset is the benchmark. Experiments are documented continuously so they can become blog posts.

Local, offline research CLI. Output is metrics only; no gating or blocking.

**Success:** a reproducible run that prints precision/recall/F1 for three methods on a 200-skill stratified sample, per-check hit rates, and a written experiment log; scalable to larger samples/splits by changing flags.

## Benchmark

[ProtectSkills/MaliciousSkillBench](https://huggingface.co/datasets/ProtectSkills/MaliciousSkillBench) (CC-BY-4.0, arXiv 2608.19901).

- 9,740 skills: 7,505 malicious, 2,235 benign (~77% malicious → report P/R/F1, not accuracy).
- `primary.parquet`: `benchmark_id`, `label` (1 malicious, 0 benign), `skill_text`, `attack_categories` (11 harmonized; covers 4,983 malicious).
- Frozen splits in `splits/` (`random`, `source_balanced_random`, `m_structural_disjoint`, `source_disjoint`); join on `benchmark_id`.
- 5 malicious rows have sanitized text only (`text_available=false`): dropped from scoring.
- HF copy has `SKILL.md` text only (no `scripts/`); v1 judges text only.

## AST10 coverage

Checkable from a single skill's text: **AST01** Malicious Skills, **AST02** Supply Chain (partial: fetch-and-run installs, typosquat-like names), **AST03** Over-Privileged, **AST04** Insecure Metadata, **AST05** Untrusted External Instructions.

Not checkable from one skill's text, excluded by design: AST06 Weak Isolation, AST07 Update Drift, AST08 Poor Scanning, AST09 No Governance, AST10 Cross-Platform Reuse. This is itself a reported finding.

## Components

```
data.py      fetch primary.parquet + splits/random; stratified sample
checks.py    AST01/02/03/04/05 rubric prompts
methods.py   ast10, naive-llm, regex — one signature: skill_text -> {flag, evidence}
run.py       method × sample -> runs/<run_id>/predictions.jsonl + config.json
score.py     predictions + labels -> metrics
docs/experiments/NNN-<slug>.md   one write-up per run
tests/       regex baseline, scorer, sampler stratification
```

Stack: Python, stdlib + `pandas`/`pyarrow`; Ollama HTTP API via `urllib`. No frameworks.

## Methods

- **ast10:** 5 independent prompts, one per check; each returns JSON `{flag, evidence}`. Skill flagged if any check fires.
- **naive-llm:** one prompt "is this skill malicious?" to the same model.
- **regex:** keyword scanner (`curl|bash`, base64 blobs, `~/.ssh`, `.env`, webhook URLs, "do not tell the user", …).

## Sampling

200 skills from the `random` test split, stratified by label at the natural ratio, fixed seed, sanitized rows dropped. Scale-up = change `--n` / `--split`; second run on `source_disjoint`.

## Run record

`config.json` stores: model digest, SHA of each prompt, seed, split, n, truncation limit, sample IDs. Reproducible from config.

## Scoring

Per method: precision, recall, F1, confusion matrix. Additionally:
- per-check hit rate on malicious vs benign
- recall by attack category
- any-of-N rule vs each check alone
- unparseable model outputs counted and reported (never silently dropped)

## Known risks

- clef-flash's `decision` capability may need a specific response format; first task is a smoke test through `/api/chat` before writing prompts.
- Very long skills truncated at a logged limit.
- Text-only evaluation underestimates script-borne attacks.
- Dataset label noise / template-generated malicious skills may inflate scores; report per-source where possible.

## Experiment documentation

Every run gets `docs/experiments/NNN-<slug>.md`: hypothesis, prompt versions, sample/seed, metrics table, observations, surprises. Raw outputs kept as JSONL so posts can be regenerated from logs.

## Out of scope (v1)

AST06–09 checks, script/package analysis, runtime sandboxing, fine-tuning, any UI or service.
