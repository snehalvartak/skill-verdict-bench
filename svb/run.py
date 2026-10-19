import argparse, json, os, pathlib, time
from svb.checks import MAX_CHARS, THRESHOLD, prompt_hashes
from svb.data import load, sample
from svb.methods import METHODS
from svb.score import current_name
from svb.systemone import model_digest

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
        done.add((r["benchmark_id"], current_name(r["method"])))
    tmp = pred.with_name(pred.name + ".tmp")
    tmp.write_text("".join(l + "\n" for l in good))
    os.replace(tmp, pred)  # atomic: a kill mid-rewrite never loses the original
    return done

MAX_FAILED_IN_A_ROW = 10  # ponytail: a dead model fails every call; a few flaky ones never reach 10 in a row
DEFAULT_METHODS = ["ast10", "generic-1q", "regex"]  # controls (ast10-split, generic-5q) are opt-in via --methods

def _check_resume(saved, cfg):
    """Refuse to append to a run made with a different sample, prompts, model or settings."""
    # ponytail: methods may differ; a resume can add or skip methods without mixing runs
    bad = [k for k in cfg if k != "methods" and saved.get(k) != cfg[k]]
    if bad:
        raise ValueError(f"resume config differs from the saved run in: {', '.join(bad)}")

def _read_ids(path):
    ids = [l.strip() for l in pathlib.Path(path).read_text().splitlines() if l.strip()]
    if not ids:
        raise ValueError(f"{path} lists no skill ids")
    return ids

def run(n=200, split="random", part="test", seed=0, methods=None, out_root="runs", df=None, resume=None, exclude=(),
        ids=None, out=None):
    """`ids`: file of benchmark ids to restrict the part to (every id must be in it). `out`: run dir to create."""
    methods = methods or DEFAULT_METHODS
    df = load(split, part) if df is None else df
    if ids:
        want = _read_ids(ids)
        missing = sorted(set(want) - set(df.benchmark_id))
        if missing:
            raise ValueError(f"{len(missing)} ids in {ids} are not in {split}/{part}, e.g. {missing[0]}")
        df = df[df.benchmark_id.isin(want)]
    skip = {i for d in exclude for i in json.loads((pathlib.Path(d) / "config.json").read_text())["sample_ids"]}
    df = sample(df[~df.benchmark_id.isin(skip)], n, seed)
    cfg = {"model": "clef-flash", "model_digest": model_digest(), "prompt_hashes": prompt_hashes(),
           "threshold": THRESHOLD, "seed": seed, "split": split, "part": part, "n": n, "max_chars": MAX_CHARS,
           "methods": methods, "sample_ids": list(df.benchmark_id)}
    if ids:
        cfg["ids_file"] = pathlib.Path(ids).name  # only when used, so older configs still pass the resume check
    if resume:
        out = pathlib.Path(resume)
        _check_resume(json.loads((out / "config.json").read_text()), cfg)
        done = _read_done(out / "predictions.jsonl")
    else:
        out = pathlib.Path(out) if out else pathlib.Path(out_root) / time.strftime("%Y%m%d-%H%M%S")
        out.mkdir(parents=True)  # an existing dir is refused: resume it instead
        (out / "config.json").write_text(json.dumps(cfg, indent=2))
        done = set()
    failed = 0
    with open(out / "predictions.jsonl", "a") as f:
        for _, r in df.iterrows():
            for m in methods:
                if (r.benchmark_id, m) in done:
                    continue
                v = METHODS[m](r.text)
                failed = failed + 1 if v["scores"] and all(x is None for x in v["scores"].values()) else 0
                f.write(json.dumps({"benchmark_id": r.benchmark_id, "label": int(r.label), "method": m,
                                    **v, "attack_categories": [str(c) for c in r.attack_categories]}) + "\n")
                f.flush()
                if failed >= MAX_FAILED_IN_A_ROW:
                    raise RuntimeError(f"{failed} model calls failed in a row; fix the model, then --resume {out}")
    return out

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=200)
    p.add_argument("--split", default="random")
    p.add_argument("--part", default="test", choices=["train", "validation", "test"])
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--methods", nargs="*")
    p.add_argument("--resume", help="run dir to continue (same --n/--seed/--split)")
    p.add_argument("--exclude", nargs="*", default=[], help="run dirs whose skills are left out of the sample")
    p.add_argument("--ids", help="file of benchmark ids, one per line; the part is restricted to them")
    p.add_argument("--out", help="run dir to create (default runs/<timestamp>); continue it later with --resume")
    a = p.parse_args()
    print(run(a.n, a.split, a.part, a.seed, a.methods, resume=a.resume, exclude=a.exclude, ids=a.ids, out=a.out))
