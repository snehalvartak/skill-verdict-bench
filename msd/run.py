import argparse, json, pathlib, time
from msd.checks import MAX_CHARS, THRESHOLD, prompt_hashes
from msd.data import load, sample
from msd.methods import METHODS
from msd.systemone import model_digest

def run(n=200, split="random", seed=0, methods=None, out_root="runs", df=None):
    methods = methods or list(METHODS)
    df = sample(load(split) if df is None else df, n, seed)
    out = pathlib.Path(out_root) / time.strftime("%Y%m%d-%H%M%S")
    out.mkdir(parents=True)
    cfg = {"model": "clef-flash", "model_digest": model_digest(), "prompt_hashes": prompt_hashes(),
           "threshold": THRESHOLD, "seed": seed, "split": split, "n": n, "max_chars": MAX_CHARS,
           "methods": methods, "sample_ids": list(df.benchmark_id)}
    (out / "config.json").write_text(json.dumps(cfg, indent=2))
    with open(out / "predictions.jsonl", "w") as f:
        for _, r in df.iterrows():
            for m in methods:
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
    a = p.parse_args()
    print(run(a.n, a.split, a.seed, a.methods))
