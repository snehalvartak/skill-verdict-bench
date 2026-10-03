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

from msd.score import auc, auc_by_check, youden_threshold, metrics_at, fit_logreg, predict_logreg

def S(label, **scores):
    return R(label, None, scores=scores)

def test_auc_perfect_and_chance():
    assert auc([S(1, a=0.9), S(0, a=0.1)]) == 1.0
    assert auc([S(1, a=0.5), S(0, a=0.5)]) == 0.5

def test_auc_uses_max_score_and_skips_rows_without_scores():
    rows = [S(1, a=0.1, b=0.9), S(0, a=0.5, b=0.2), S(1)]
    assert auc(rows) == 1.0

def test_auc_single_class_is_none():
    assert auc([S(1, a=0.9)]) is None

def test_auc_by_check():
    rows = [S(1, a=0.9, b=0.1), S(0, a=0.1, b=0.9)]
    assert auc_by_check(rows) == {"a": 1.0, "b": 0.0}

def test_youden_threshold_separates_classes():
    rows = [S(1, a=0.3), S(1, a=0.4), S(0, a=0.05), S(0, a=0.1)]
    t = youden_threshold(rows)
    assert 0.1 < t <= 0.3

def test_metrics_at_threshold_on_max_score():
    rows = [S(1, a=0.3), S(1, a=0.05), S(0, a=0.1)]
    m = metrics_at(rows, 0.2)
    assert (m["tp"], m["fn"], m["fp"], m["tn"]) == (1, 1, 0, 1)

def test_logreg_learns_separable_data():
    X = [[0.1, 0.2], [0.2, 0.1], [0.8, 0.9], [0.9, 0.7]]
    y = [0, 0, 1, 1]
    w = fit_logreg(X, y)
    p = predict_logreg(w, [[0.1, 0.1], [0.9, 0.9]])
    assert p[0] < 0.5 < p[1]
