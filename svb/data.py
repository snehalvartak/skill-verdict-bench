import hashlib, pathlib, sys, urllib.request
import pandas as pd

# Pinned to the revision SkillScreen (arXiv 2610.17727) evaluates on, so results are comparable
REVISION = "d4b42ce5766a6e0359c987cf59c1007cb3795a90"
BASE = f"https://huggingface.co/datasets/ProtectSkills/MaliciousSkillBench/resolve/{REVISION}/"
DATA = pathlib.Path("data")
# sha256 at REVISION, from SkillScreen's configs/data.json; the random split was not published there
PINNED = {
    "primary.parquet": "1d6382017f259bde0b699d402318f3c03f16b2e8ed2363a346b77a5465f06a06",
    "splits/m_structural_disjoint.parquet": "f6456f678910170bc2203998d1823842112bba5d5036859f58ea409c292a34d8",
    "splits/source_disjoint.parquet": "9fae37c53b6ad47070d118e9bc4cdafd82c416a68b7e74847b4e0dd9d66bd276",
}

def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def _fetch(name):
    dest = DATA / name.replace("/", "_")
    if not dest.exists():
        DATA.mkdir(exist_ok=True)
        tmp = dest.with_name(dest.name + ".part")
        try:
            urllib.request.urlretrieve(BASE + name, tmp)
            if name in PINNED and _sha256(tmp) != PINNED[name]:
                raise ValueError(f"{name}: sha256 differs from revision {REVISION[:7]}")
            tmp.rename(dest)
        finally:
            tmp.unlink(missing_ok=True)
    # ponytail: files cached before pinning are not re-checked here, so runs in progress keep working; see verify()
    return dest

def verify():
    """Compare cached files with the pinned hashes: {name: "match" | "differs" | "not pinned" | "not cached"}."""
    out = {}
    for f in sorted(set(PINNED) | {p.name.replace("splits_", "splits/", 1) for p in DATA.glob("*.parquet")}):
        path = DATA / f.replace("/", "_")
        out[f] = ("not cached" if not path.exists() else "not pinned" if f not in PINNED
                  else "match" if _sha256(path) == PINNED[f] else "differs")
    return out

def load(split="random", part="test"):
    primary = pd.read_parquet(_fetch("primary.parquet"))
    splits = pd.read_parquet(_fetch(f"splits/{split}.parquet"))
    keep = splits[splits.split == part][["benchmark_id"]]
    df = primary.merge(keep, on="benchmark_id")
    df = df[df.text_available]
    df = df.assign(text=df.skill_text)
    return df[["benchmark_id", "label", "source_id", "text", "attack_categories"]].reset_index(drop=True)

def sample(df, n, seed=0):
    frac = min(1.0, n / len(df))
    parts = [g.sample(n=min(len(g), round(len(g) * frac)), random_state=seed)
             for _, g in df.groupby("label")]
    return pd.concat(parts).sort_values("benchmark_id").reset_index(drop=True)

if __name__ == "__main__":
    if sys.argv[1:] != ["verify"]:
        sys.exit("usage: python -m svb.data verify")
    for name, state in verify().items():
        print(f"{state:>10}  {name}")
