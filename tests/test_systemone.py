import json, pathlib
import pytest
from svb import systemone

FIX = pathlib.Path(__file__).parent / "fixtures" / "systemone_hello.json"

def test_extract_from_real_response():
    raw = json.loads(FIX.read_text())
    assert systemone._extract(raw, ["says_hello"]) == {"says_hello": pytest.approx(0.29, abs=0.01)}

def test_extract_garbage_gives_none():
    assert systemone._extract({"nope": 1}, ["a", "b"]) == {"a": None, "b": None}

def test_ask_unreachable_returns_none(monkeypatch):
    monkeypatch.setattr(systemone, "URL", "http://127.0.0.1:1/v1/systemone")
    out = systemone.ask("x", {"q": ("Q?", {"true": "t", "false": "f"})})
    assert out == {"q": None}

def test_ask_failure_is_logged_to_stderr(monkeypatch, capsys):
    monkeypatch.setattr(systemone, "URL", "http://127.0.0.1:1/v1/systemone")
    systemone.ask("x", {"q": ("Q?", {"true": "t", "false": "f"})})
    assert "systemone" in capsys.readouterr().err
