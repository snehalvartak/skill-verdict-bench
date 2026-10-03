import argparse, json, os, pathlib, time
from msd.checks import MAX_CHARS, THRESHOLD, prompt_hashes
from msd.data import load, sample
from msd.methods import METHODS
from msd.systemone import model_digest

def _read_done(pred):
    """Return {(benchmark_id, method)} already scored; drop torn and unparseable lines."""
    done, good = set(), []
    for line in pred.read_text().splitlines():
        try:
            r = json.loads(line)
        except ValueError:
            break  # ponytail: only the last line can be torn by a kill; stop at the first bad one
        if r["flag"] is None:
            continue  # unparseable rows are retried, not kept
        good.append(line)
        done.add((r["benchmark_id"], r["method"]))
    tmp = pred.with_name(pred.name + ".tmp")
    tmp.write_text("".join(l + "\n" for l in good))
    os.replace(tmp, pred)  # atomic: a kill mid-rewrite never loses the original
    return done

def run(n=200, split="random", seed=0, methods=None, out_root="runs", df=None, resume=None):
    methods = methods or list(METHODS)
    df = sample(load(split) if df is None else df, n, seed)
    if resume:
        out = pathlib.Path(resume)
        done = _read_done(out / "predictions.jsonl")
    else:
        out = pathlib.Path(out_root) / time.strftime("%Y%m%d-%H%M%S")
        out.mkdir(parents=True)
        done = set()
    cfg = {"model": "clef-flash", "model_digest": model_digest(), "prompt_hashes": prompt_hashes(),
           "threshold": THRESHOLD, "seed": seed, "split": split, "n": n, "max_chars": MAX_CHARS,
           "methods": methods, "sample_ids": list(df.benchmark_id)}
    if not resume:
        (out / "config.json").write_text(json.dumps(cfg, indent=2))
    with open(out / "predictions.jsonl", "a") as f:
        for _, r in df.iterrows():
            for m in methods:
                if (r.benchmark_id, m) in done:
                    continue
                v = METHODS[m](r.text)
                f.write(json.dumps({"benchmark_id": r.benchmark_id, "label": int(r.label), "method": m,
                                    **v, "attack_categories": [str(c) for c in r.attack_categories]}) + "\n")
                f.flush()
    return out

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=200)
    p.add_argument("--split", default="random")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--methods", nargs="*")
    p.add_argument("--resume", help="run dir to continue (same --n/--seed/--split)")
    a = p.parse_args()
    print(run(a.n, a.split, a.seed, a.methods, resume=a.resume))
