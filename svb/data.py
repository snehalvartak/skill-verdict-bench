import pathlib, urllib.request
import pandas as pd

BASE = "https://huggingface.co/datasets/ProtectSkills/MaliciousSkillBench/resolve/main/"
DATA = pathlib.Path("data")

def _fetch(name):
    dest = DATA / name.replace("/", "_")
    if not dest.exists():
        DATA.mkdir(exist_ok=True)
        tmp = dest.with_name(dest.name + ".part")
        try:
            urllib.request.urlretrieve(BASE + name, tmp)
            tmp.rename(dest)
        finally:
            tmp.unlink(missing_ok=True)
    return dest

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
