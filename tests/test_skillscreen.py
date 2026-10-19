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
    assert [(r["method"], r["n"]) for r in res["rows"]] == [("ours", 4), ("direct-s42", 4), ("typesafe", 4)]
    assert res["rows"][0]["recall"] == 0.5 and res["rows"][0]["fpr"] == 0.5
    assert res["by_source"]["SkillFortifyBench"][0] == [2, 1, 2]
    assert res["by_source"]["SkillHarm"][1] == [2, 1, 2]
    assert res["cascade"] == {"recall": 0.5, "fpr": 0.5}

def test_compare_refuses_label_mismatch_and_no_overlap(root):
    with pytest.raises(ValueError, match="labels differ"):
        ss.compare({"h1": (0, 0.3)}, root, "sd", t=0.1)
    with pytest.raises(ValueError, match="shares no skills"):
        ss.compare({"zz": (1, 0.3)}, root, "sd", t=0.1)

def test_probe_ids_takes_skillharm_malicious_and_fortify_benign(root):
    ids = ss.probe_ids(root, n_harm=2, seed=0)
    assert len(ids) == 4 and {"f1", "f2"} <= set(ids)
    assert all(i.startswith(("h", "f")) for i in ids)
    assert ss.probe_ids(root, n_harm=2, seed=0) == ids

def test_compare_reports_partial_prediction_file_instead_of_crashing(root):
    p = root / "data/predictions/sd/test/typesafe.csv"
    p.write_text("\n".join(p.read_text().splitlines()[:-2]) + "\n")  # drop f1, f2
    res = ss.compare({"h1": (1, 0.3), "f1": (0, 0.02)}, root, "sd", t=0.1)
    ts = next(r for r in res["rows"] if r["method"] == "typesafe")
    assert ts["n"] == 1 and ts["auroc"] is None and ts["fpr"] is None

def test_compare_refuses_gate_missing_a_skill(root):
    p = root / "data/predictions/sd/test/direct-s42.csv"
    p.write_text("\n".join(p.read_text().splitlines()[:-1]) + "\n")  # drop f2
    with pytest.raises(ValueError, match="gate direct-s42 has no prediction for 1"):
        ss.compare({"h1": (1, 0.3), "f2": (0, 0.4)}, root, "sd", t=0.1)

def _cfg(d, **kw):
    d.mkdir(exist_ok=True); (d / "config.json").write_text(json.dumps(kw)); return d

def test_check_run_refuses_wrong_split_or_part(tmp_path):
    ss.check_run(_cfg(tmp_path / "a", split="source_disjoint", part="test"), "sd")
    ss.check_run(_cfg(tmp_path / "b", split="m_structural_disjoint"), "msd")  # pre --part runs are test
    with pytest.raises(ValueError, match="split=random part=test; --protocol sd needs split=source_disjoint"):
        ss.check_run(_cfg(tmp_path / "c", split="random", part="test"), "sd")
    with pytest.raises(ValueError, match="part=validation"):
        ss.check_run(_cfg(tmp_path / "d", split="source_disjoint", part="validation"), "sd")

def test_report_lists_rows_sources_and_cascade(root):
    res = ss.compare({"h1": (1, 0.3), "h2": (1, 0.05), "f1": (0, 0.02), "f2": (0, 0.4)}, root, "sd", t=0.1)
    out = ss.report(res, 0.1, "direct-s42")
    assert out.startswith("Skills compared: 4 of SkillScreen's 5. Ours cut at 0.1, theirs at 0.5.")
    assert "| ours | 4 | 0.500 | 0.500 | 0.500 | 0.500 |" in out
    assert "| SkillFortifyBench | benign | 2 | 1 | 2 |" in out
    assert out.endswith("recall 0.500, FPR 0.500")

def test_cli_compare_checks_split_and_requires_threshold(tmp_path, root, capsys):
    d = _run(tmp_path, [R("h1", 1, {"AST01": 0.3}), R("f1", 0, {"AST01": 0.02})])
    _cfg(d, split="source_disjoint", part="test")
    ss.main(["compare", str(d), "--method", "ast10", "--skillscreen", str(root), "--protocol", "sd", "--threshold", "0.1"])
    assert "| ours | 2 |" in capsys.readouterr().out
    with pytest.raises(SystemExit, match="--protocol msd needs split=m_structural_disjoint"):
        ss.main(["compare", str(d), "--method", "ast10", "--skillscreen", str(root), "--protocol", "msd", "--threshold", "0.1"])
    with pytest.raises(SystemExit):
        ss.main(["compare", str(d), "--method", "ast10", "--skillscreen", str(root), "--protocol", "sd"])
    assert "--threshold" in capsys.readouterr().err

def test_cli_export_and_probe_write_files(tmp_path, root, capsys):
    d = _run(tmp_path, [R("h1", 1, {"AST01": 0.3})])
    ss.main(["export", str(d), "--method", "ast10", "--out", str(tmp_path / "x.csv")])
    assert (tmp_path / "x.csv").read_text() == "benchmark_id,label,score\nh1,1,0.3\n"
    ss.main(["probe", "--skillscreen", str(root), "--out", str(tmp_path / "ids.txt"), "--n-harm", "1"])
    assert len((tmp_path / "ids.txt").read_text().split()) == 3 and "3 ids" in capsys.readouterr().out

def test_combiner_max_single_check_and_logreg():
    r = {"scores": {"AST01": 0.1, "AST02": 0.0, "AST03": 0.2, "AST04": 0.6, "AST05": 0.0}}
    assert ss.combiner("max")(r) == 0.6 and ss.combiner("AST04")(r) == 0.6
    assert ss.combiner("logreg", [0, 0, 0, 0, 0, 0])(r) == 0.5
    assert ss.combiner("logreg", [0, 0, 0, 0, 0, 0])({"scores": {**r["scores"], "AST02": None}}) is None
    with pytest.raises(ValueError, match="needs 6 weights"):
        ss.combiner("logreg", [1.0])
    with pytest.raises(ValueError, match="unknown combiner"):
        ss.combiner("mean")

def test_paired_auroc_diff_same_and_opposite_rankings():
    ours = {"a": (1, 0.9), "b": (1, 0.8), "c": (0, 0.1), "d": (0, 0.2), "e": (1, None)}
    same = ss.paired_auroc_diff(ours, {k: v for k, v in ours.items()}, list(ours), n_boot=200)
    assert same["n"] == 4 and same["diff"] == 0 and same["ci"] == (0, 0)
    flipped = {k: (l, None if s is None else 1 - s) for k, (l, s) in ours.items()}
    opp = ss.paired_auroc_diff(ours, flipped, list(ours), n_boot=200)
    assert opp["diff"] == 1.0 and opp["ci"] == (1.0, 1.0)

def test_cli_compare_with_combiner_and_paired_test(tmp_path, root, capsys):
    d = _run(tmp_path, [R("h1", 1, {"AST01": 0.0, "AST04": 0.3}), R("f1", 0, {"AST01": 0.9, "AST04": 0.02})])
    _cfg(d, split="source_disjoint", part="test")
    ss.main(["compare", str(d), "--method", "ast10", "--combine", "AST04", "--skillscreen", str(root),
             "--protocol", "sd", "--threshold", "0.1", "--paired", "direct-s42", "--n-boot", "50"])
    out = capsys.readouterr().out
    assert "| ours | 2 | 1.000 |" in out and "Paired AUROC, ours - direct-s42: 0.000 [0.000, 0.000] on 2 skills" in out
    with pytest.raises(SystemExit, match="no SkillScreen file nope.csv"):
        ss.main(["compare", str(d), "--method", "ast10", "--skillscreen", str(root), "--protocol", "sd",
                 "--threshold", "0.1", "--paired", "nope"])

def test_cli_export_with_combiner_feeds_paired_test(tmp_path, root, capsys):
    d = _run(tmp_path, [R("h1", 1, {"AST01": 0.0, "AST04": 0.3}), R("f1", 0, {"AST01": 0.9, "AST04": 0.02}),
                        R("h1", 1, {"malicious": 0.1}, "naive-llm"), R("f1", 0, {"malicious": 0.2}, "naive-llm")])
    _cfg(d, split="source_disjoint", part="test")
    naive = tmp_path / "naive.csv"
    ss.main(["export", str(d), "--method", "naive-llm", "--out", str(naive)])
    ss.main(["export", str(d), "--method", "ast10", "--combine", "AST04", "--out", str(tmp_path / "a4.csv")])
    assert (tmp_path / "a4.csv").read_text() == "benchmark_id,label,score\nf1,0,0.02\nh1,1,0.3\n"
    ss.main(["compare", str(d), "--method", "ast10", "--combine", "AST04", "--skillscreen", str(root),
             "--protocol", "sd", "--threshold", "0.1", "--paired", str(naive), "--n-boot", "50"])
    assert f"Paired AUROC, ours - {naive}: 1.000 [1.000, 1.000] on 2 skills" in capsys.readouterr().out
