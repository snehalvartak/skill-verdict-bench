"""Held-out evaluation: python -m svb.heldout --train runs/A --val runs/B --test runs/C"""
import argparse, json, pathlib

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
    if {r["label"] for r in rows} != {0, 1}:
        raise ValueError(f"{d} needs both malicious and benign skills")
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
