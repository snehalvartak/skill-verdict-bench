"""R1: does an earlier run reproduce? python scripts/exp005_reproduce.py RUN_A RUN_B

Compares ast10-split (max of its five scores) and generic-1q on the skills both runs scored: Spearman correlation
of the scores, the largest absolute difference, and each run's AUROC. A silent model change would show here.
"""
import json, pathlib, sys

def scores(run):
    out = {}
    for line in (pathlib.Path(run) / "predictions.jsonl").read_text().splitlines():
        r = json.loads(line)
        v = [x for x in r["scores"].values() if x is not None]
        if not v: continue
        s = max(v) if r["method"] == "ast10-split" else r["scores"].get("malicious") if r["method"] == "generic-1q" else None
        if s is not None: out[(r["method"], r["benchmark_id"])] = (s, r["label"])
    return out

def ranks(x):
    o = sorted(range(len(x)), key=lambda i: x[i]); r = [0.0] * len(x); i = 0
    while i < len(o):
        j = i
        while j < len(o) and x[o[j]] == x[o[i]]: j += 1
        for k in range(i, j): r[o[k]] = (i + j + 1) / 2
        i = j
    return r

def corr(a, b):
    n = len(a); ma, mb = sum(a) / n, sum(b) / n
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b)); va = sum((x - ma) ** 2 for x in a); vb = sum((y - mb) ** 2 for y in b)
    return cov / (va * vb) ** 0.5 if va and vb else float("nan")

def auroc(s, y):
    r = ranks(s); pos = sum(y); neg = len(y) - pos
    return (sum(r[i] for i in range(len(y)) if y[i]) - pos * (pos + 1) / 2) / (pos * neg)

def main(a, b):
    A, B = scores(a), scores(b)
    for m in ("ast10-split", "generic-1q"):
        ids = sorted(k for k in A if k[0] == m and k in B)
        if not ids: print(f"{m}: no skills in common"); continue
        sa, sb, y = [A[k][0] for k in ids], [B[k][0] for k in ids], [A[k][1] for k in ids]
        print(f"{m}: {len(ids)} skills in common; Spearman {corr(ranks(sa), ranks(sb)):.4f}; largest score difference "
              f"{max(abs(p - q) for p, q in zip(sa, sb)):.4f}; AUROC {auroc(sa, y):.4f} vs {auroc(sb, y):.4f}")

if __name__ == "__main__":
    main(*sys.argv[1:3])
