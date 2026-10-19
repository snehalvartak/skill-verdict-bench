# Hosted decision models through OpenRouter

Date: 2026-10-19. Status: backend built (`svb.run --backend openrouter`). Experiment 004 is the first hosted run, on `cloudflare/clef-flash` (`scripts/exp004_overnight.sh`).

## Why

Experiments 001 to 004 use one local model, `clef-flash` on Ollama. Several other decision models now share the same request shape through OpenRouter. Running the same pre-registered design on them asks whether targeted per-risk questions beat one generic question across decision models, not just for one. A hosted run also takes minutes rather than hours.

## Backend

- **Endpoint:** `POST https://openrouter.ai/api/alpha/decisions`, with the same `{model, state, questions}` body as the local `/v1/systemone` ([OpenRouter Jev tutorial](https://openrouter.ai/docs/guides/community/jev-tutorial.md)). The endpoint is **alpha**: if its response shape changes, calls come back unparseable and the run stops after 10 failures in a row.
- **Key:** read from the `OPENROUTER_API_KEY` environment variable. It is never written to a run, a log or an error message.
- **Version recorded:** the config's `model_digest` is the dated slug and provider OpenRouter actually serves (for example `typesafe/jev-1.13-20260917|TypeSafe`). It comes from one tiny call at start, so `--resume` and `svb.heldout` refuse to mix versions. A model that returns no dated slug is marked `|unpinned`.
- **Per-row usage:** every hosted prediction row records `usage`: calls, input tokens, the cost OpenRouter reports, and the served model. Spend is therefore measured, not estimated.
- **Spending cap:** `--max-cost` stops a run once logged spend reaches it, counting earlier sessions of a resumed run. `--workers` scores several skills at once.
- **State format:** `--state-format object` sends `{"skill_md": text}` in place of the plain string, in case a model refuses a string `state`. Our local runs send a string. Check on the first hosted call which form each model accepts, and record it, because it changes the input.
- **Local runs are unaffected:** a local run writes the same config keys and rows as before (checked against a run made by the previous code), so experiment 004 can still resume.
- **Not comparable with local runs:** a hosted model is a different model from the local Q8 `clef-flash`, even under the same name. Hosted runs are their own rows and are never pooled with 001 to 004.

## Models and estimated cost

Prices were checked on 2026-10-18 from secondary sources, because the OpenRouter model pages did not load; confirm them before spending. Output tokens are free on all of these. The token estimate is SkillScreen's per-skill token counts (mean about 1,800 tokens after the 60,000-character cap) plus about 90 tokens of framing per call. Real tokenizers and per-call framing may move it by about 20%.

| Model | `--model` | Input $/1M | Probe, 190 skills (2.2M tokens) | 004 design, batched `ast10` + `generic-1q` (20.5M) | 004 design, `ast10-split` + `generic-1q` (56.2M) |
|---|---|---|---|---|---|
| Cloudflare Clef Flash 9B | `cloudflare/clef-flash` | 0.038 (0.021 to 0.09 also reported) | $0.08 | $0.78 | $2.14 |
| Cloudflare Clef 27B | `cloudflare/clef` | 0.24 | $0.53 | $4.92 | $13.49 |
| Cloudflare Clef Omni | `cloudflare/clef-omni` | 0.15 | $0.33 | $3.07 | $8.43 |
| TypeSafe Jev 1.14 | `typesafe/jev-1.14` | 0.042 | $0.09 | $0.86 | $2.36 |
| Microsoft-Decision-1 | `microsoft/microsoft-decision-1` | 0.042 (third-party figure) | $0.09 | $0.86 | $2.36 |
| Liquid d1-ultra | `liquid/d1-ultra` | 0.042 | $0.09 | $0.86 | $2.36 |
| Perplexity pplx-decider v1.2 | `perplexity/pplx-decider-v1.2` | 0.02 | $0.04 | $0.41 | $1.12 |
| Perplexity pplx-decider-flash v1.2 | `perplexity/pplx-decider-flash-v1.2` | 0.01 | $0.02 | $0.21 | $0.56 |
| Respan span-02 | `respan/span-02` | 0.01 | $0.02 | $0.21 | $0.56 |
| **All nine** | | | **about $1.30** | **about $12** | **about $33** |

Celeris-1 Decision ($0.04/M) is not on OpenRouter. It would need its own backend, and is left out for now.

Unknowns that could change the bill:
- **Cached-input discounts:** `ast10-split` sends the same skill five times, so a discount would bring the full design close to the batched cost.
- **Per-request fees:** none are published, but the full design makes about 30,000 calls per model, so even a small fee would add up.

## Order of work

1. **Probe sweep (exploratory, about $1.30).** Run each model on the 190-skill SkillHarm probe and read AUROC only. These probe skills are part of the source-disjoint test set, so the write-up says that test data was looked at.
   ```bash
   export OPENROUTER_API_KEY=...        # never commit it
   uv run python -m svb.skillscreen probe --skillscreen ../SkillScreen --out probe-ids.txt
   for m in cloudflare/clef-flash cloudflare/clef typesafe/jev-1.14 microsoft/microsoft-decision-1 \
            liquid/d1-ultra perplexity/pplx-decider-v1.2 perplexity/pplx-decider-flash-v1.2 respan/span-02 cloudflare/clef-omni; do
     uv run python -m svb.run --backend openrouter --model "$m" --split source_disjoint --part test \
       --ids probe-ids.txt --n 5000 --methods ast10 generic-1q --workers 8 --max-cost 1 \
       --out "runs/hosted/probe-${m//\//_}"
   done
   ```
   Then for each run:
   ```bash
   uv run python -m svb.skillscreen compare runs/hosted/probe-<model> --method ast10 --combine AST04 \
     --skillscreen ../SkillScreen --protocol sd --threshold 0.1
   ```
   Read the AUROC column only, and use `--method generic-1q` for the baseline.
2. **Experiment 005, pre-registered first.** Run the 004 design (train 300, validation 400, full test) with batched `ast10`, `AST04` and `generic-1q` on the models the probe shows are worth it. Batched is the cheap default, because experiment 002 found batching does not change AUC. That is about $1 to $5 per model.
3. **`ast10-split` only where per-check scores are the point,** on one or two models.

## Sources

- [OpenRouter Jev tutorial](https://openrouter.ai/docs/guides/community/jev-tutorial.md)
- [OpenRouter SDK: decisions usage](https://openrouter.ai/docs/client-sdks/python/components/decisionsresponseusage.md)
- [OpenRouter decision-model listing](https://openrouter.ai/models?q=decision)
- [Cloudflare Workers AI pricing](https://developers.cloudflare.com/workers-ai/platform/pricing/)
- [TechEnclave](https://techenclave.com/news/items/cloudflare-adds-clef-omni-and-cuts-clef-flash-pricing-with-a-shorter-hosted-context)
- [DevelopersDigest](https://www.developersdigest.tech/blog/cloudflare-clef-decision-models-2026)
- [TypeSafe docs](https://docs.typesafe.ai/models)
- [llmreference](https://www.llmreference.com/model/microsoft-decision-1/openrouter)
- [eesel](https://www.eesel.ai/blog/microsoft-decision-1-pricing)
- [Infrabase](https://infrabase.ai/models/celeris-1-decision)
