# Overnight brief: run experiment 004 (hosted clef-flash)

For the local session, any model. Everything that needs judgment is already in the code. Your job is to start one script, keep it running, and report. Do not change code, prompts, thresholds or this repo's files.

The model is `cloudflare/clef-flash` through OpenRouter (pre-registration amendment 1). No local Ollama model is used.

## Goal

`runs/exp004/summary.md` exists and its progress log ends with `finished`, or the run stopped for a reason in the table below and you reported it.

## Steps

1. Pull: `git checkout main && git pull`. Confirm these files exist:
   - `docs/experiments/004-skillscreen-cohorts.md`, containing "Amendment 1";
   - `scripts/exp004_overnight.sh`;
   - `scripts/exp004_probe_backend.py`.
2. The API key: the person sets `OPENROUTER_API_KEY` in the terminal where the script will start, for example `export OPENROUTER_API_KEY=...` from their password manager.
   - **Never** write the key into a file, a commit, a log or this chat, and never print or echo it.
   - To check it is set without revealing it, run `[ -n "$OPENROUTER_API_KEY" ] && echo set`.
3. Start the run in that same terminal, in the background so it outlives this session:
   - macOS: `caffeinate -is nohup bash scripts/exp004_overnight.sh > /dev/null 2>&1 &`
   - Linux: `nohup bash scripts/exp004_overnight.sh > /dev/null 2>&1 &`
4. Check `tail -n 5 runs/exp004/progress.log` about every 30 minutes.
   - A few lines starting `systemone call failed` are retried automatically; ignore them.
   - Each `done` line shows the spend so far.
   - Do nothing else while it runs.
5. When the log says `finished` or `STOPPED`, report as described below.

## If it stops

| `progress.log` says | Do |
|---|---|
| `STOPPED: ... is not committed` | Pull again (step 1). If the file is still missing, stop and report. |
| `STOPPED: OPENROUTER_API_KEY is not set` | Ask the person to export it in the terminal (step 2), then re-run step 3 in that terminal. |
| `STOPPED: OpenRouter refused the probe call` | Report the last 10 lines of `runs/exp004/backend-probe.err`. They may mention a 401 (key), 402 (credits) or 404 (model ID). Do not retry with another model. |
| `STOPPED: OpenRouter now serves ... but the first run used ...` | Stop and report both versions. Do not delete `backend.txt`. |
| `STOPPED: ... reached its $5 cap` or `spent $... of the $15 budget` | Stop and report. Only the person may raise `STEP_CAP` or `TOTAL_CAP`. |
| `STOPPED: <step> failed 5 times` | Run `tail -n 40 runs/exp004/progress.log`. If the network dropped or the machine slept, re-run step 3. Otherwise stop and report those 40 lines. |
| `context check: ... WARNING ...` | Not a stop. Note it in the report. |
| The script is gone but the log ends mid-step | Re-run step 3. It resumes where it stopped. |

Re-running step 3 is always safe: finished steps are skipped and partial runs resume.

## Report

Reply with:
1. The last 10 lines of `runs/exp004/progress.log`.
2. The full text of `runs/exp004/summary.md`, or attach the file.
3. The contents of `runs/exp004/backend.txt`.

Do not interpret the numbers, edit `docs/experiments/004-skillscreen-cohorts.md`, commit or push. The cloud session writes up the results.

## Timing and cost

The order is the probe, then source-disjoint train, validation and test, then the same three for structurally disjoint. With 8 workers this should take one to three hours in total, depending on OpenRouter's speed and rate limits.

It should cost about $2 to $5. The script stops at $5 per step or $15 in total. `summary.md` is rewritten after the probe and after each protocol.
