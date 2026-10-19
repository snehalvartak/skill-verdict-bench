#!/usr/bin/env bash
# Experiment 004, unattended. Plan: docs/superpowers/plans/2026-10-19-exp004-skillscreen-cohorts.md
#
# Model: hosted cloudflare/clef-flash through OpenRouter (pre-registration amendment 1). The key must be in the
# environment of the shell that starts the script; it is never written to a file or a log.
#
# Start it from the repo root and leave it:
#   export OPENROUTER_API_KEY=...      (from your password manager; never paste it into a file)
#   macOS:  caffeinate -is nohup bash scripts/exp004_overnight.sh > /dev/null 2>&1 &
#   Linux:  nohup bash scripts/exp004_overnight.sh > /dev/null 2>&1 &
# Watch:    tail -f runs/exp004/progress.log
# Result:   runs/exp004/summary.md (written at the end; also after the probe and after each protocol)
#
# Safe to re-run at any time: every step resumes where it stopped and finished steps are skipped.
# It stops, and says why in progress.log, if the key, the served model version, the data, the budget or the
# pre-registration is not what 004 needs.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1

SS=${SKILLSCREEN:-../SkillScreen}
OUT=runs/exp004
MODEL=${MODEL:-cloudflare/clef-flash}
PROVIDER=${PROVIDER:-cloudflare}  # every call on this OpenRouter provider, no fallbacks (amendment 2)
WORKERS=${WORKERS:-8}         # skills scored at once
STEP_CAP=${STEP_CAP:-5}       # dollars per run step (expected well under $1 each)
TOTAL_CAP=${TOTAL_CAP:-15}    # dollars for the whole experiment (expected about $2 to $5)
METHODS=(ast10-split generic-1q)
W003=-0.32,0.84,1.28,3.73,6.49,1.37   # 003's logistic regression (local model), frozen, for the probe only
PREREG=docs/experiments/004-skillscreen-cohorts.md
mkdir -p "$OUT"

log() { echo "[$(date '+%F %T')] $*" | tee -a "$OUT/progress.log"; }
die() { log "STOPPED: $*"; exit 1; }
py() { uv run --quiet python "$@"; }
spent() {  # dollars OpenRouter reported for every 004 run so far
  py -c "import json,pathlib; print(round(sum((json.loads(l).get('usage') or {}).get('cost', 0) for f in pathlib.Path('$OUT').glob('*/predictions.jsonl') for l in f.read_text().splitlines() if l.strip()), 4))"
}

# --- preflight -------------------------------------------------------------------------------------------
log "start"
git ls-files --error-unmatch "$PREREG" > /dev/null 2>&1 || die "$PREREG is not committed; the pre-registration must exist before any test run"
[ -n "${OPENROUTER_API_KEY:-}" ] || die "OPENROUTER_API_KEY is not set in this shell; export it, then re-run"

# Which state form the hosted model accepts, and which version it serves, from tiny probe calls. On a re-run the
# served version must match the first run's, or the runs would mix model versions.
probe=$(PYTHONPATH=. MODEL="$MODEL" PROVIDER="$PROVIDER" py scripts/exp004_probe_backend.py 2> "$OUT/backend-probe.err") \
  || die "OpenRouter refused the probe call for $MODEL; see $OUT/backend-probe.err"
SF=${probe%% *}; got=${probe#* }
if [ -f "$OUT/backend.txt" ]; then
  read -r first_sf first_got < "$OUT/backend.txt"
  [ "$got" = "$first_got" ] && [ "$SF" = "$first_sf" ] \
    || die "OpenRouter now serves $got ($SF), but the first run used $first_got ($first_sf). Decide with a person first"
else
  echo "$SF $got" > "$OUT/backend.txt"
  log "backend: OpenRouter $MODEL on provider $PROVIDER, served as $got, state sent as a $SF"
  [[ $got == *unpinned ]] && log "note: OpenRouter returned no dated version for $MODEL; a silent model change would not be detected"
fi

[ -d "$SS/.git" ] || git clone --quiet --depth 1 https://github.com/JerroldH/SkillScreen "$SS" || die "could not clone SkillScreen into $SS"

if [ ! -f "$OUT/data-verify-before.txt" ]; then
  py -m svb.data verify | tee "$OUT/data-verify-before.txt" > /dev/null
  if grep -q differs "$OUT/data-verify-before.txt"; then
    # files cached before the pin came from another revision: keep them aside and let the pinned ones download
    mv data "data-before-pin-$(date +%Y%m%d%H%M%S)" && log "cached data differed from the pinned revision; moved aside, pinned files will download"
  fi
fi

if [ ! -f "$OUT/context-check.txt" ]; then
  # The hosted context is 24,576 tokens; skills are sent up to 60,000 characters. On the pinned provider a longer
  # skill is refused and left unscored (amendment 2). Record what the model reads for the longest test skill.
  PYTHONPATH=. MODEL="$MODEL" PROVIDER="$PROVIDER" SF="$SF" CONTEXT_CHECK=1 py scripts/exp004_probe_backend.py > "$OUT/context-check.txt" 2>&1 \
    || log "context check failed; see $OUT/context-check.txt"
  log "context check: $(tr '\n' ' ' < "$OUT/context-check.txt")"
fi

# --- runs ------------------------------------------------------------------------------------------------
run_step() {  # run_step NAME svb.run-args... ; resumes NAME's dir if it exists, retries a few times
  local name=$1; shift
  local dir=$OUT/$name total
  [ -f "$dir/.done" ] && return 0
  [ -d "$dir" ] && [ ! -f "$dir/config.json" ] && rmdir "$dir" 2> /dev/null
  total=$(spent)
  py -c "import sys; sys.exit(0 if $total < $TOTAL_CAP else 1)" || die "spent \$$total of the \$$TOTAL_CAP budget; a person decides whether to raise TOTAL_CAP"
  log "$name: running (spent so far \$$total)"
  local hosted=(--backend openrouter --model "$MODEL" --state-format "$SF" --provider "$PROVIDER" --workers "$WORKERS" --max-cost "$STEP_CAP")
  for attempt in 1 2 3 4 5; do
    if [ -f "$dir/config.json" ]; then
      py -m svb.run "$@" --methods "${METHODS[@]}" "${hosted[@]}" --resume "$dir" >> "$OUT/progress.log" 2>&1 && break
    else
      py -m svb.run "$@" --methods "${METHODS[@]}" "${hosted[@]}" --out "$dir" >> "$OUT/progress.log" 2>&1 && break
    fi
    tail -n 3 "$OUT/progress.log" | grep -q "reached --max-cost" && die "$name reached its \$$STEP_CAP cap; a person decides whether to raise STEP_CAP"
    [ "$attempt" = 5 ] && die "$name failed 5 times; fix the cause, then re-run this script"
    log "$name: attempt $attempt failed; retrying in 2 minutes"; sleep 120
  done
  touch "$dir/.done"; log "$name: done ($(wc -l < "$dir/predictions.jsonl") predictions, spent so far \$$(spent))"
}

field() { py -c "import json,sys; d=json.load(open('$1')); print($2)"; }

analyse() {  # analyse PROTOCOL ; held-out tables, then SkillScreen comparisons at the fpr05 thresholds
  local p=$1 j=$OUT/$1-heldout.json gate
  gate=$([ "$p" = sd ] && echo direct-s42 || echo direct)   # SkillScreen seed 42
  py -m svb.heldout --train "$OUT/$p-train" --val "$OUT/$p-validation" --test "$OUT/$p-test" \
    --baseline generic-1q --json "$j" > "$OUT/$p-heldout.txt" 2>&1 || { log "$p: heldout failed; see $OUT/$p-heldout.txt"; return; }
  py -m svb.skillscreen export "$OUT/$p-test" --method generic-1q --out "$OUT/$p-generic.csv"
  local w; w=$(field "$j" "','.join(str(x) for x in d['weights'])")
  for c in logreg AST04 max; do
    local t; t=$(field "$j" "d['results']['$c']['rules']['fpr05']['threshold']")
    py -m svb.skillscreen compare "$OUT/$p-test" --method ast10-split --combine "$c" --weights="$w" \
      --skillscreen "$SS" --protocol "$p" --threshold "$t" \
      --paired "$OUT/$p-generic.csv" typesafe judge-gpt-5.5 "$gate" > "$OUT/$p-compare-$c.txt" 2>&1 \
      || log "$p: compare $c failed; see $OUT/$p-compare-$c.txt"
  done
  log "$p: analysis written"
}

summary() {
  {
    echo "# Experiment 004 results, $(date '+%F %T')"; echo
    echo "Model: OpenRouter $MODEL on provider $PROVIDER, served as $got, state sent as a $SF. Spent: \$$(spent). Commit: $(git rev-parse --short HEAD)."; echo
    for f in "$OUT"/data-verify-*.txt "$OUT"/context-check.txt "$OUT"/probe-*.txt "$OUT"/sd-heldout.txt \
             "$OUT"/sd-compare-*.txt "$OUT"/msd-heldout.txt "$OUT"/msd-compare-*.txt; do
      [ -f "$f" ] && [ "${f##*/}" != probe-ids.txt ] && { echo "## ${f##*/}"; echo; echo '```'; cat "$f"; echo '```'; echo; }
    done
    echo "## Progress log"; echo; echo '```'; grep -v '^systemone call failed' "$OUT/progress.log" | tail -n 60; echo '```'
  } > "$OUT/summary.md"
}

# 004a: SkillHarm probe (exploratory; read AUROC only)
py -m svb.skillscreen probe --skillscreen "$SS" --out "$OUT/probe-ids.txt" >> "$OUT/progress.log" 2>&1 || die "could not build the probe list"
run_step probe --split source_disjoint --part test --ids "$OUT/probe-ids.txt" --n 5000
for c in max AST04; do
  py -m svb.skillscreen compare "$OUT/probe" --method ast10-split --combine "$c" --skillscreen "$SS" --protocol sd \
    --threshold 0.1 > "$OUT/probe-$c.txt" 2>&1 || log "probe compare $c failed"
done
# 003's weights were fitted on the local model's scores; on the hosted model this row is only indicative
py -m svb.skillscreen compare "$OUT/probe" --method ast10-split --combine logreg --weights="$W003" --skillscreen "$SS" \
  --protocol sd --threshold 0.5 > "$OUT/probe-logreg003.txt" 2>&1 || log "probe compare logreg failed"
py -m svb.skillscreen compare "$OUT/probe" --method generic-1q --skillscreen "$SS" --protocol sd \
  --threshold 0.1 > "$OUT/probe-generic.txt" 2>&1 || log "probe compare generic failed"
summary

# 004b: source-disjoint first (it answers the main question), then structurally disjoint
for p in sd msd; do
  s=$([ "$p" = sd ] && echo source_disjoint || echo m_structural_disjoint)
  run_step "$p-train"      --split "$s" --part train      --n 300  --seed 0
  run_step "$p-validation" --split "$s" --part validation --n 400  --seed 0
  run_step "$p-test"       --split "$s" --part test       --n 5000 --seed 0
  analyse "$p"
  summary
done

py -m svb.data verify > "$OUT/data-verify-after.txt" 2>&1
summary
log "finished; read $OUT/summary.md"
