import json, math, pathlib, sys
from collections import defaultdict
from svb.checks import THRESHOLD

def metrics(rows):
    ok = [r for r in rows if r["flag"] is not None]
    tp = sum(r["label"] == 1 and r["flag"] for r in ok)
    fn = sum(r["label"] == 1 and not r["flag"] for r in ok)
    fp = sum(r["label"] == 0 and r["flag"] for r in ok)
    tn = sum(r["label"] == 0 and not r["flag"] for r in ok)
    p = tp / (tp + fp) if tp + fp else 0.0
    rc = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * p * rc / (p + rc) if p + rc else 0.0
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn, "unparseable": len(rows) - len(ok),
            "precision": p, "recall": rc, "f1": f1}

def per_check(rows):
    hits = defaultdict(lambda: {1: [0, 0], 0: [0, 0]})
    for r in rows:
        for cid, v in r["scores"].items():
            if v is None:
                continue
            h = hits[cid][r["label"]]
            h[0] += v >= THRESHOLD; h[1] += 1
    rate = lambda h: h[0] / h[1] if h[1] else 0.0
    return {c: {"malicious_hit": rate(h[1]), "benign_hit": rate(h[0])} for c, h in hits.items()}

def by_category(rows):
    c = defaultdict(lambda: [0, 0])
    for r in rows:
        if r["label"] != 1 or r["flag"] is None:
            continue
        for cat in r["attack_categories"]:
            c[cat][0] += bool(r["flag"]); c[cat][1] += 1
    return {k: v[0] / v[1] for k, v in c.items()}

def _max(r):
    v = [x for x in r["scores"].values() if x is not None]
    return max(v) if v else None

def _auc(pos, neg):
    """P(malicious score > benign score), ties counting half; mean ranks make it O(n log n), not O(pos x neg)."""
    if not pos or not neg:
        return None
    vals = sorted([(v, 1) for v in pos] + [(v, 0) for v in neg])
    rank_sum, i = 0.0, 0
    while i < len(vals):
        j = i
        while j < len(vals) and vals[j][0] == vals[i][0]:
            j += 1
        rank_sum += (i + 1 + j) / 2 * sum(y for _, y in vals[i:j]); i = j
    return (rank_sum - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg))

def auc(rows):
    """AUC of the max score; rows without scores are skipped."""
    sc = [(r["label"], _max(r)) for r in rows if _max(r) is not None]
    return _auc([s for l, s in sc if l == 1], [s for l, s in sc if l == 0])

def auc_by_check(rows):
    ids = sorted({c for r in rows for c in r["scores"]})
    out = {}
    for c in ids:
        sc = [(r["label"], r["scores"][c]) for r in rows if r["scores"].get(c) is not None]
        out[c] = _auc([s for l, s in sc if l == 1], [s for l, s in sc if l == 0])
    return out

def youden_threshold(rows):
    """Threshold on the max score maximizing TPR - FPR (robust to class imbalance)."""
    sc = [(r["label"], _max(r)) for r in rows if _max(r) is not None]
    pos = [s for l, s in sc if l == 1]; neg = [s for l, s in sc if l == 0]
    best, best_j = 0.5, -1.0
    for t in sorted({s for _, s in sc}):
        j = sum(s >= t for s in pos) / len(pos) - sum(s >= t for s in neg) / len(neg)
        if j > best_j:
            best, best_j = t, j
    return best

def metrics_at(rows, t):
    return metrics([{**r, "flag": None if _max(r) is None else _max(r) >= t} for r in rows])

# ponytail: plain gradient descent, no regularisation; swap for sklearn if features grow
def fit_logreg(X, y, lr=0.5, steps=2000):
    w = [0.0] * (len(X[0]) + 1)
    for _ in range(steps):
        g = [0.0] * len(w)
        for xi, yi in zip(X, y):
            z = w[0] + sum(wj * xj for wj, xj in zip(w[1:], xi))
            e = 1 / (1 + math.exp(-z)) - yi
            g[0] += e
            for j, xj in enumerate(xi):
                g[j + 1] += e * xj
        w = [wj - lr * gj / len(X) for wj, gj in zip(w, g)]
    return w

def predict_logreg(w, X):
    return [1 / (1 + math.exp(-(w[0] + sum(wj * xj for wj, xj in zip(w[1:], xi))))) for xi in X]

SWEEP = (0.5, 0.3, 0.2, 0.1, 0.05)

def sweep(rows, thresholds=SWEEP):
    """P/R/F1 when the max score is cut at each threshold instead of the run's fixed one."""
    scored = [r for r in rows if _max(r) is not None]
    return {t: metrics([{**r, "flag": _max(r) >= t} for r in scored]) for t in thresholds}

def _fmt(x):
    return "n/a" if x is None else f"{x:.2f}"

def report(run_dir):
    rows = [json.loads(l) for l in (pathlib.Path(run_dir) / "predictions.jsonl").read_text().splitlines()]
    out = ["| method | precision | recall | F1 | TP | FP | FN | TN | unparseable |", "|---|---|---|---|---|---|---|---|---|"]
    for m in sorted({r["method"] for r in rows}):
        s = metrics([r for r in rows if r["method"] == m])
        out.append(f"| {m} | {s['precision']:.2f} | {s['recall']:.2f} | {s['f1']:.2f} | {s['tp']} | {s['fp']} | {s['fn']} | {s['tn']} | {s['unparseable']} |")
    llm = sorted({r["method"] for r in rows if r["scores"]})
    if llm:
        by_m = {m: [r for r in rows if r["method"] == m] for m in llm}
        out += ["", "| method | AUC (max score) |", "|---|---|"]
        out += [f"| {m} | {_fmt(auc(by_m[m]))} |" for m in llm]
        out += ["", "| threshold | " + " | ".join(f"{m} P / R / F1" for m in llm) + " |",
                "|---|" + "---|" * len(llm)]
        sw = {m: sweep(by_m[m]) for m in llm}
        for t in SWEEP:
            cells = [f"{s['precision']:.2f} / {s['recall']:.2f} / {s['f1']:.2f}" for s in (sw[m][t] for m in llm)]
            out.append(f"| {t} | " + " | ".join(cells) + " |")
    ast = [r for r in rows if r["method"] == "ast10"]
    if ast:
        out += ["", "| check | AUC |", "|---|---|"]
        out += [f"| {c} | {_fmt(v)} |" for c, v in auc_by_check(ast).items()]
        out += ["", "| check | hit on malicious | hit on benign |", "|---|---|---|"]
        out += [f"| {c} | {v['malicious_hit']:.2f} | {v['benign_hit']:.2f} |" for c, v in sorted(per_check(ast).items())]
        out += ["", "| attack category | ast10 recall |", "|---|---|"]
        out += [f"| {k} | {v:.2f} |" for k, v in sorted(by_category(ast).items())]
    return "\n".join(out)

if __name__ == "__main__":
    print(report(sys.argv[1]))

def auc_diff_ci(rows_a, rows_b, n_boot=2000, seed=0):
    """95% paired-bootstrap CI of AUC(a) - AUC(b). Rows are paired by benchmark_id."""
    import random
    a = {r["benchmark_id"]: r for r in rows_a}
    b = {r["benchmark_id"]: r for r in rows_b}
    ids = sorted(a.keys() & b.keys())
    rng, diffs = random.Random(seed), []
    for _ in range(n_boot):
        pick = [ids[rng.randrange(len(ids))] for _ in ids]
        da, db = auc([a[i] for i in pick]), auc([b[i] for i in pick])
        if da is not None and db is not None:
            diffs.append(da - db)
    diffs.sort()
    return diffs[int(0.025 * len(diffs))], diffs[int(0.975 * len(diffs)) - 1]

def bootstrap_ci(rows, stat, n_boot=2000, seed=0):
    """95% percentile-bootstrap CI of stat(rows); resamples where stat is None are dropped."""
    import random
    rng, vals = random.Random(seed), []
    for _ in range(n_boot):
        v = stat([rows[rng.randrange(len(rows))] for _ in rows])
        if v is not None:
            vals.append(v)
    vals.sort()
    return vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]
