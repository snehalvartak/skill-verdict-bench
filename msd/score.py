import json, pathlib, sys
from collections import defaultdict
from msd.checks import THRESHOLD

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

def report(run_dir):
    rows = [json.loads(l) for l in (pathlib.Path(run_dir) / "predictions.jsonl").read_text().splitlines()]
    out = ["| method | precision | recall | F1 | TP | FP | FN | TN | unparseable |", "|---|---|---|---|---|---|---|---|---|"]
    for m in sorted({r["method"] for r in rows}):
        s = metrics([r for r in rows if r["method"] == m])
        out.append(f"| {m} | {s['precision']:.2f} | {s['recall']:.2f} | {s['f1']:.2f} | {s['tp']} | {s['fp']} | {s['fn']} | {s['tn']} | {s['unparseable']} |")
    ast = [r for r in rows if r["method"] == "ast10"]
    if ast:
        out += ["", "| check | hit on malicious | hit on benign |", "|---|---|---|"]
        out += [f"| {c} | {v['malicious_hit']:.2f} | {v['benign_hit']:.2f} |" for c, v in sorted(per_check(ast).items())]
        out += ["", "| attack category | ast10 recall |", "|---|---|"]
        out += [f"| {k} | {v:.2f} |" for k, v in sorted(by_category(ast).items())]
    return "\n".join(out)

if __name__ == "__main__":
    print(report(sys.argv[1]))
