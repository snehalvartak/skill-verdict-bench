import pandas as pd
from msd.data import sample

def _df(n_mal, n_ben):
    return pd.DataFrame({"benchmark_id": range(n_mal + n_ben),
                         "label": [1] * n_mal + [0] * n_ben})

def test_sample_keeps_ratio():
    s = sample(_df(770, 230), n=100, seed=0)
    assert len(s) == 100 and s.label.sum() == 77

def test_sample_is_deterministic():
    a, b = sample(_df(50, 50), 20, seed=1), sample(_df(50, 50), 20, seed=1)
    assert list(a.benchmark_id) == list(b.benchmark_id)

def test_sample_larger_than_class_takes_all():
    s = sample(_df(100, 3), n=100, seed=0)
    assert (s.label == 0).sum() == 3

def test_failed_download_leaves_no_cache_file(tmp_path, monkeypatch):
    from msd import data
    import pytest
    monkeypatch.setattr(data, "DATA", tmp_path)
    def bad(url, dest):
        open(dest, "wb").write(b"partial")
        raise OSError("cut short")
    monkeypatch.setattr(data.urllib.request, "urlretrieve", bad)
    with pytest.raises(OSError):
        data._fetch("primary.parquet")
    assert not (tmp_path / "primary.parquet").exists()

def test_load_filters_split_and_drops_missing_text(tmp_path, monkeypatch):
    from msd import data
    primary = pd.DataFrame({
        "benchmark_id": ["a", "b", "c", "d"], "label": [1, 0, 1, 0],
        "source_id": ["s1"] * 4, "skill_text": ["t", "t", None, "t"],
        "text_available": [True, True, False, True],
        "attack_categories": [["x"], [], ["y"], []]})
    splits = pd.DataFrame({"benchmark_id": ["a", "b", "c", "d"], "label": [1, 0, 1, 0],
                           "source_id": ["s1"] * 4, "split": ["test", "test", "test", "train"]})
    p, s = tmp_path / "p.parquet", tmp_path / "s.parquet"
    primary.to_parquet(p); splits.to_parquet(s)
    monkeypatch.setattr(data, "_fetch", lambda name: p if name == "primary.parquet" else s)
    df = data.load()
    assert list(df.benchmark_id) == ["a", "b"]
    assert list(df.columns) == ["benchmark_id", "label", "source_id", "text", "attack_categories"]
