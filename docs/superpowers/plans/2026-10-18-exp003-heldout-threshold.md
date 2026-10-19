# Experiment 003: Held-out Threshold and Learned Combination — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Choose the `ast10-split` threshold and check combination on data the test score never sees, then report AUC, TPR and FPR with 95% confidence intervals on a fresh test sample.

**Architecture:** Three new `ast10-split` runs (train, validation, and a fresh test sample that excludes the 200 skills experiments 001 and 002 already looked at). A new module `svb/heldout.py` loads the three runs, checks that they are compatible, and compares three ways of combining the five check scores: `max` (the current method), `AST04` alone (suggested by experiment 002), and a logistic regression fitted on train. Each combiner's threshold is chosen on validation (Youden's J), and everything is reported once on test. The existing `auc`, `youden_threshold` and `metrics_at` are reused unchanged by re-scoring rows with a single combined score.

**Tech Stack:** Python 3.11+, stdlib only for statistics (no new dependencies), pytest, local Ollama `clef-flash`.

**Spec:** `docs/experiments/002-controls.md`, section "Next", item 1, and "Conclusions" 4–5. There is no separate design doc; this plan carries the design.

## Global Constraints

- Python `>=3.11`; dependencies stay `pandas`, `pyarrow` (dev: `pytest`). No sklearn, numpy or scipy.
- Tests run offline: no Ollama, no network. Real runs only in Task 5.
- Model `clef-flash`, method `ast10-split`, `--split random`, seed `0` for train and validation, seed `1` for test.
- Label convention in `predictions.jsonl`: `label` is int `1` (malicious) or `0` (benign).
- A row's score is `None` when the model's answer was unparseable; those rows are skipped by AUC and counted, never imputed.
- Deliberate shortcuts get a `# ponytail:` comment naming the ceiling.
- Commit messages and PR bodies contain no `claude.ai/code/session_...` links.
- The pre-registration (Task 5, Step 1) is committed before the test run is scored.

## Review Focus

1. **Run dirs passed in the wrong slot** (for example, the test run as `--val`): `heldout` must refuse, naming the dir and its actual part, not silently tune on test. → Task 3 `test_load_run_refuses_wrong_part`.
2. **Runs from different model digests or AST prompt versions mixed together**: refuse with the differing key. → Task 3 `test_check_compatible_refuses_digest_and_prompt_mismatch`.
3. **The same skill appearing in two of train, validation and test**: refuse. → Task 3 `test_check_compatible_refuses_overlap`.
4. **Unparseable scores (`None`) in some rows**: logistic regression must skip them in fitting and score them `None` on test, and the report must count them. → Task 4 `test_rows_with_missing_scores_are_skipped_and_counted`.
5. **A run with only one class** (for example, an `--n` so small that no benign skill is sampled): refuse before `youden_threshold` divides by zero. → Task 3 `test_load_run_needs_both_classes`.

---

### Task 1: Generic bootstrap CI in the scorer

**Files:**
- Modify: `svb/score.py` (append after `auc_diff_ci`)
- Test: `tests/test_score.py` (append)

**Interfaces:**
- Consumes: nothing new.
- Produces: `bootstrap_ci(rows: list[dict], stat: Callable[[list[dict]], float | None], n_boot: int = 2000, seed: int = 0) -> tuple[float, float]`: a 95% percentile-bootstrap interval of `stat`, where resamples whose `stat` is `None` are dropped.

- [ ] **Step 1: Write the failing tests**

```python
from svb.score import bootstrap_ci

def test_bootstrap_ci_constant_stat_is_a_point():
    rows = [S(1, a=0.9), S(0, a=0.1)] * 10
    assert bootstrap_ci(rows, lambda rs: 0.3, n_boot=50) == (0.3, 0.3)

def test_bootstrap_ci_perfect_auc_and_drops_none_resamples():
    rows = [S(1, a=0.9), S(0, a=0.1)] * 3   # small: some resamples are single-class, auc -> None
    lo, hi = bootstrap_ci(rows, auc, n_boot=200, seed=0)
    assert lo == hi == 1.0

def test_bootstrap_ci_is_seeded():
    rows = [S(i % 2, a=(i * 7 % 10) / 10) for i in range(30)]
    assert bootstrap_ci(rows, auc, n_boot=100, seed=3) == bootstrap_ci(rows, auc, n_boot=100, seed=3)
```

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run pytest tests/test_score.py -k bootstrap_ci -v`
Expected: FAIL with `ImportError: cannot import name 'bootstrap_ci'`

- [ ] **Step 3: Implement**

```python
def bootstrap_ci(rows, stat, n_boot=2000, seed=0):
    """95% percentile-bootstrap CI of stat(rows); resamples where stat is None are dropped."""
    import random
    rng, vals = random.Random(seed), []
    for _ in range(n_boot):
        v = stat([rows[rng.randrange(len(rows))] for _ in rows])
        if v is not None:
            vals.append(v)
    vals.sort()
    return vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]
```

- [ ] **Step 4: Run the tests**

Run: `uv run pytest -q`
Expected: all pass (52 existing + 3 new).

- [ ] **Step 5: Commit**

```bash
git add svb/score.py tests/test_score.py
git commit -m "feat: generic bootstrap CI in scorer"
```

---

### Task 2: `--exclude` so the fresh test sample skips skills already seen

**Files:**
- Modify: `svb/run.py` (`run()` signature and sampling line; `__main__` argparse)
- Test: `tests/test_run.py` (append)

**Interfaces:**
- Consumes: an existing run dir's `config.json["sample_ids"]`.
- Produces: `run(..., resume=None, exclude=())`, where `exclude` is an iterable of run-dir paths whose `sample_ids` are removed before sampling. CLI: `--exclude DIR [DIR ...]`. `exclude` is **not** written to `config.json`: `sample_ids` already records the result, and adding a key would make `_check_resume` refuse every existing run.

- [ ] **Step 1: Write the failing test**

```python
def test_exclude_drops_skills_from_earlier_runs(tmp_path, monkeypatch):
    monkeypatch.setattr(runmod, "model_digest", lambda: "d")
    df = pd.DataFrame({"benchmark_id": ["a", "b", "c", "d"], "label": [1, 0, 1, 0], "source_id": ["s"] * 4,
                       "text": ["t"] * 4, "attack_categories": [[]] * 4})
    seen = tmp_path / "seen"; seen.mkdir()
    (seen / "config.json").write_text(json.dumps({"sample_ids": ["a", "b"]}))
    out = runmod.run(n=4, methods=["regex"], out_root=str(tmp_path), df=df, exclude=[seen])
    assert json.loads((out / "config.json").read_text())["sample_ids"] == ["c", "d"]
    assert "exclude" not in json.loads((out / "config.json").read_text())
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/test_run.py::test_exclude_drops_skills_from_earlier_runs -v`
Expected: FAIL with `TypeError: run() got an unexpected keyword argument 'exclude'`

- [ ] **Step 3: Implement**

In `svb/run.py`, change the signature and the sampling line:

```python
def run(n=200, split="random", part="test", seed=0, methods=None, out_root="runs", df=None, resume=None, exclude=()):
    methods = methods or DEFAULT_METHODS
    df = load(split, part) if df is None else df
    skip = {i for d in exclude for i in json.loads((pathlib.Path(d) / "config.json").read_text())["sample_ids"]}
    df = sample(df[~df.benchmark_id.isin(skip)], n, seed)
```

In `__main__`, add the argument and pass it through:

```python
    p.add_argument("--exclude", nargs="*", default=[], help="run dirs whose skills are left out of the sample")
    a = p.parse_args()
    print(run(a.n, a.split, a.part, a.seed, a.methods, resume=a.resume, exclude=a.exclude))
```

- [ ] **Step 4: Run the tests**

Run: `uv run pytest -q`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add svb/run.py tests/test_run.py
git commit -m "feat: run --exclude leaves out skills sampled by earlier runs"
```

---

### Task 3: `svb/heldout.py`: load and validate the three runs

**Files:**
- Create: `svb/heldout.py`
- Create: `tests/test_heldout.py`

**Interfaces:**
- Consumes: run dirs in the format `svb.run` writes.
- Produces:
  - `CHECK_IDS = ["AST01", "AST02", "AST03", "AST04", "AST05"]`
  - `load_run(d: str | Path, part: str, method: str = "ast10-split") -> tuple[dict, list[dict]]`: returns `(config, rows of that method)`. A config without `part` counts as `"test"` (runs before `--part` existed). Raises `ValueError` on the wrong part, no rows of `method`, or only one label.
  - `check_compatible(cfgs: list[dict]) -> None`: raises `ValueError` when `model_digest`, `split` or any `CHECK_IDS` prompt hash differs, or when any two runs share a `sample_id`.

- [ ] **Step 1: Write the failing tests**

```python
import json, pytest
from svb import heldout

H = {c: "h" + c for c in heldout.CHECK_IDS}

def make_run(path, part, rows, digest="d", hashes=H, ids=None):
    path.mkdir()
    cfg = {"model_digest": digest, "split": "random", "prompt_hashes": hashes,
           "sample_ids": ids or sorted({r["benchmark_id"] for r in rows})}
    if part is not None:
        cfg["part"] = part
    (path / "config.json").write_text(json.dumps(cfg))
    (path / "predictions.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    return path

def row(i, label, method="ast10-split", **scores):
    s = {c: 0.1 for c in heldout.CHECK_IDS} | scores
    return {"benchmark_id": i, "label": label, "method": method, "flag": False, "scores": s, "attack_categories": []}

TWO = [row("a", 1), row("b", 0)]

def test_load_run_returns_rows_of_the_method(tmp_path):
    d = make_run(tmp_path / "r", "validation", TWO + [row("a", 1, method="ast10")])
    cfg, rows = heldout.load_run(d, "validation")
    assert len(rows) == 2 and cfg["part"] == "validation"

def test_load_run_refuses_wrong_part(tmp_path):
    d = make_run(tmp_path / "r", "test", TWO)
    with pytest.raises(ValueError, match="is a test run, expected validation"):
        heldout.load_run(d, "validation")

def test_load_run_treats_missing_part_as_test(tmp_path):
    d = make_run(tmp_path / "r", None, TWO)
    heldout.load_run(d, "test")

def test_load_run_needs_the_method(tmp_path):
    d = make_run(tmp_path / "r", "train", [row("a", 1, method="ast10"), row("b", 0, method="ast10")])
    with pytest.raises(ValueError, match="no ast10-split predictions"):
        heldout.load_run(d, "train")

def test_load_run_needs_both_classes(tmp_path):
    d = make_run(tmp_path / "r", "train", [row("a", 1), row("b", 1)])
    with pytest.raises(ValueError, match="both malicious and benign"):
        heldout.load_run(d, "train")

def cfg(ids, digest="d", hashes=H):
    return {"model_digest": digest, "split": "random", "prompt_hashes": hashes, "sample_ids": ids}

def test_check_compatible_accepts_disjoint_matching_runs():
    heldout.check_compatible([cfg(["a"]), cfg(["b"]), cfg(["c"])])

def test_check_compatible_refuses_digest_and_prompt_mismatch():
    with pytest.raises(ValueError, match="model_digest"):
        heldout.check_compatible([cfg(["a"]), cfg(["b"], digest="x"), cfg(["c"])])
    with pytest.raises(ValueError, match="AST check prompts"):
        heldout.check_compatible([cfg(["a"]), cfg(["b"]), cfg(["c"], hashes=H | {"AST04": "changed"})])

def test_check_compatible_ignores_non_ast_prompt_hashes():
    heldout.check_compatible([cfg(["a"]), cfg(["b"], hashes=H | {"n1": "x"}), cfg(["c"])])

def test_check_compatible_refuses_overlap():
    with pytest.raises(ValueError, match="share skills"):
        heldout.check_compatible([cfg(["a", "b"]), cfg(["c"]), cfg(["b"])])
```

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run pytest tests/test_heldout.py -v`
Expected: FAIL with `ImportError: cannot import name 'heldout' from 'svb'`

- [ ] **Step 3: Implement**

```python
"""Held-out evaluation: python -m svb.heldout --train runs/A --val runs/B --test runs/C"""
import argparse, json, pathlib

CHECK_IDS = ["AST01", "AST02", "AST03", "AST04", "AST05"]

def load_run(d, part, method="ast10-split"):
    d = pathlib.Path(d)
    cfg = json.loads((d / "config.json").read_text())
    got = cfg.get("part", "test")  # ponytail: runs from before --part existed were all test
    if got != part:
        raise ValueError(f"{d} is a {got} run, expected {part}")
    rows = [r for r in map(json.loads, (d / "predictions.jsonl").read_text().splitlines()) if r["method"] == method]
    if not rows:
        raise ValueError(f"{d} has no {method} predictions")
    if {r["label"] for r in rows} != {0, 1}:
        raise ValueError(f"{d} needs both malicious and benign skills")
    return cfg, rows

def check_compatible(cfgs):
    ref = cfgs[0]
    for c in cfgs[1:]:
        for k in ("model_digest", "split"):
            if c[k] != ref[k]:
                raise ValueError(f"runs differ in {k}")
        if any(c["prompt_hashes"][i] != ref["prompt_hashes"][i] for i in CHECK_IDS):
            raise ValueError("runs differ in AST check prompts")
    ids = [set(c["sample_ids"]) for c in cfgs]
    if any(ids[i] & ids[j] for i in range(len(ids)) for j in range(i + 1, len(ids))):
        raise ValueError("train, validation and test share skills")
```

- [ ] **Step 4: Run the tests**

Run: `uv run pytest -q`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add svb/heldout.py tests/test_heldout.py
git commit -m "feat: heldout loads train/val/test runs and refuses mismatched ones"
```

---

### Task 4: `svb/heldout.py`: combiners, evaluation and report

**Files:**
- Modify: `svb/heldout.py` (append)
- Modify: `tests/test_heldout.py` (append)
- Modify: `README.md` (module list and commands)

**Interfaces:**
- Consumes: `load_run`, `check_compatible`, `CHECK_IDS` (Task 3); `bootstrap_ci` (Task 1); `auc`, `auc_diff_ci`, `fit_logreg`, `predict_logreg`, `metrics_at`, `youden_threshold` from `svb.score` (existing; `auc` and `youden_threshold` read the max of `r["scores"]` and skip rows with no score).
- Produces:
  - `as_rows(rows, score) -> list[dict]`: copies of `rows` whose `scores` is `{"s": score(r)}`, or `{}` when `score(r)` is `None`.
  - `rates(rows, t) -> tuple[float | None, float | None]`: `(TPR, FPR)` at threshold `t`.
  - `evaluate(train, val, test, n_boot=2000, seed=0) -> tuple[dict, list[float]]`: returns `({name: result}, logreg weights)` for names `"max"`, `"AST04"`, `"logreg"`. Each result holds `threshold`, `auc`, `auc_ci`, `tpr`, `tpr_ci`, `fpr`, `fpr_ci`, `unscored` (the count of test rows with no score) and `rows` (the re-scored test rows).
  - `main(argv=None)`: CLI that prints Markdown tables.

- [ ] **Step 1: Write the failing tests**

```python
def signal_in_ast04(prefix, n=20):
    # benign skills trip AST01 hard, so max() can't separate them; AST04 alone can
    return [row(f"{prefix}{i}", i % 2, AST01=0.9, AST04=0.8 if i % 2 else 0.1) for i in range(n)]

def test_as_rows_unscored_rows_are_skipped_by_auc():
    from svb.score import auc
    rs = heldout.as_rows([row("a", 1), row("b", 0, AST04=0.9), row("c", 1)],
                         lambda r: None if r["benchmark_id"] == "c" else r["scores"]["AST04"])
    assert rs[2]["scores"] == {} and auc(rs) == 0.0

def test_rates():
    rs = heldout.as_rows([row("a", 1, AST04=0.6), row("b", 1, AST04=0.2), row("c", 0, AST04=0.7)],
                         lambda r: r["scores"]["AST04"])
    assert heldout.rates(rs, 0.5) == (0.5, 1.0)

def test_evaluate_learned_combination_beats_max():
    res, w = heldout.evaluate(signal_in_ast04("t"), signal_in_ast04("v"), signal_in_ast04("x"), n_boot=50)
    assert res["max"]["auc"] == 0.5
    assert res["AST04"]["auc"] == 1.0 and res["logreg"]["auc"] == 1.0
    assert res["logreg"]["tpr"] == 1.0 and res["logreg"]["fpr"] == 0.0
    assert 0.1 < res["AST04"]["threshold"] <= 0.8
    assert len(w) == 1 + len(heldout.CHECK_IDS) and w[1 + heldout.CHECK_IDS.index("AST04")] > 0

def test_rows_with_missing_scores_are_skipped_and_counted():
    train = signal_in_ast04("t") + [row("tn", 1, AST02=None)]
    test = signal_in_ast04("x") + [row("xn", 0, AST04=None)]
    res, _ = heldout.evaluate(train, signal_in_ast04("v"), test, n_boot=50)
    assert res["logreg"]["unscored"] == 1 and res["AST04"]["unscored"] == 1
    assert res["max"]["unscored"] == 0  # max uses whatever scores are present
    assert res["logreg"]["auc"] == 1.0

def test_main_prints_tables(tmp_path, capsys):
    tr = make_run(tmp_path / "tr", "train", signal_in_ast04("t"))
    va = make_run(tmp_path / "va", "validation", signal_in_ast04("v"))
    te = make_run(tmp_path / "te", "test", signal_in_ast04("x"))
    heldout.main(["--train", str(tr), "--val", str(va), "--test", str(te), "--n-boot", "50"])
    out = capsys.readouterr().out
    assert "| logreg | " in out and "| logreg - max | " in out and "| AST04 | " in out
    assert "test skills: 20 (10 malicious, 10 benign)" in out
```

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run pytest tests/test_heldout.py -v`
Expected: the five new tests FAIL with `AttributeError: module 'svb.heldout' has no attribute 'as_rows'` (and similar).

- [ ] **Step 3: Implement**

Add to the imports at the top of `svb/heldout.py`:

```python
from svb.score import auc, auc_diff_ci, bootstrap_ci, fit_logreg, metrics_at, predict_logreg, youden_threshold
```

Append:

```python
def _full(r):
    v = [r["scores"].get(c) for c in CHECK_IDS]
    return None if None in v else v

def as_rows(rows, score):
    """Re-score rows with one combined score so auc/youden/metrics_at apply unchanged."""
    out = []
    for r in rows:
        s = score(r)
        out.append({**r, "scores": {} if s is None else {"s": s}})
    return out

def rates(rows, t):
    m = metrics_at(rows, t)
    tpr = m["tp"] / (m["tp"] + m["fn"]) if m["tp"] + m["fn"] else None
    fpr = m["fp"] / (m["fp"] + m["tn"]) if m["fp"] + m["tn"] else None
    return tpr, fpr

def evaluate(train, val, test, n_boot=2000, seed=0):
    fit = [r for r in train if _full(r)]
    # ponytail: unweighted, unregularised fit on 5 features; Youden on validation absorbs class imbalance
    w = fit_logreg([_full(r) for r in fit], [r["label"] for r in fit])
    combiners = {
        "max": lambda r: max([v for v in r["scores"].values() if v is not None], default=None),
        "AST04": lambda r: r["scores"].get("AST04"),
        "logreg": lambda r: None if _full(r) is None else predict_logreg(w, [_full(r)])[0],
    }
    res = {}
    for name, f in combiners.items():
        t = youden_threshold(as_rows(val, f))
        rs = as_rows(test, f)
        tpr, fpr = rates(rs, t)
        res[name] = {"threshold": t, "auc": auc(rs), "auc_ci": bootstrap_ci(rs, auc, n_boot, seed),
                     "tpr": tpr, "tpr_ci": bootstrap_ci(rs, lambda x: rates(x, t)[0], n_boot, seed),
                     "fpr": fpr, "fpr_ci": bootstrap_ci(rs, lambda x: rates(x, t)[1], n_boot, seed),
                     "unscored": sum(not r["scores"] for r in rs), "rows": rs}
    return res, w

def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--train", required=True)
    p.add_argument("--val", required=True)
    p.add_argument("--test", required=True)
    p.add_argument("--method", default="ast10-split")
    p.add_argument("--n-boot", type=int, default=2000)
    a = p.parse_args(argv)
    (ct, tr), (cv, va), (cx, te) = (load_run(a.train, "train", a.method), load_run(a.val, "validation", a.method),
                                    load_run(a.test, "test", a.method))
    check_compatible([ct, cv, cx])
    res, w = evaluate(tr, va, te, a.n_boot)
    mal = sum(r["label"] for r in te)
    print(f"train skills: {len(tr)}, validation skills: {len(va)}, test skills: {len(te)} ({mal} malicious, {len(te) - mal} benign)\n")
    print("| combiner | threshold (from validation) | test AUC [95% CI] | test TPR [95% CI] | test FPR [95% CI] | unscored |")
    print("|---|---|---|---|---|---|")
    ci = lambda v, c: f"{v:.3f} [{c[0]:.3f}, {c[1]:.3f}]"
    for m, r in res.items():
        print(f"| {m} | {r['threshold']:.3f} | {ci(r['auc'], r['auc_ci'])} | {ci(r['tpr'], r['tpr_ci'])} | {ci(r['fpr'], r['fpr_ci'])} | {r['unscored']} |")
    print("\n| paired difference on test | AUC diff [95% CI] |\n|---|---|")
    for x, y in (("logreg", "max"), ("AST04", "max"), ("logreg", "AST04")):
        lo, hi = auc_diff_ci(res[x]["rows"], res[y]["rows"], a.n_boot)
        print(f"| {x} - {y} | {res[x]['auc'] - res[y]['auc']:+.3f} [{lo:+.3f}, {hi:+.3f}] |")
    print("\n| logreg weight | " + " | ".join(["intercept"] + CHECK_IDS) + " |")
    print("|---|" + "---|" * len(w))
    print("| value | " + " | ".join(f"{x:+.2f}" for x in w) + " |")

if __name__ == "__main__":
    main()
```

In `README.md`, add to the module list after the `svb/compare.py` line:

```
svb/heldout.py     threshold and check combination chosen on validation, reported on test with CIs
```

and add to the command block after the `svb.score` line:

```
uv run python -m svb.heldout --train runs/<train> --val runs/<val> --test runs/<test>   # held-out evaluation
```

Update the README's test count comment to the number `uv run pytest -q` reports.

- [ ] **Step 4: Run the tests**

Run: `uv run pytest -q`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add svb/heldout.py tests/test_heldout.py README.md
git commit -m "feat: heldout compares max, AST04 and logreg with thresholds from validation"
```

---

### Task 5: Pre-register, run, and write up experiment 003

**Files:**
- Create: `docs/experiments/003-heldout-threshold.md`

**Interfaces:**
- Consumes: `svb.run` with `--part` and `--exclude` (Task 2); `svb.heldout` (Tasks 3–4).
- Produces: three run dirs under `runs/` (git-ignored) and the experiment write-up.

- [ ] **Step 1: Write and commit the pre-registration before any test scoring**

Create `docs/experiments/003-heldout-threshold.md`:

```markdown
# Experiment 003: Held-out threshold and learned combination

Date: <date of the runs>. Method: `ast10-split`. Model: `clef-flash` (same digest as 001 and 002, checked by `svb.heldout`).

## Question

Experiments 001 and 002 chose thresholds and suggested combinations on the same 200 test skills they reported on. Do those findings hold when the threshold and the combination are chosen on separate data and measured on skills nobody has looked at?

## Pre-registration (committed before the test run was scored)

- Train: 200 skills from `random/train`, seed 0. Validation: 200 skills from `random/validation`, seed 0. Test: 200 skills from `random/test`, seed 1, excluding the 200 skills used in 001 and 002 (`--exclude runs/20261003-115058`).
- Combiners: `max` of the five check scores (current method); `AST04` alone (from 002, conclusion 4); logistic regression on the five scores, fitted on train.
- Each threshold is Youden's J on validation. Test is scored once; nothing is changed after seeing it.
- Primary comparison: test AUC of `logreg` minus `max`, with a paired-bootstrap 95% CI. Secondary: `AST04` minus `max`, and the TPR and FPR of each combiner at its validation threshold, with 95% CIs.
- Unparseable scores are skipped and counted, not imputed.

## Results

## Conclusions

## Limitations

## Notes on the run
```

```bash
git add docs/experiments/003-heldout-threshold.md
git commit -m "docs: pre-register experiment 003"
```

- [ ] **Step 2: Score train and validation**

Each run takes about 50 minutes (about 15 seconds per skill for `ast10-split`). Run them one at a time in the background. If one is killed, continue it with `--resume <run dir>` and the same arguments.

```bash
uv run python -m svb.run --n 200 --part train --seed 0 --methods ast10-split > runs/exp003-train.log 2>&1
uv run python -m svb.run --n 200 --part validation --seed 0 --methods ast10-split > runs/exp003-val.log 2>&1
```

Expected: each prints a run dir; `uv run python -m svb.score <dir>` shows 0 or a few unparseable rows.

- [ ] **Step 3: Score the fresh test sample**

```bash
uv run python -m svb.run --n 200 --part test --seed 1 --methods ast10-split --exclude runs/20261003-115058 > runs/exp003-test.log 2>&1
```

Check the exclusion took effect:

```bash
uv run python -c "import json,sys; a=set(json.load(open('runs/20261003-115058/config.json'))['sample_ids']); b=set(json.load(open(sys.argv[1]+'/config.json'))['sample_ids']); print(len(b), len(a & b))" runs/<test run>
```

Expected: `200 0` (or close to 200; `sample()` rounds per class).

- [ ] **Step 4: Evaluate**

```bash
uv run python -m svb.heldout --train runs/<train> --val runs/<val> --test runs/<test> | tee runs/exp003-heldout.md
```

- [ ] **Step 5: Write up and commit**

Fill in Results (paste the tables and name the three run dirs), Conclusions (answer the pre-registered comparisons first, then anything exploratory, labelled as such), Limitations (benign counts, one seed, `SKILL.md` text only), and Notes on the run (unparseable counts, kills and resumes, timing). Do not edit the pre-registration section.

```bash
git add docs/experiments/003-heldout-threshold.md
git commit -m "docs: experiment 003 held-out threshold and combination"
```
