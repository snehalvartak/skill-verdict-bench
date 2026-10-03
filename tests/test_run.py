import json, pandas as pd
from msd import run as runmod

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
