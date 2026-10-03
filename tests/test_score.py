from msd.score import metrics, per_check, by_category

def R(label, flag, **kw):
    return {"label": label, "flag": flag, "method": "ast10", "scores": {}, "attack_categories": [], **kw}

def test_metrics_basic():
    m = metrics([R(1, True), R(1, False), R(0, True), R(0, False)])
    assert (m["tp"], m["fn"], m["fp"], m["tn"]) == (1, 1, 1, 1)
    assert m["precision"] == 0.5 and m["recall"] == 0.5 and m["f1"] == 0.5

def test_no_positive_predictions_no_crash():
    m = metrics([R(1, False), R(0, False)])
    assert m["precision"] == 0.0 and m["f1"] == 0.0

def test_unparseable_counted_not_scored():
    m = metrics([R(1, None), R(1, True)])
    assert m["unparseable"] == 1 and m["tp"] == 1 and m["fn"] == 0

def test_per_check_hit_rates_threshold_scores():
    rows = [R(1, True, scores={"AST01": 0.9}), R(1, True, scores={"AST01": 0.2}),
            R(0, False, scores={"AST01": 0.1})]
    pc = per_check(rows)["AST01"]
    assert pc["malicious_hit"] == 0.5 and pc["benign_hit"] == 0.0

def test_per_check_ignores_none_scores():
    rows = [R(1, True, scores={"AST01": None}), R(1, True, scores={"AST01": 0.9})]
    assert per_check(rows)["AST01"]["malicious_hit"] == 1.0

def test_by_category_recall():
    rows = [R(1, True, attack_categories=["Exfil"]), R(1, False, attack_categories=["Exfil"])]
    assert by_category(rows) == {"Exfil": 0.5}
