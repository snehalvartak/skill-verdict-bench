from svb import methods, checks

def test_ast10_flags_if_any_check_over_threshold(monkeypatch):
    monkeypatch.setattr(methods, "ask", lambda s, q: {k: 0.9 if k == "AST03" else 0.1 for k in q})
    v = methods.ast10("skill")
    assert v["flag"] is True and v["scores"]["AST03"] == 0.9 and v["scores"]["AST01"] == 0.1

def test_ast10_all_below_threshold_not_flagged(monkeypatch):
    monkeypatch.setattr(methods, "ask", lambda s, q: {k: 0.2 for k in q})
    assert methods.ast10("skill")["flag"] is False

def test_ast10_all_none_is_unparseable(monkeypatch):
    monkeypatch.setattr(methods, "ask", lambda s, q: {k: None for k in q})
    assert methods.ast10("skill")["flag"] is None

def test_threshold_boundary_counts_as_flag(monkeypatch):
    monkeypatch.setattr(methods, "ask", lambda s, q: {"malicious": checks.THRESHOLD})
    assert methods.generic_1q("skill")["flag"] is True

def test_generic_1q_maps_single_question(monkeypatch):
    monkeypatch.setattr(methods, "ask", lambda s, q: {"malicious": 0.8})
    v = methods.generic_1q("skill")
    assert v["flag"] is True and v["scores"] == {"malicious": 0.8}

def test_truncate_records_truncation():
    t, cut = checks.truncate("a" * (checks.MAX_CHARS + 5))
    assert len(t) == checks.MAX_CHARS and cut is True
    assert checks.truncate("abc") == ("abc", False)

def test_truncated_skill_is_marked_in_evidence(monkeypatch):
    monkeypatch.setattr(methods, "ask", lambda s, q: {k: 0.1 for k in q})
    assert methods.ast10("a" * (checks.MAX_CHARS + 1))["evidence"] == "truncated"

def test_empty_text_does_not_call_model(monkeypatch):
    def boom(*a, **k): raise AssertionError("called")
    monkeypatch.setattr(methods, "ask", boom)
    assert methods.ast10("  ")["flag"] is None
    assert methods.generic_1q("")["flag"] is None

def test_all_five_checks_defined():
    assert list(checks.CHECKS) == ["AST01", "AST02", "AST03", "AST04", "AST05"]

def test_ast10_split_makes_one_call_per_check(monkeypatch):
    calls = []
    def fake(s, q):
        calls.append(list(q)); return {k: 0.9 if k == "AST02" else 0.1 for k in q}
    monkeypatch.setattr(methods, "ask", fake)
    v = methods.ast10_split("skill")
    assert calls == [["AST01"], ["AST02"], ["AST03"], ["AST04"], ["AST05"]]
    assert v["flag"] is True and v["scores"]["AST02"] == 0.9

def test_ast10_split_empty_text_no_calls(monkeypatch):
    monkeypatch.setattr(methods, "ask", lambda *a: (_ for _ in ()).throw(AssertionError("called")))
    assert methods.ast10_split(" ")["flag"] is None

def test_generic_5q_batches_five_paraphrases_in_one_call(monkeypatch):
    seen = []
    monkeypatch.setattr(methods, "ask", lambda s, q: seen.append(list(q)) or {k: 0.6 if k == "n3" else 0.1 for k in q})
    v = methods.generic_5q("skill")
    assert seen == [["n1", "n2", "n3", "n4", "n5"]] and v["flag"] is True

def test_paraphrases_are_distinct_and_hashed():
    qs = [v[0] for v in checks.GENERIC5.values()]
    assert len(set(qs)) == 5
    assert "n1" in checks.prompt_hashes()

def test_new_methods_registered():
    assert {"ast10-split", "generic-5q"} <= set(methods.METHODS)

def test_generic_question_methods_are_named_by_what_they_ask():
    assert {"generic-1q", "generic-5q"} <= set(methods.METHODS)
    assert not {"naive-llm", "naive-x5"} & set(methods.METHODS)
