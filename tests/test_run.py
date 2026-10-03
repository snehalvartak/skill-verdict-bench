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
