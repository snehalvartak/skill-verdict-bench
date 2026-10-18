import json, pytest
from svb import heldout

H = {c: "h" + c for c in heldout.CHECK_IDS}

def make_run(path, part, rows, digest="d", hashes=H, ids=None):
    path.mkdir()
    cfg = {"model_digest": digest, "split": "random", "prompt_hashes": hashes,
           "sample_ids": ids or sorted({r["benchmark_id"] for r in rows})}
    if part is not None:
        cfg["part"] = part
    (path / "config.json").write_text(json.dumps(cfg))
    (path / "predictions.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    return path

def row(i, label, method="ast10-split", **scores):
    s = {c: 0.1 for c in heldout.CHECK_IDS} | scores
    return {"benchmark_id": i, "label": label, "method": method, "flag": False, "scores": s, "attack_categories": []}

TWO = [row("a", 1), row("b", 0)]

def test_load_run_returns_rows_of_the_method(tmp_path):
    d = make_run(tmp_path / "r", "validation", TWO + [row("a", 1, method="ast10")])
    cfg, rows = heldout.load_run(d, "validation")
    assert len(rows) == 2 and cfg["part"] == "validation"

def test_load_run_refuses_wrong_part(tmp_path):
    d = make_run(tmp_path / "r", "test", TWO)
    with pytest.raises(ValueError, match="is a test run, expected validation"):
        heldout.load_run(d, "validation")

def test_load_run_treats_missing_part_as_test(tmp_path):
    d = make_run(tmp_path / "r", None, TWO)
    heldout.load_run(d, "test")

def test_load_run_needs_the_method(tmp_path):
    d = make_run(tmp_path / "r", "train", [row("a", 1, method="ast10"), row("b", 0, method="ast10")])
    with pytest.raises(ValueError, match="no ast10-split predictions"):
        heldout.load_run(d, "train")

def test_load_run_needs_both_classes(tmp_path):
    d = make_run(tmp_path / "r", "train", [row("a", 1), row("b", 1)])
    with pytest.raises(ValueError, match="both malicious and benign"):
        heldout.load_run(d, "train")

def cfg(ids, digest="d", hashes=H):
    return {"model_digest": digest, "split": "random", "prompt_hashes": hashes, "sample_ids": ids}

def test_check_compatible_accepts_disjoint_matching_runs():
    heldout.check_compatible([cfg(["a"]), cfg(["b"]), cfg(["c"])])

def test_check_compatible_refuses_digest_and_prompt_mismatch():
    with pytest.raises(ValueError, match="model_digest"):
        heldout.check_compatible([cfg(["a"]), cfg(["b"], digest="x"), cfg(["c"])])
    with pytest.raises(ValueError, match="AST check prompts"):
        heldout.check_compatible([cfg(["a"]), cfg(["b"]), cfg(["c"], hashes=H | {"AST04": "changed"})])

def test_check_compatible_ignores_non_ast_prompt_hashes():
    heldout.check_compatible([cfg(["a"]), cfg(["b"], hashes=H | {"n1": "x"}), cfg(["c"])])

def test_check_compatible_refuses_overlap():
    with pytest.raises(ValueError, match="share skills"):
        heldout.check_compatible([cfg(["a", "b"]), cfg(["c"]), cfg(["b"])])
