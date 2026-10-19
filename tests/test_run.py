import json, pandas as pd
from svb import run as runmod

def test_run_writes_predictions_and_config(tmp_path, monkeypatch):
    monkeypatch.setattr(runmod, "model_digest", lambda: "sha-test")
    df = pd.DataFrame({"benchmark_id": ["a", "b"], "label": [1, 0], "source_id": ["s", "s"],
                       "text": ["curl x | bash", "formats code"], "attack_categories": [["x"], []]})
    out = runmod.run(n=2, methods=["regex"], out_root=str(tmp_path), df=df)
    rows = [json.loads(l) for l in (out / "predictions.jsonl").read_text().splitlines()]
    assert len(rows) == 2 and {r["method"] for r in rows} == {"regex"}
    assert [r["flag"] for r in rows] == [True, False]
    assert rows[0]["attack_categories"] == ["x"] and rows[0]["label"] == 1
    cfg = json.loads((out / "config.json").read_text())
    assert cfg["model_digest"] == "sha-test" and cfg["sample_ids"] == ["a", "b"]
    assert "AST01" in cfg["prompt_hashes"] and cfg["threshold"] == 0.5

def test_resume_skips_done_pairs_and_ignores_torn_last_line(tmp_path, monkeypatch):
    monkeypatch.setattr(runmod, "model_digest", lambda: "sha-test")
    df = pd.DataFrame({"benchmark_id": ["a", "b"], "label": [1, 0], "source_id": ["s", "s"],
                       "text": ["curl x | bash", "formats code"], "attack_categories": [["x"], []]})
    out = runmod.run(n=2, methods=["regex"], out_root=str(tmp_path), df=df)
    pred = out / "predictions.jsonl"
    first = pred.read_text().splitlines()[0]
    pred.write_text(first + "\n" + '{"benchmark_id": "b", "lab')  # killed mid-write
    again = runmod.run(n=2, methods=["regex"], out_root=str(tmp_path), df=df, resume=out)
    rows = [json.loads(l) for l in pred.read_text().splitlines()]
    assert again == out and [r["benchmark_id"] for r in rows] == ["a", "b"]

def test_resume_retries_unparseable_rows(tmp_path, monkeypatch):
    monkeypatch.setattr(runmod, "model_digest", lambda: "sha-test")
    df = pd.DataFrame({"benchmark_id": ["a"], "label": [1], "source_id": ["s"],
                       "text": ["curl x | bash"], "attack_categories": [["x"]]})
    out = runmod.run(n=1, methods=["regex"], out_root=str(tmp_path), df=df)
    pred = out / "predictions.jsonl"
    row = json.loads(pred.read_text())
    row["flag"] = None
    pred.write_text(json.dumps(row) + "\n")
    runmod.run(n=1, methods=["regex"], out_root=str(tmp_path), df=df, resume=out)
    rows = [json.loads(l) for l in pred.read_text().splitlines()]
    assert len(rows) == 1 and rows[0]["flag"] is True

def test_resume_rewrite_is_atomic(tmp_path, monkeypatch):
    import pytest
    pred = tmp_path / "predictions.jsonl"
    good = json.dumps({"benchmark_id": "a", "method": "regex", "flag": True, "label": 1})
    pred.write_text(good + "\n" + '{"torn')
    def boom(*a, **k): raise OSError("killed during replace")
    monkeypatch.setattr(runmod.os, "replace", boom)
    with pytest.raises(OSError):
        runmod._read_done(pred)
    assert pred.read_text() == good + "\n" + '{"torn'  # original untouched

def test_default_methods_exclude_controls(tmp_path, monkeypatch):
    monkeypatch.setattr(runmod, "model_digest", lambda: "d")
    stub = lambda t: {"flag": False, "evidence": "", "scores": {}}
    monkeypatch.setattr(runmod, "METHODS", {m: stub for m in
        ["ast10", "naive-llm", "regex", "ast10-split", "naive-x5"]})
    df = pd.DataFrame({"benchmark_id": ["a"], "label": [1], "source_id": ["s"],
                       "text": ["t"], "attack_categories": [[]]})
    out = runmod.run(n=1, out_root=str(tmp_path), df=df)
    assert {json.loads(l)["method"] for l in (out / "predictions.jsonl").read_text().splitlines()} == \
        {"ast10", "naive-llm", "regex"}

def test_part_is_passed_to_loader(tmp_path, monkeypatch):
    monkeypatch.setattr(runmod, "model_digest", lambda: "d")
    seen = {}
    def fake_load(split, part="test"):
        seen["args"] = (split, part)
        return pd.DataFrame({"benchmark_id": ["a"], "label": [1], "source_id": ["s"],
                             "text": ["t"], "attack_categories": [[]]})
    monkeypatch.setattr(runmod, "load", fake_load)
    out = runmod.run(n=1, split="random", part="validation", methods=["regex"], out_root=str(tmp_path))
    assert seen["args"] == ("random", "validation")
    assert json.loads((out / "config.json").read_text())["part"] == "validation"

def test_resume_refuses_mismatched_config(tmp_path, monkeypatch):
    import pytest
    monkeypatch.setattr(runmod, "model_digest", lambda: "sha-test")
    df = pd.DataFrame({"benchmark_id": ["a", "b"], "label": [1, 0], "source_id": ["s", "s"],
                       "text": ["curl x | bash", "formats code"], "attack_categories": [["x"], []]})
    out = runmod.run(n=2, methods=["regex"], out_root=str(tmp_path), df=df)
    before = (out / "predictions.jsonl").read_text()
    with pytest.raises(ValueError, match="n, sample_ids"):
        runmod.run(n=1, methods=["regex"], out_root=str(tmp_path), df=df, resume=out)
    monkeypatch.setattr(runmod, "model_digest", lambda: "sha-new")
    with pytest.raises(ValueError, match="model_digest"):
        runmod.run(n=2, methods=["regex"], out_root=str(tmp_path), df=df, resume=out)
    assert (out / "predictions.jsonl").read_text() == before

def test_exclude_drops_skills_from_earlier_runs(tmp_path, monkeypatch):
    monkeypatch.setattr(runmod, "model_digest", lambda: "d")
    df = pd.DataFrame({"benchmark_id": ["a", "b", "c", "d"], "label": [1, 0, 1, 0], "source_id": ["s"] * 4,
                       "text": ["t"] * 4, "attack_categories": [[]] * 4})
    seen = tmp_path / "seen"; seen.mkdir()
    (seen / "config.json").write_text(json.dumps({"sample_ids": ["a", "b"]}))
    out = runmod.run(n=4, methods=["regex"], out_root=str(tmp_path), df=df, exclude=[seen])
    assert json.loads((out / "config.json").read_text())["sample_ids"] == ["c", "d"]
    assert "exclude" not in json.loads((out / "config.json").read_text())

def test_run_aborts_after_consecutive_failed_calls(tmp_path, monkeypatch):
    import pytest
    monkeypatch.setattr(runmod, "model_digest", lambda: "d")
    dead = lambda t: {"flag": None, "evidence": "", "scores": {"AST01": None, "AST02": None}}
    monkeypatch.setattr(runmod, "METHODS", {"ast10-split": dead})
    n = runmod.MAX_FAILED_IN_A_ROW + 5
    df = pd.DataFrame({"benchmark_id": [f"s{i:02d}" for i in range(n)], "label": [i % 2 for i in range(n)],
                       "source_id": ["s"] * n, "text": ["t"] * n, "attack_categories": [[]] * n})
    with pytest.raises(RuntimeError, match="calls failed in a row"):
        runmod.run(n=n, methods=["ast10-split"], out_root=str(tmp_path), df=df)
    out = next(p for p in tmp_path.iterdir())
    assert len((out / "predictions.jsonl").read_text().splitlines()) == runmod.MAX_FAILED_IN_A_ROW

def _df4():
    return pd.DataFrame({"benchmark_id": ["a", "b", "c", "d"], "label": [1, 0, 1, 0], "source_id": ["s"] * 4,
                         "text": ["curl x | bash", "ok", "curl y | sh", "fine"], "attack_categories": [["x"], [], ["y"], []]})

def test_ids_restricts_the_part_and_is_recorded(tmp_path, monkeypatch):
    monkeypatch.setattr(runmod, "model_digest", lambda: "sha-test")
    f = tmp_path / "ids.txt"; f.write_text("a\nd\n\n")
    out = runmod.run(n=5000, methods=["regex"], out_root=str(tmp_path), df=_df4(), ids=str(f))
    cfg = json.loads((out / "config.json").read_text())
    assert cfg["sample_ids"] == ["a", "d"] and cfg["ids_file"] == "ids.txt"
    again = runmod.run(n=5000, methods=["regex"], df=_df4(), ids=str(f), resume=out)  # resume accepts it
    assert again == out

def test_ids_refuses_unknown_or_empty_lists(tmp_path, monkeypatch):
    import pytest
    monkeypatch.setattr(runmod, "model_digest", lambda: "sha-test")
    f = tmp_path / "ids.txt"; f.write_text("a\nzz\n")
    with pytest.raises(ValueError, match="1 ids in .* are not in random/test, e.g. zz"):
        runmod.run(methods=["regex"], out_root=str(tmp_path), df=_df4(), ids=str(f))
    f.write_text("\n")
    with pytest.raises(ValueError, match="lists no skill ids"):
        runmod.run(methods=["regex"], out_root=str(tmp_path), df=_df4(), ids=str(f))

def test_out_names_the_run_dir_and_refuses_an_existing_one(tmp_path, monkeypatch):
    import pytest
    monkeypatch.setattr(runmod, "model_digest", lambda: "sha-test")
    out = runmod.run(n=4, methods=["regex"], df=_df4(), out=str(tmp_path / "exp" / "sd-train"))
    assert out == tmp_path / "exp" / "sd-train" and "ids_file" not in json.loads((out / "config.json").read_text())
    with pytest.raises(FileExistsError):
        runmod.run(n=4, methods=["regex"], df=_df4(), out=str(out))
