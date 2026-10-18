"""Held-out evaluation: python -m svb.heldout --train runs/A --val runs/B --test runs/C"""
import argparse, json, pathlib
from svb.score import auc, auc_diff_ci, bootstrap_ci, fit_logreg, metrics_at, predict_logreg, youden_threshold

CHECK_IDS = ["AST01", "AST02", "AST03", "AST04", "AST05"]

def load_run(d, part, method="ast10-split"):
    d = pathlib.Path(d)
    cfg = json.loads((d / "config.json").read_text())
    got = cfg.get("part", "test")  # ponytail: runs from before --part existed were all test
    if got != part:
        raise ValueError(f"{d} is a {got} run, expected {part}")
    rows = [r for r in map(json.loads, (d / "predictions.jsonl").read_text().splitlines()) if r["method"] == method]
    if not rows:
        raise ValueError(f"{d} has no {method} predictions")
    ids = [r["benchmark_id"] for r in rows]
    if len(ids) != len(set(ids)):
        raise ValueError(f"{d} has duplicate {method} rows")
    if set(ids) != set(cfg["sample_ids"]):
        raise ValueError(f"{d} is incomplete: {len(set(cfg['sample_ids']) - set(ids))} sampled skills have no {method} row")
    if {r["label"] for r in rows if any(v is not None for v in r["scores"].values())} != {0, 1}:
        raise ValueError(f"{d} needs both malicious and benign skills with scores")
    return cfg, rows

def check_compatible(cfgs):
    ref = cfgs[0]
    for c in cfgs[1:]:
        for k in ("model_digest", "split"):
            if c[k] != ref[k]:
                raise ValueError(f"runs differ in {k}")
        if any(c["prompt_hashes"][i] != ref["prompt_hashes"][i] for i in CHECK_IDS):
            raise ValueError("runs differ in AST check prompts")
    ids = [set(c["sample_ids"]) for c in cfgs]
    if any(ids[i] & ids[j] for i in range(len(ids)) for j in range(i + 1, len(ids))):
        raise ValueError("train, validation and test share skills")

def _full(r):
    v = [r["scores"].get(c) for c in CHECK_IDS]
    return None if None in v else v

def as_rows(rows, score):
    """Re-score rows with one combined score so auc/youden/metrics_at apply unchanged."""
    out = []
    for r in rows:
        s = score(r)
        out.append({**r, "scores": {} if s is None else {"s": s}})
    return out

def rates(rows, t):
    m = metrics_at(rows, t)
    tpr = m["tp"] / (m["tp"] + m["fn"]) if m["tp"] + m["fn"] else None
    fpr = m["fp"] / (m["fp"] + m["tn"]) if m["fp"] + m["tn"] else None
    return tpr, fpr

def evaluate(train, val, test, n_boot=2000, seed=0):
    fit = [r for r in train if _full(r)]
    if not fit:
        raise ValueError("no fully scored train rows to fit the logistic regression on")
    # ponytail: unweighted, unregularised fit on 5 features; Youden on validation absorbs class imbalance
    w = fit_logreg([_full(r) for r in fit], [r["label"] for r in fit])
    combiners = {
        "max": lambda r: max([v for v in r["scores"].values() if v is not None], default=None),
        "AST04": lambda r: r["scores"].get("AST04"),
        "logreg": lambda r: None if _full(r) is None else predict_logreg(w, [_full(r)])[0],
    }
    scored = {name: as_rows(test, f) for name, f in combiners.items()}
    # compare every combiner on the skills all of them could score, so paired differences are like for like
    common = set.intersection(*({r["benchmark_id"] for r in rs if r["scores"]} for rs in scored.values()))
    res = {}
    for name, f in combiners.items():
        t = youden_threshold(as_rows(val, f))
        rs = [r if r["benchmark_id"] in common else {**r, "scores": {}} for r in scored[name]]
        tpr, fpr = rates(rs, t)
        res[name] = {"threshold": t, "auc": auc(rs), "auc_ci": bootstrap_ci(rs, auc, n_boot, seed),
                     "tpr": tpr, "tpr_ci": bootstrap_ci(rs, lambda x: rates(x, t)[0], n_boot, seed),
                     "fpr": fpr, "fpr_ci": bootstrap_ci(rs, lambda x: rates(x, t)[1], n_boot, seed),
                     "unscored": sum(not r["scores"] for r in scored[name]), "rows": rs}
    return res, w

def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--train", required=True)
    p.add_argument("--val", required=True)
    p.add_argument("--test", required=True)
    p.add_argument("--method", default="ast10-split")
    p.add_argument("--n-boot", type=int, default=2000)
    a = p.parse_args(argv)
    (ct, tr), (cv, va), (cx, te) = (load_run(a.train, "train", a.method), load_run(a.val, "validation", a.method),
                                    load_run(a.test, "test", a.method))
    check_compatible([ct, cv, cx])
    res, w = evaluate(tr, va, te, a.n_boot)
    mal = sum(r["label"] for r in te)
    print(f"train skills: {len(tr)}, validation skills: {len(va)}, test skills: {len(te)} ({mal} malicious, {len(te) - mal} benign)\n")
    print("| combiner | threshold (from validation) | test AUC [95% CI] | test TPR [95% CI] | test FPR [95% CI] | unscored |")
    print("|---|---|---|---|---|---|")
    ci = lambda v, c: f"{v:.3f} [{c[0]:.3f}, {c[1]:.3f}]"
    for m, r in res.items():
        print(f"| {m} | {r['threshold']:.3f} | {ci(r['auc'], r['auc_ci'])} | {ci(r['tpr'], r['tpr_ci'])} | {ci(r['fpr'], r['fpr_ci'])} | {r['unscored']} |")
    print("\n| paired difference on test | AUC diff [95% CI] |\n|---|---|")
    for x, y in (("logreg", "max"), ("AST04", "max"), ("logreg", "AST04")):
        lo, hi = auc_diff_ci(res[x]["rows"], res[y]["rows"], a.n_boot)
        print(f"| {x} - {y} | {res[x]['auc'] - res[y]['auc']:+.3f} [{lo:+.3f}, {hi:+.3f}] |")
    print("\n| logreg weight | " + " | ".join(["intercept"] + CHECK_IDS) + " |")
    print("|---|" + "---|" * len(w))
    print("| value | " + " | ".join(f"{x:+.2f}" for x in w) + " |")

if __name__ == "__main__":
    main()
