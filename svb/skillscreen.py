"""Score our runs with SkillScreen's Table 1 rules and compare them skill by skill with its released predictions.

SkillScreen: Huang et al., arXiv 2610.17727, github.com/JerroldH/SkillScreen. Point --skillscreen at a clone.
Its predictions are CC BY 4.0 (c) SkillScreen contributors; they are read in place and never copied here.

  python -m svb.skillscreen export runs/<id> --method ast10 --out ast10.csv
  python -m svb.skillscreen compare runs/<id> --method ast10 --skillscreen ../SkillScreen --protocol sd --threshold <t>
  python -m svb.skillscreen compare runs/<id> --method ast10-split --combine logreg --weights=-0.32,0.84,1.28,3.73,6.49,1.37 \
      --skillscreen ../SkillScreen --protocol sd --threshold <t> --paired typesafe

--threshold has no default: this model's scores sit far below 0.5, so choose the cut on validation.
  python -m svb.skillscreen probe --skillscreen ../SkillScreen --out probe-ids.txt
"""
import argparse, csv, json, math, pathlib, random, sys
from collections import defaultdict
from svb.score import _max, predict_logreg, read_predictions

CHECK_IDS = ["AST01", "AST02", "AST03", "AST04", "AST05"]

PROTOCOL_SPLIT = {"msd": "m_structural_disjoint", "sd": "source_disjoint"}
GATE = {"msd": "direct", "sd": "direct-s42"}  # SkillScreen seed 42; its file is named differently per protocol

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

def combiner(combine="max", weights=None):
    """Score one prediction row: "max" of its checks, a single check id (e.g. "AST04"), or "logreg" with
    weights [intercept, AST01..AST05] as printed by svb.heldout. Rows without the needed scores give None."""
    if combine == "max":
        return _max
    if combine in CHECK_IDS:
        return lambda r: r["scores"].get(combine)
    if combine == "logreg":
        if not weights or len(weights) != len(CHECK_IDS) + 1:
            raise ValueError(f"logreg needs {len(CHECK_IDS) + 1} weights: intercept, then {', '.join(CHECK_IDS)}")
        def lr(r):
            x = [r["scores"].get(c) for c in CHECK_IDS]
            return None if None in x else predict_logreg(weights, [x])[0]
        return lr
    raise ValueError(f"unknown combiner {combine!r}: use max, logreg or one of {', '.join(CHECK_IDS)}")

def run_scores(run_dir, method, combine=_max):
    """{benchmark_id: (label, score)} for one method; LLM rows go through `combine`, regex scores by its flag."""
    out = {}
    for r in read_predictions(run_dir):
        if r["method"] == method:
            s = combine(r) if r["scores"] else (None if r["flag"] is None else float(r["flag"]))
            out[r["benchmark_id"]] = (r["label"], s)
    if not out:
        raise ValueError(f"no {method} rows in {run_dir}")
    return out

def check_run(run_dir, protocol):
    """Refuse a run whose split or part is not the SkillScreen test set it would be compared with."""
    cfg = json.loads((pathlib.Path(run_dir) / "config.json").read_text())
    split, part = cfg.get("split"), cfg.get("part", "test")  # runs from before --part are test runs
    if split != PROTOCOL_SPLIT[protocol] or part != "test":
        raise ValueError(f"{run_dir} is split={split} part={part}; --protocol {protocol} needs "
                         f"split={PROTOCOL_SPLIT[protocol]} part=test")

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

def _row(name, ids, scores, t):
    """Metrics over the ids this file covers; n says how many, so a partial file is visible, not fatal."""
    have = [i for i in ids if i in scores]
    labels, values = [scores[i][0] for i in have], [scores[i][1] for i in have]
    f99, at = fpr_at_recall(labels, values), at_threshold(labels, values, t)
    return {"method": name, "n": len(have), "auroc": auroc(labels, values), "fpr99": f99 and f99["fpr"],
            "recall": at["recall"], "fpr": at["fpr"]}

def compare(scores, root, protocol, t, gate=None):
    """Our method next to every SkillScreen test method on the skills both scored.

    `t` applies to our scores (choose it on validation); SkillScreen's methods keep their native 0.5.
    `gate` is the SkillScreen file used as the first stage of the cascade; it must cover every compared skill.
    """
    root, gate = pathlib.Path(root), gate or GATE[protocol]
    cohort = read_scores(root / "data/cohorts" / f"{protocol}-test.csv")
    pred = root / "data/predictions" / protocol / "test"
    theirs = {p.stem: read_scores(p) for p in sorted(pred.glob("*.csv"))}
    if gate not in theirs:
        raise ValueError(f"no gate file {gate}.csv in {pred}")
    ids = sorted(set(scores) & set(cohort))
    if not ids:
        raise ValueError(f"run shares no skills with SkillScreen's {protocol} test cohort")
    bad = [i for i in ids if scores[i][0] != cohort[i][0]]
    if bad:
        raise ValueError(f"labels differ from SkillScreen's for {len(bad)} skills, e.g. {bad[0]}")
    missing = [i for i in ids if i not in theirs[gate]]
    if missing:
        raise ValueError(f"gate {gate} has no prediction for {len(missing)} compared skills, e.g. {missing[0]}")
    g = theirs[gate]
    rows = [_row("ours", ids, scores, t)] + [_row(n, ids, s, 0.5) for n, s in theirs.items()]
    src, by_src = sources(root), defaultdict(lambda: defaultdict(lambda: [0, 0, 0]))
    for i in ids:
        cell = by_src[src.get(i, "unknown")][cohort[i][0]]
        cell[0] += 1
        cell[1] += scores[i][1] is None or scores[i][1] >= t
        cell[2] += g[i][1] is None or g[i][1] >= 0.5
    labels = [cohort[i][0] for i in ids]
    both = [(g[i][1] is None or g[i][1] >= 0.5) and (scores[i][1] is None or scores[i][1] >= t) for i in ids]
    pos = [f for f, y in zip(both, labels) if y == 1]; neg = [f for f, y in zip(both, labels) if y == 0]
    cascade = {"recall": sum(pos) / len(pos) if pos else None, "fpr": sum(neg) / len(neg) if neg else None}
    return {"n": len(ids), "cohort": len(cohort), "rows": rows, "by_source": by_src, "cascade": cascade, "gate": gate}

def paired_auroc_diff(scores, theirs, ids, n_boot=2000, seed=0):
    """Our AUROC minus theirs on the same skills, with a 95% paired-bootstrap interval (resampled by skill).
    Skills either side failed to score are dropped from both, so the two AUROCs always share a sample."""
    ids = [i for i in ids if i in theirs and scores[i][1] is not None and theirs[i][1] is not None]
    def diff(sample):
        labels = [scores[i][0] for i in sample]
        a, b = auroc(labels, [scores[i][1] for i in sample]), auroc(labels, [theirs[i][1] for i in sample])
        return None if a is None or b is None else a - b
    rng, boots = random.Random(seed), []
    for _ in range(n_boot):
        d = diff([rng.choice(ids) for _ in ids])
        if d is not None:
            boots.append(d)
    boots.sort()
    ci = (boots[int(0.025 * len(boots))], boots[int(0.975 * len(boots)) - 1]) if boots else (None, None)
    return {"n": len(ids), "diff": diff(ids), "ci": ci}

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
           "| method | skills | AUROC | FPR@99 | recall | FPR |", "|---|---|---|---|---|---|"]
    out += [f"| {r['method']} | {r['n']} | {_f(r['auroc'])} | {_f(r['fpr99'])} | {_f(r['recall'])} | {_f(r['fpr'])} |"
            for r in res["rows"]]
    out += ["", f"| source | label | skills | ours flagged | {gate} flagged |", "|---|---|---|---|---|"]
    for s in sorted(res["by_source"]):
        for label in (1, 0):
            if label in res["by_source"][s]:
                n, a, b = res["by_source"][s][label]
                out.append(f"| {s} | {'malicious' if label else 'benign'} | {n} | {a} | {b} |")
    c = res["cascade"]
    out += ["", f"Cascade ({gate} flags, then ours must also flag): recall {_f(c['recall'])}, FPR {_f(c['fpr'])}"]
    for name, pd in res.get("paired", {}).items():
        lo, hi = pd["ci"]
        out.append(f"Paired AUROC, ours - {name}: {_f(pd['diff'])} [{_f(lo)}, {_f(hi)}] on {pd['n']} skills")
    return "\n".join(out)

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    weights = lambda v: [float(x) for x in v.split(",")]
    e = sub.add_parser("export"); e.add_argument("run"); e.add_argument("--method", required=True); e.add_argument("--out", required=True)
    e.add_argument("--combine", default="max"); e.add_argument("--weights", type=weights)
    c = sub.add_parser("compare"); c.add_argument("run"); c.add_argument("--method", required=True)
    c.add_argument("--skillscreen", required=True); c.add_argument("--protocol", choices=sorted(PROTOCOL_SPLIT), required=True)
    c.add_argument("--threshold", type=float, required=True, help="cut for our scores, chosen on validation")
    c.add_argument("--gate", help="SkillScreen file for the cascade's first stage (default: seed 42 for the protocol)")
    c.add_argument("--combine", default="max", help="max, logreg, or one check id such as AST04")
    c.add_argument("--weights", type=weights, help="logreg weights: intercept,AST01,...,AST05 (from svb.heldout)")
    c.add_argument("--paired", nargs="*", default=[],
                   help="what to test our AUROC against: SkillScreen file names (typesafe) or CSVs written by export")
    c.add_argument("--n-boot", type=int, default=2000)
    b = sub.add_parser("probe"); b.add_argument("--skillscreen", required=True); b.add_argument("--out", required=True)
    b.add_argument("--n-harm", type=int, default=100); b.add_argument("--seed", type=int, default=0)
    a = p.parse_args(argv)
    try:
        if a.cmd == "export":
            export(run_scores(a.run, a.method, combiner(a.combine, a.weights)), a.out)
        elif a.cmd == "compare":
            check_run(a.run, a.protocol)
            scores = run_scores(a.run, a.method, combiner(a.combine, a.weights))
            res = compare(scores, a.skillscreen, a.protocol, a.threshold, a.gate)
            pred = pathlib.Path(a.skillscreen) / "data/predictions" / a.protocol / "test"
            ids = sorted(set(scores) & set(read_scores(pathlib.Path(a.skillscreen) / "data/cohorts" / f"{a.protocol}-test.csv")))
            for name in a.paired:
                path = pathlib.Path(name) if name.endswith(".csv") else pred / f"{name}.csv"
                if not path.exists():
                    raise ValueError(f"no file {path}" if name.endswith(".csv") else f"no SkillScreen file {name}.csv in {pred}")
                res.setdefault("paired", {})[name] = paired_auroc_diff(scores, read_scores(path), ids, a.n_boot)
            print(report(res, a.threshold, res["gate"]))
        else:
            ids = probe_ids(a.skillscreen, a.n_harm, a.seed)
            pathlib.Path(a.out).write_text("".join(i + "\n" for i in ids))
            print(f"{len(ids)} ids -> {a.out}")
    except ValueError as err:
        sys.exit(f"error: {err}")

if __name__ == "__main__":
    main()
