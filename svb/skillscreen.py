"""Score our runs with SkillScreen's Table 1 rules and compare them skill by skill with its released predictions.

SkillScreen: Huang et al., arXiv 2610.17727, github.com/JerroldH/SkillScreen. Point --skillscreen at a clone.
Its predictions are CC BY 4.0 (c) SkillScreen contributors; they are read in place and never copied here.

  python -m svb.skillscreen export runs/<id> --method ast10 --out ast10.csv
  python -m svb.skillscreen compare runs/<id> --method ast10 --skillscreen ../SkillScreen --protocol sd --threshold 0.12
  python -m svb.skillscreen probe --skillscreen ../SkillScreen --out probe-ids.txt
"""
import argparse, csv, json, math, pathlib, random
from collections import defaultdict
from svb.score import _max

def auroc(labels, values):
    """SkillScreen's rule: ties get their mean rank, missing scores are dropped."""
    pairs = sorted((v, y) for v, y in zip(values, labels) if v is not None)
    pos = sum(y for _, y in pairs); neg = len(pairs) - pos
    if not pos or not neg:
        return None
    rank_sum, i = 0.0, 0
    while i < len(pairs):
        j = i + 1
        while j < len(pairs) and pairs[j][0] == pairs[i][0]:
            j += 1
        rank_sum += (i + 1 + j) / 2 * sum(y for _, y in pairs[i:j]); i = j
    return (rank_sum - pos * (pos + 1) / 2) / (pos * neg)

def fpr_at_recall(labels, values, recall=0.99):
    """SkillScreen's FPR@99 rule: cut at the k-th highest malicious score, ties kept, missing counts as +inf."""
    v = [math.inf if x is None else x for x in values]
    pos = sorted((x for x, y in zip(v, labels) if y == 1), reverse=True)
    neg = [x for x, y in zip(v, labels) if y == 0]
    if not pos or not neg:
        return None
    k = max(1, min(math.ceil(recall * len(pos) - 1e-12), len(pos)))
    t = pos[k - 1]
    return {"fpr": sum(x >= t for x in neg) / len(neg), "recall": sum(x >= t for x in pos) / len(pos),
            "threshold": t if math.isfinite(t) else None}

def at_threshold(labels, values, t):
    """Recall and FPR at a fixed cut; a missing score counts as flagged (SkillScreen's review policy)."""
    flag = [v is None or v >= t for v in values]
    pos = [f for f, y in zip(flag, labels) if y == 1]; neg = [f for f, y in zip(flag, labels) if y == 0]
    return {"recall": sum(pos) / len(pos) if pos else None, "fpr": sum(neg) / len(neg) if neg else None}

def run_scores(run_dir, method):
    """{benchmark_id: (label, score)} for one method; LLM methods score by the max check, regex by its flag."""
    out = {}
    for line in (pathlib.Path(run_dir) / "predictions.jsonl").read_text().splitlines():
        r = json.loads(line)
        if r["method"] == method:
            s = _max(r) if r["scores"] else (None if r["flag"] is None else float(r["flag"]))
            out[r["benchmark_id"]] = (r["label"], s)
    if not out:
        raise ValueError(f"no {method} rows in {run_dir}")
    return out

def export(scores, out):
    with open(out, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["benchmark_id", "label", "score"])
        for i in sorted(scores):
            label, s = scores[i]
            w.writerow([i, label, "" if s is None else repr(s)])

def read_scores(path):
    with open(path) as f:
        return {r["benchmark_id"]: (int(r["label"]), float(r["score"]) if r.get("score") else None)
                for r in csv.DictReader(f)}

def sources(root):
    with open(pathlib.Path(root) / "data/metadata/benchmark_metadata.csv") as f:
        return {r["benchmark_id"]: r["source_name"] for r in csv.DictReader(f)}

def _row(name, labels, values, t):
    f99, at = fpr_at_recall(labels, values), at_threshold(labels, values, t)
    return {"method": name, "auroc": auroc(labels, values), "fpr99": f99 and f99["fpr"],
            "recall": at["recall"], "fpr": at["fpr"]}

def compare(scores, root, protocol, t=0.5, gate="direct-s42"):
    """Our method next to every SkillScreen test method on the skills both scored.

    `t` applies to our scores (choose it on validation); SkillScreen's methods keep their native 0.5.
    `gate` is the SkillScreen file used as the first stage of the cascade.
    """
    pred = pathlib.Path(root) / "data/predictions" / protocol / "test"
    theirs = {p.stem: read_scores(p) for p in sorted(pred.glob("*.csv"))}
    cohort = theirs[gate]
    ids = sorted(set(scores) & set(cohort))
    if not ids:
        raise ValueError(f"run shares no skills with SkillScreen's {protocol} test cohort")
    bad = [i for i in ids if scores[i][0] != cohort[i][0]]
    if bad:
        raise ValueError(f"labels differ from SkillScreen's for {len(bad)} skills, e.g. {bad[0]}")
    labels = [cohort[i][0] for i in ids]
    rows = [_row("ours", labels, [scores[i][1] for i in ids], t)]
    rows += [_row(n, labels, [s[i][1] for i in ids], 0.5) for n, s in theirs.items()]
    src, by_src = sources(root), defaultdict(lambda: defaultdict(lambda: [0, 0, 0]))
    for i in ids:
        cell = by_src[src.get(i, "unknown")][cohort[i][0]]
        cell[0] += 1
        cell[1] += scores[i][1] is None or scores[i][1] >= t
        cell[2] += cohort[i][1] is None or cohort[i][1] >= 0.5
    both = [(cohort[i][1] is None or cohort[i][1] >= 0.5) and (scores[i][1] is None or scores[i][1] >= t) for i in ids]
    pos = [f for f, y in zip(both, labels) if y == 1]; neg = [f for f, y in zip(both, labels) if y == 0]
    cascade = {"recall": sum(pos) / len(pos) if pos else None, "fpr": sum(neg) / len(neg) if neg else None}
    return {"n": len(ids), "cohort": len(cohort), "rows": rows, "by_source": by_src, "cascade": cascade}

def probe_ids(root, n_harm=100, seed=0):
    """Source-disjoint test skills that decide the cascade story: a SkillHarm sample (zero-shot TypeSafe
    catches none of them) and every SkillFortifyBench benign skill (SkillScreen flags all of them)."""
    cohort, src = read_scores(pathlib.Path(root) / "data/cohorts/sd-test.csv"), sources(root)
    harm = sorted(i for i, (l, _) in cohort.items() if l == 1 and src[i] == "SkillHarm")
    fort = sorted(i for i, (l, _) in cohort.items() if l == 0 and src[i] == "SkillFortifyBench")
    return sorted(random.Random(seed).sample(harm, min(n_harm, len(harm))) + fort)

def _f(x):
    return "n/a" if x is None else f"{x:.3f}"

def report(res, t, gate):
    out = [f"Skills compared: {res['n']} of SkillScreen's {res['cohort']}. Ours cut at {t}, theirs at 0.5.", "",
           "| method | AUROC | FPR@99 | recall | FPR |", "|---|---|---|---|---|"]
    out += [f"| {r['method']} | {_f(r['auroc'])} | {_f(r['fpr99'])} | {_f(r['recall'])} | {_f(r['fpr'])} |" for r in res["rows"]]
    out += ["", f"| source | label | skills | ours flagged | {gate} flagged |", "|---|---|---|---|---|"]
    for s in sorted(res["by_source"]):
        for label in (1, 0):
            if label in res["by_source"][s]:
                n, a, b = res["by_source"][s][label]
                out.append(f"| {s} | {'malicious' if label else 'benign'} | {n} | {a} | {b} |")
    c = res["cascade"]
    out += ["", f"Cascade ({gate} flags, then ours must also flag): recall {_f(c['recall'])}, FPR {_f(c['fpr'])}"]
    return "\n".join(out)

if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("export"); e.add_argument("run"); e.add_argument("--method", required=True); e.add_argument("--out", required=True)
    c = sub.add_parser("compare"); c.add_argument("run"); c.add_argument("--method", required=True)
    c.add_argument("--skillscreen", required=True); c.add_argument("--protocol", choices=["msd", "sd"], required=True)
    c.add_argument("--threshold", type=float, default=0.5); c.add_argument("--gate", default="direct-s42")
    b = sub.add_parser("probe"); b.add_argument("--skillscreen", required=True); b.add_argument("--out", required=True)
    b.add_argument("--n-harm", type=int, default=100); b.add_argument("--seed", type=int, default=0)
    a = p.parse_args()
    if a.cmd == "export":
        export(run_scores(a.run, a.method), a.out)
    elif a.cmd == "compare":
        print(report(compare(run_scores(a.run, a.method), a.skillscreen, a.protocol, a.threshold, a.gate), a.threshold, a.gate))
    else:
        ids = probe_ids(a.skillscreen, a.n_harm, a.seed)
        pathlib.Path(a.out).write_text("".join(i + "\n" for i in ids))
        print(f"{len(ids)} ids -> {a.out}")
