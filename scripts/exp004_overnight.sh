#!/usr/bin/env bash
# Experiment 004, unattended. Plan: docs/superpowers/plans/2026-10-19-exp004-skillscreen-cohorts.md
#
# Start it from the repo root and leave it:
#   macOS:  caffeinate -is nohup bash scripts/exp004_overnight.sh > /dev/null 2>&1 &
#   Linux:  nohup bash scripts/exp004_overnight.sh > /dev/null 2>&1 &
# Watch:    tail -f runs/exp004/progress.log
# Result:   runs/exp004/summary.md (written at the end; also after each protocol)
#
# Safe to re-run at any time: every step resumes where it stopped and finished steps are skipped.
# It stops, and says why in progress.log, if the model, the data or the pre-registration is not what 004 needs.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1

SS=${SKILLSCREEN:-../SkillScreen}
OUT=runs/exp004
DIGEST=0a2a05d6a581        # experiment 003's clef-flash; every 004 run must use the same one
METHODS=(ast10-split naive-llm)
W003=-0.32,0.84,1.28,3.73,6.49,1.37   # 003's logistic regression, frozen, for the probe only
PREREG=docs/experiments/004-skillscreen-cohorts.md
mkdir -p "$OUT"

log() { echo "[$(date '+%F %T')] $*" | tee -a "$OUT/progress.log"; }
die() { log "STOPPED: $*"; exit 1; }
py() { uv run --quiet python "$@"; }

# --- preflight -------------------------------------------------------------------------------------------
log "start"
git ls-files --error-unmatch "$PREREG" > /dev/null 2>&1 || die "$PREREG is not committed; the pre-registration must exist before any test run"
curl -sf http://localhost:11434/api/tags > /dev/null || die "Ollama is not answering on localhost:11434; start it, then re-run"
got=$(py -c 'from svb.systemone import model_digest; print(model_digest())' 2> /dev/null) || die "clef-flash:latest is not in Ollama"
[[ $got == "$DIGEST"* ]] || die "clef-flash digest is ${got:0:12}, expected $DIGEST. Do not re-pull; decide with a person first"
[ -d "$SS/.git" ] || git clone --quiet --depth 1 https://github.com/JerroldH/SkillScreen "$SS" || die "could not clone SkillScreen into $SS"

if [ ! -f "$OUT/data-verify-before.txt" ]; then
  py -m svb.data verify | tee "$OUT/data-verify-before.txt" > /dev/null
  if grep -q differs "$OUT/data-verify-before.txt"; then
    # files cached before the pin came from another revision: keep them aside and let the pinned ones download
    mv data "data-before-pin-$(date +%Y%m%d%H%M%S)" && log "cached data differed from the pinned revision; moved aside, pinned files will download"
  fi
fi

if [ ! -f "$OUT/context-check.txt" ]; then
  # Ollama's default context for clef-flash is 16,384 tokens and skills are sent up to 60,000 characters.
  # Record what the model actually reads for the longest test skill; a person decides what to do about it.
  py - > "$OUT/context-check.txt" 2>&1 <<'EOF' || log "context check failed; see $OUT/context-check.txt"
import json, urllib.request
from svb.checks import truncate
from svb.data import load
for split in ("source_disjoint", "m_structural_disjoint"):
    df = load(split, "test")
    text, cut = truncate(df.text[df.text.str.len().idxmax()])
    body = {"model": "clef-flash", "state": text, "questions": {"q": {"type": "noul", "instructions": "Is this text long?",
            "criteria": {"true": "yes", "false": "no"}}}}
    req = urllib.request.Request("http://localhost:11434/v1/systemone", json.dumps(body).encode(), {"Content-Type": "application/json"})
    usage = json.load(urllib.request.urlopen(req, timeout=600)).get("usage", {})
    tok = usage.get("input_tokens")
    warn = " <- WARNING: far fewer tokens than characters/4 suggests; the context window may be cutting long skills" \
        if isinstance(tok, int) and tok < len(text) / 6 else ""
    print(f"{split}: longest test skill sent as {len(text)} characters (cut at 60,000: {cut}); model read {tok} input tokens{warn}")
EOF
  log "context check: $(tr '\n' ' ' < "$OUT/context-check.txt")"
fi

# --- runs ------------------------------------------------------------------------------------------------
run_step() {  # run_step NAME svb.run-args... ; resumes NAME's dir if it exists, retries a few times
  local name=$1; shift
  local dir=$OUT/$name
  [ -f "$dir/.done" ] && return 0
  [ -d "$dir" ] && [ ! -f "$dir/config.json" ] && rmdir "$dir" 2> /dev/null
  log "$name: running"
  for attempt in 1 2 3 4 5; do
    if [ -f "$dir/config.json" ]; then
      py -m svb.run "$@" --methods "${METHODS[@]}" --resume "$dir" >> "$OUT/progress.log" 2>&1 && break
    else
      py -m svb.run "$@" --methods "${METHODS[@]}" --out "$dir" >> "$OUT/progress.log" 2>&1 && break
    fi
    [ "$attempt" = 5 ] && die "$name failed 5 times; fix the cause, then re-run this script"
    log "$name: attempt $attempt failed; retrying in 2 minutes"; sleep 120
  done
  touch "$dir/.done"; log "$name: done ($(wc -l < "$dir/predictions.jsonl") predictions)"
}

field() { py -c "import json,sys; d=json.load(open('$1')); print($2)"; }

analyse() {  # analyse PROTOCOL ; held-out tables, then SkillScreen comparisons at the fpr05 thresholds
  local p=$1 j=$OUT/$1-heldout.json gate
  gate=$([ "$p" = sd ] && echo direct-s42 || echo direct)   # SkillScreen seed 42
  py -m svb.heldout --train "$OUT/$p-train" --val "$OUT/$p-validation" --test "$OUT/$p-test" \
    --baseline naive-llm --json "$j" > "$OUT/$p-heldout.txt" 2>&1 || { log "$p: heldout failed; see $OUT/$p-heldout.txt"; return; }
  py -m svb.skillscreen export "$OUT/$p-test" --method naive-llm --out "$OUT/$p-naive.csv"
  local w; w=$(field "$j" "','.join(str(x) for x in d['weights'])")
  for c in logreg AST04 max; do
    local t; t=$(field "$j" "d['results']['$c']['rules']['fpr05']['threshold']")
    py -m svb.skillscreen compare "$OUT/$p-test" --method ast10-split --combine "$c" --weights="$w" \
      --skillscreen "$SS" --protocol "$p" --threshold "$t" \
      --paired "$OUT/$p-naive.csv" typesafe judge-gpt-5.5 "$gate" > "$OUT/$p-compare-$c.txt" 2>&1 \
      || log "$p: compare $c failed; see $OUT/$p-compare-$c.txt"
  done
  log "$p: analysis written"
}

summary() {
  {
    echo "# Experiment 004 results, $(date '+%F %T')"; echo
    echo "Model digest: $got. Commit: $(git rev-parse --short HEAD)."; echo
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
py -m svb.skillscreen compare "$OUT/probe" --method ast10-split --combine logreg --weights="$W003" --skillscreen "$SS" \
  --protocol sd --threshold 0.5 > "$OUT/probe-logreg003.txt" 2>&1 || log "probe compare logreg failed"
py -m svb.skillscreen compare "$OUT/probe" --method naive-llm --skillscreen "$SS" --protocol sd \
  --threshold 0.1 > "$OUT/probe-naive.txt" 2>&1 || log "probe compare naive failed"
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
