"""Compare methods across run dirs: python -m svb.compare runs/A runs/B ..."""
import json, sys
from svb.score import read_predictions, auc, auc_by_check, auc_diff_ci, metrics_at, youden_threshold

PAIRS = [("ast10", "generic-1q"), ("ast10", "generic-5q"), ("generic-5q", "generic-1q"),
         ("ast10-split", "ast10"), ("ast10-split", "generic-5q")]

def load(dirs):
    rows = [r for d in dirs for r in read_predictions(d)]
    by = {}
    for r in rows:
        by.setdefault(r["method"], []).append(r)
    return by

def main(dirs):
    by = load(dirs)
    llm = [m for m in ("ast10", "ast10-split", "generic-1q", "generic-5q") if m in by]
    print("| method | AUC | Youden t | TPR | FPR |\n|---|---|---|---|---|")
    for m in llm:
        if len({r["label"] for r in by[m]}) < 2:
            print(f"| {m} | n/a (needs malicious and benign skills) | | | |"); continue
        t = youden_threshold(by[m]); s = metrics_at(by[m], t)
        print(f"| {m} | {auc(by[m]):.3f} | {t:.3f} | {s['recall']:.2f} | {s['fp'] / (s['fp'] + s['tn']):.2f} |")
    print("\n| paired difference | AUC diff 95% CI |\n|---|---|")
    for a, b in PAIRS:
        if a in by and b in by and auc(by[a]) is not None and auc(by[b]) is not None:
            lo, hi = auc_diff_ci(by[a], by[b]); print(f"| {a} - {b} | {auc(by[a]) - auc(by[b]):+.3f} [{lo:+.3f}, {hi:+.3f}] |")
    print("\n| check | ast10 (batched) | ast10-split |\n|---|---|---|")
    if "ast10" in by and "ast10-split" in by:
        a, b = auc_by_check(by["ast10"]), auc_by_check(by["ast10-split"])
        for c in sorted(a):
            print(f"| {c} | {a[c]:.3f} | {b[c]:.3f} |")
    if "generic-5q" in by:
        print("\n| paraphrase | AUC |\n|---|---|")
        for k, v in sorted(auc_by_check(by["generic-5q"]).items()):
            print(f"| {k} | {v:.3f} |")

if __name__ == "__main__":
    main(sys.argv[1:])
