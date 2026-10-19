"""Build site/data.json for the experiment 004 dashboard.

python scripts/build_dashboard.py [--results results/exp004] [--skillscreen ../SkillScreen] [--out site/data.json]

Per test skill: label, source, our scores (generic-1q, the five checks, and the max, AST04 and logreg combiners)
and three SkillScreen methods for comparison. Thresholds and intervals come from the held-out JSON. No skill text.
"""
import argparse, json, math, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from svb.checks import CHECKS as CHECKS_Q, GENERIC, GENERIC5
from svb.skillscreen import GATE, read_scores, sources

CHECKS = ["AST01", "AST02", "AST03", "AST04", "AST05"]
SPLIT = {"sd": "source_disjoint", "msd": "m_structural_disjoint"}
# SkillScreen methods shown next to ours: their fine-tuned model (seed 42), GPT-5.5 zero-shot, TypeSafe Jev 1.13
THEIRS = {"skillscreen": None, "gpt55": "judge-gpt-5.5", "typesafe": "typesafe"}

def _r(x):  # 6 significant digits: rounding near-1.0 probabilities to fixed decimals would create ties and move AUROC
    return None if x is None else float(f"{x:.6g}")

def protocol(res, ss, p, src):
    held = json.loads((res / f"{p}-heldout.json").read_text())
    w = held["weights"]
    rows = {}
    for line in (res / f"{p}-test" / "predictions.jsonl").read_text().splitlines():
        r = json.loads(line)
        rows.setdefault(r["benchmark_id"], {"label": r["label"], "cats": r["attack_categories"]})[r["method"]] = r["scores"]
    pred = ss / "data/predictions" / p / "test"
    theirs = {k: read_scores(pred / f"{v or GATE[p]}.csv") for k, v in THEIRS.items()}
    skills = []
    for i, r in sorted(rows.items()):
        g = (r.get("generic-1q") or {}).get("malicious")
        c = [(r.get("ast10-split") or {}).get(k) for k in CHECKS]
        full = None not in c
        logreg = 1 / (1 + math.exp(-(w[0] + sum(a * b for a, b in zip(w[1:], c))))) if full else None
        skills.append({"id": i, "y": r["label"], "src": src.get(i, "unknown"), "cat": r["cats"][0] if r["cats"] else "",
                       "s": {"generic": _r(g), "max": _r(max(c)) if full else None, "AST04": _r(c[3]),
                             "logreg": _r(logreg), **{k: _r(v) for k, v in zip(CHECKS, c)},
                             **{k: _r(t.get(i, (None, None))[1]) for k, t in theirs.items()}}})
    res_ = held["results"]
    ours = {"max": "max", "AST04": "AST04", "logreg": "logreg", "generic": "baseline"}
    thresholds = {k: {"youden": res_[v]["threshold"], **{rule: res_[v]["rules"][rule]["threshold"] for rule in ("tpr95", "fpr05")}}
                  for k, v in ours.items()}
    auc = {k: {"auc": res_[v]["auc"], "ci": res_[v]["auc_ci"]} for k, v in ours.items()}
    vs = {k: res_[v]["vs_baseline"] for k, v in ours.items() if "vs_baseline" in res_[v]}
    return {"split": SPLIT[p], "weights": w, "thresholds": thresholds, "auc": auc, "vs_generic": vs, "skills": skills}

def _qs(d):
    return [{"id": k, "text": v[0], "yes": v[1]["true"], "no": v[1]["false"]} for k, v in d.items()]

def questions():
    """Question text comes from svb.checks, so the dashboard shows exactly what the model was asked."""
    sets = {"ast10": _qs(CHECKS_Q), "generic-1q": _qs(GENERIC), "generic-5q": _qs(GENERIC5)}
    sets["ast10-split"] = sets["ast10"]  # same five questions, one call each
    exps = [
        {"id": "001", "title": "Baseline on 200 skills", "asks": "Does splitting detection into one question per AST10 risk find more malicious skills than one generic question?",
         "methods": ["ast10", "generic-1q", "regex"], "data": "random/test, 200 skills (154 malicious, 46 benign)", "model": "clef-flash, local (digest 2aa4d39fd93b)"},
        {"id": "002", "title": "Controls", "asks": "Is the gap from the AST10 content, the max of five scores, or batching the questions into one call?",
         "methods": ["generic-5q", "ast10-split"], "data": "same 200 skills as 001", "model": "clef-flash, local (digest 2aa4d39fd93b)"},
        {"id": "003", "title": "Held-out threshold", "asks": "Do 001 and 002 hold when the threshold and the combination are chosen on separate data?",
         "methods": ["ast10-split"], "data": "random: 200 train, 200 validation, 200 test", "model": "clef-flash, local (digest 0a2a05d6a581)"},
        {"id": "004", "title": "SkillScreen cohorts", "asks": "Do 003's findings hold on SkillScreen's test sets when the skills come from unseen sources, and where does clef-flash sit next to published methods?",
         "methods": ["ast10-split", "generic-1q"], "data": "source-disjoint (1,384 test) and structurally disjoint (1,947 test)", "model": "clef-flash, hosted via OpenRouter"},
    ]
    return {"sets": sets, "experiments": exps}

def main():
    a = argparse.ArgumentParser()
    a.add_argument("--results", default="results/exp004")
    a.add_argument("--skillscreen", default="../SkillScreen")
    a.add_argument("--out", default="site/data.json")
    a = a.parse_args()
    res, ss = pathlib.Path(a.results), pathlib.Path(a.skillscreen)
    src = sources(ss)
    served = (res / "backend.txt").read_text().split()
    data = {"model": "cloudflare/clef-flash", "served": served[1] if len(served) > 1 else "", "protocols": {p: protocol(res, ss, p, src) for p in SPLIT}}
    out = pathlib.Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, separators=(",", ":")))
    out.with_name("questions.json").write_text(json.dumps(questions(), indent=1))
    print(out, f"{out.stat().st_size / 1024:.0f} KB", {p: len(v["skills"]) for p, v in data["protocols"].items()})

if __name__ == "__main__":
    main()
