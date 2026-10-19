import json
from svb import compare

def _run(tmp_path, rows):
    d = tmp_path / "run"; d.mkdir()
    (d / "predictions.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    return d

def R(label, score, method="ast10"):
    return {"benchmark_id": f"{method}{label}{score}", "label": label, "method": method,
            "flag": score >= 0.5, "scores": {"AST01": score}}

def test_run_without_benign_skills_prints_na_instead_of_crashing(tmp_path, capsys):
    d = _run(tmp_path, [R(1, 0.9), R(1, 0.2), R(1, 0.4, "naive-llm"), R(0, 0.1, "naive-llm")])
    compare.main([str(d)])
    out = capsys.readouterr().out
    assert "| ast10 | n/a" in out and "| naive-llm | 1.000 |" in out
    assert "ast10 - naive-llm" not in out
