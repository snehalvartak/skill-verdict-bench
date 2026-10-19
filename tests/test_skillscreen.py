import json, pytest
from svb import skillscreen as ss

def _csv(path, rows, header="benchmark_id,label,score"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(header + "\n" + "".join(",".join(map(str, r)) + "\n" for r in rows))

@pytest.fixture
def root(tmp_path):
    """A fake SkillScreen clone: 2 sources, a gate model and one judge on the sd test cohort."""
    r = tmp_path / "SkillScreen"
    meta = [("h1", "SRC1", "SkillHarm"), ("h2", "SRC1", "SkillHarm"), ("h3", "SRC1", "SkillHarm"),
            ("f1", "SRC2", "SkillFortifyBench"), ("f2", "SRC2", "SkillFortifyBench")]
    _csv(r / "data/metadata/benchmark_metadata.csv", meta, "benchmark_id,source_id,source_name")
    _csv(r / "data/cohorts/sd-test.csv", [("h1", 1), ("h2", 1), ("h3", 1), ("f1", 0), ("f2", 0)], "benchmark_id,label")
    pred = r / "data/predictions/sd/test"
    _csv(pred / "direct-s42.csv", [("h1", 1, 0.9), ("h2", 1, 0.8), ("h3", 1, 0.2), ("f1", 0, 0.7), ("f2", 0, 0.6)])
    _csv(pred / "typesafe.csv", [("h1", 1, 0.1), ("h2", 1, ""), ("h3", 1, 0.1), ("f1", 0, 0.0), ("f2", 0, 0.0)])
    return r

def _run(tmp_path, rows):
    d = tmp_path / "run"; d.mkdir()
    (d / "predictions.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    return d

def R(i, label, scores, method="ast10", flag=True):
    return {"benchmark_id": i, "label": label, "method": method, "flag": flag, "scores": scores}

def test_auroc_ties_and_missing():
    assert ss.auroc([1, 0], [0.5, 0.5]) == 0.5
    assert ss.auroc([1, 1, 0, 0], [0.9, None, 0.1, 0.2]) == 1.0
    assert ss.auroc([1, 1], [0.9, 0.2]) is None

def test_fpr_at_recall_cuts_at_kth_malicious_score():
    r = ss.fpr_at_recall([1, 1, 1, 0, 0], [0.9, 0.8, 0.7, 0.75, 0.1])
    assert r == {"fpr": 0.5, "recall": 1.0, "threshold": 0.7}

def test_fpr_at_recall_counts_missing_as_infinite():
    r = ss.fpr_at_recall([1, 1, 0], [None, 0.8, 0.9])
    assert r["threshold"] == 0.8 and r["fpr"] == 1.0

def test_at_threshold_flags_missing():
    assert ss.at_threshold([1, 1, 0], [None, 0.1, 0.1], 0.5) == {"recall": 0.5, "fpr": 0.0}

def test_run_scores_max_for_llm_and_flag_for_regex(tmp_path):
    d = _run(tmp_path, [R("a", 1, {"AST01": 0.1, "AST04": 0.4}), R("a", 1, {}, "regex", False),
                        R("b", 0, {"AST01": None}, flag=None)])
    assert ss.run_scores(d, "ast10") == {"a": (1, 0.4), "b": (0, None)}
    assert ss.run_scores(d, "regex") == {"a": (1, 0.0)}
    with pytest.raises(ValueError, match="no naive-llm rows"):
        ss.run_scores(d, "naive-llm")

def test_export_round_trips(tmp_path):
    out = tmp_path / "x.csv"
    ss.export({"b": (0, None), "a": (1, 0.25)}, out)
    assert out.read_text() == "benchmark_id,label,score\na,1,0.25\nb,0,\n"
    assert ss.read_scores(out) == {"a": (1, 0.25), "b": (0, None)}

def test_compare_rows_sources_and_cascade(root):
    ours = {"h1": (1, 0.3), "h2": (1, 0.05), "f1": (0, 0.02), "f2": (0, 0.4)}
    res = ss.compare(ours, root, "sd", t=0.1)
    assert res["n"] == 4 and res["cohort"] == 5
    assert [r["method"] for r in res["rows"]] == ["ours", "direct-s42", "typesafe"]
    assert res["rows"][0]["recall"] == 0.5 and res["rows"][0]["fpr"] == 0.5
    assert res["by_source"]["SkillFortifyBench"][0] == [2, 1, 2]
    assert res["by_source"]["SkillHarm"][1] == [2, 1, 2]
    assert res["cascade"] == {"recall": 0.5, "fpr": 0.5}

def test_compare_refuses_label_mismatch_and_no_overlap(root):
    with pytest.raises(ValueError, match="labels differ"):
        ss.compare({"h1": (0, 0.3)}, root, "sd")
    with pytest.raises(ValueError, match="shares no skills"):
        ss.compare({"zz": (1, 0.3)}, root, "sd")

def test_probe_ids_takes_skillharm_malicious_and_fortify_benign(root):
    ids = ss.probe_ids(root, n_harm=2, seed=0)
    assert len(ids) == 4 and {"f1", "f2"} <= set(ids)
    assert all(i.startswith(("h", "f")) for i in ids)
    assert ss.probe_ids(root, n_harm=2, seed=0) == ids
