# Overnight brief: run experiment 004

For the local session, any model. Everything that needs judgment is already in the code. Your job is to start one script, keep it running, and report. Do not change code, prompts, thresholds or this repo's files.

## Goal

`runs/exp004/summary.md` exists and its progress log ends with `finished`, or the run stopped for a reason in the table below and you reported it.

## Steps

1. Pull: `git checkout main && git pull`. Confirm `docs/experiments/004-skillscreen-cohorts.md` and `scripts/exp004_overnight.sh` exist.
2. Check the model without changing it: `ollama list` must show `clef-flash:latest` with ID starting `0a2a05d6a581`. **Never run `ollama pull`**; it changes the model and invalidates the experiment.
3. Start the run in the background so it outlives this session:
   - macOS: `caffeinate -is nohup bash scripts/exp004_overnight.sh > /dev/null 2>&1 &`
   - Linux: `nohup bash scripts/exp004_overnight.sh > /dev/null 2>&1 &`
4. Check `tail -n 5 runs/exp004/progress.log` about once an hour. Lines starting `systemone call failed` are retried automatically; ignore a few. Do nothing else while it runs.
5. When the log says `finished` or `STOPPED`, report as described below.

## If it stops

| `progress.log` says | Do |
|---|---|
| `STOPPED: ... is not committed` | Pull again (step 1). If the file is still missing, stop and report. |
| `STOPPED: Ollama is not answering` | Start Ollama (`ollama serve`, or open the Ollama app), wait one minute, re-run step 3. |
| `STOPPED: clef-flash digest is ...` | Stop and report the digest. Do not pull or re-pull any model. |
| `STOPPED: <step> failed 5 times` | Run `tail -n 40 runs/exp004/progress.log`. If Ollama was down or the machine slept, fix that and re-run step 3. Otherwise stop and report those 40 lines. |
| `context check: ... WARNING ...` | Not a stop. Note it in the report. |
| The script is gone but the log ends mid-step | Re-run step 3. It resumes where it stopped. |

Re-running step 3 is always safe: finished steps are skipped, and partial runs resume.

## Report (morning)

Reply with:
1. The last 10 lines of `runs/exp004/progress.log`.
2. The full text of `runs/exp004/summary.md`, or attach the file.

Do not interpret the numbers, edit `docs/experiments/004-skillscreen-cohorts.md`, commit, or push. The cloud session writes up the results.

## Timing

About 19 hours at 12 to 14 seconds per skill, in this order: probe (about 40 minutes), then source-disjoint train, validation and test (about 8 hours), then the same three for structurally disjoint (about 10 hours). `summary.md` is rewritten after the probe and after each protocol, so a morning report is useful even if the structurally disjoint runs are still going. Leave them running.
