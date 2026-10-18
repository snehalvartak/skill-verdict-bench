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

def signal_in_ast04(prefix, n=20):
    # benign skills trip AST01 hard, so max() can't separate them; AST04 alone can
    return [row(f"{prefix}{i}", i % 2, AST01=0.9, AST04=0.8 if i % 2 else 0.1) for i in range(n)]

def test_as_rows_unscored_rows_are_skipped_by_auc():
    from svb.score import auc
    rs = heldout.as_rows([row("a", 1), row("b", 0, AST04=0.9), row("c", 1)],
                         lambda r: None if r["benchmark_id"] == "c" else r["scores"]["AST04"])
    assert rs[2]["scores"] == {} and auc(rs) == 0.0

def test_rates():
    rs = heldout.as_rows([row("a", 1, AST04=0.6), row("b", 1, AST04=0.2), row("c", 0, AST04=0.7)],
                         lambda r: r["scores"]["AST04"])
    assert heldout.rates(rs, 0.5) == (0.5, 1.0)

def test_evaluate_learned_combination_beats_max():
    res, w = heldout.evaluate(signal_in_ast04("t"), signal_in_ast04("v"), signal_in_ast04("x"), n_boot=50)
    assert res["max"]["auc"] == 0.5
    assert res["AST04"]["auc"] == 1.0 and res["logreg"]["auc"] == 1.0
    assert res["logreg"]["tpr"] == 1.0 and res["logreg"]["fpr"] == 0.0
    assert 0.1 < res["AST04"]["threshold"] <= 0.8
    assert len(w) == 1 + len(heldout.CHECK_IDS) and w[1 + heldout.CHECK_IDS.index("AST04")] > 0

def test_rows_with_missing_scores_are_skipped_and_counted():
    train = signal_in_ast04("t") + [row("tn", 1, AST02=None)]
    test = signal_in_ast04("x") + [row("xn", 0, AST04=None)]
    res, _ = heldout.evaluate(train, signal_in_ast04("v"), test, n_boot=50)
    assert res["logreg"]["unscored"] == 1 and res["AST04"]["unscored"] == 1
    assert res["max"]["unscored"] == 0  # max uses whatever scores are present
    assert res["logreg"]["auc"] == 1.0

def test_main_prints_tables(tmp_path, capsys):
    tr = make_run(tmp_path / "tr", "train", signal_in_ast04("t"))
    va = make_run(tmp_path / "va", "validation", signal_in_ast04("v"))
    te = make_run(tmp_path / "te", "test", signal_in_ast04("x"))
    heldout.main(["--train", str(tr), "--val", str(va), "--test", str(te), "--n-boot", "50"])
    out = capsys.readouterr().out
    assert "| logreg | " in out and "| logreg - max | " in out and "| AST04 | " in out
    assert "test skills: 20 (10 malicious, 10 benign)" in out
