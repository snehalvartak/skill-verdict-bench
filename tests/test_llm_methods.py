from msd import methods, checks

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
    assert methods.naive_llm("skill")["flag"] is True

def test_naive_maps_single_question(monkeypatch):
    monkeypatch.setattr(methods, "ask", lambda s, q: {"malicious": 0.8})
    v = methods.naive_llm("skill")
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
    assert methods.naive_llm("")["flag"] is None

def test_all_five_checks_defined():
    assert list(checks.CHECKS) == ["AST01", "AST02", "AST03", "AST04", "AST05"]
