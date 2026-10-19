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

import io, urllib.error

class _Resp:
    def __init__(self, obj): self.b = json.dumps(obj).encode()
    def read(self, *a): return self.b
    def __enter__(self): return self
    def __exit__(self, *a): return False

def _fake(monkeypatch, replies, seen):
    """Patch urlopen: each call pops the next reply (a dict, or an int HTTP error code)."""
    def urlopen(req, timeout=None):
        seen.append({"url": req.full_url, "headers": dict(req.header_items()), "body": json.loads(req.data)})
        r = replies.pop(0)
        if isinstance(r, int):
            raise urllib.error.HTTPError(req.full_url, r, "err", {"Retry-After": "0"}, io.BytesIO(b'{"error":"nope"}'))
        return _Resp(r)
    monkeypatch.setattr(systemone.urllib.request, "urlopen", urlopen)
    monkeypatch.setattr(systemone.time, "sleep", lambda s: None)

def _answer(p, model="cloudflare/clef-flash-20261001", cost=0.0001):
    return {"model": model, "provider": "Cloudflare", "answers": {"q": {"type": "noul", "noul": p}},
            "usage": {"input_tokens": 120, "output_tokens": 0, "cost": cost}}

Q = {"q": ("Q?", {"true": "t", "false": "f"})}

@pytest.fixture
def hosted(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test-secret")
    systemone.configure("openrouter", "cloudflare/clef-flash")
    yield
    systemone.configure()

def test_configure_needs_key_and_model(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    with pytest.raises(ValueError, match="OPENROUTER_API_KEY"):
        systemone.configure("openrouter", "cloudflare/clef-flash")
    monkeypatch.setenv("OPENROUTER_API_KEY", "k")
    with pytest.raises(ValueError, match="needs --model"):
        systemone.configure("openrouter")
    with pytest.raises(ValueError, match="unknown backend"):
        systemone.configure("bedrock", "m")
    systemone.configure()

def test_openrouter_request_shape_and_usage(monkeypatch, hosted):
    seen = []
    _fake(monkeypatch, [_answer(0.8), _answer(0.2, cost=0.0002)], seen)
    assert systemone.ask("skill text", Q) == {"q": 0.8}
    assert systemone.ask("skill text", Q) == {"q": 0.2}
    call = seen[0]
    assert call["url"] == systemone.OPENROUTER_URL and call["headers"]["Authorization"] == "Bearer sk-test-secret"
    assert call["body"] == {"model": "cloudflare/clef-flash", "state": "skill text",
                            "questions": {"q": {"type": "noul", "instructions": "Q?", "criteria": {"true": "t", "false": "f"}}}}
    u = systemone.take_usage()
    assert u["calls"] == 2 and u["input_tokens"] == 240 and u["cost"] == pytest.approx(0.0003)
    assert u["served"] == ["cloudflare/clef-flash-20261001|Cloudflare"] and systemone.take_usage() is None

def test_openrouter_provider_pin_is_sent_and_checked(monkeypatch, capsys):
    monkeypatch.setenv("OPENROUTER_API_KEY", "k")
    systemone.configure("openrouter", "cloudflare/clef-flash", provider="cloudflare")
    seen = []
    other = {**_answer(0.4), "provider": "PrimeIntellect"}
    _fake(monkeypatch, [_answer(0.6), other], seen)
    assert systemone.ask("x", Q) == {"q": 0.6}
    assert seen[0]["body"]["provider"] == {"only": ["cloudflare"], "allow_fallbacks": False}
    assert systemone.ask("x", Q) == {"q": None}  # served by another provider: unscored, never pooled
    assert "not the pinned provider" in capsys.readouterr().err
    with pytest.raises(ValueError, match="only applies"):
        systemone.configure("ollama", provider="cloudflare")
    systemone.configure()

def test_openrouter_unpinned_body_has_no_provider(monkeypatch, hosted):
    seen = []
    _fake(monkeypatch, [_answer(0.5)], seen)
    systemone.ask("x", Q)
    assert "provider" not in seen[0]["body"]

def test_openrouter_state_as_object(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "k")
    systemone.configure("openrouter", "typesafe/jev-1.14", state_format="object")
    seen = []
    _fake(monkeypatch, [_answer(0.5)], seen)
    systemone.ask("skill text", Q)
    assert seen[0]["body"]["state"] == {"skill_md": "skill text"}
    systemone.configure()

def test_openrouter_retries_429_then_succeeds(monkeypatch, hosted):
    seen = []
    _fake(monkeypatch, [429, 503, _answer(0.7)], seen)
    assert systemone.ask("x", Q) == {"q": 0.7} and len(seen) == 3

def test_openrouter_400_is_unparseable_and_never_logs_the_key(monkeypatch, hosted, capsys):
    _fake(monkeypatch, [400], [])
    assert systemone.ask("x", Q) == {"q": None}
    err = capsys.readouterr().err
    assert "OpenRouter HTTP 400" in err and "sk-test-secret" not in err

def test_model_digest_records_served_version(monkeypatch, hosted):
    _fake(monkeypatch, [_answer(0.1), _answer(0.1, model="cloudflare/clef-flash")], [])
    assert systemone.model_digest() == "cloudflare/clef-flash-20261001|Cloudflare"
    assert systemone.model_digest() == "cloudflare/clef-flash|Cloudflare|unpinned"

def test_ollama_body_is_unchanged(monkeypatch):
    systemone.configure()
    seen = []
    _fake(monkeypatch, [{"answers": {"q": {"type": "noul", "noul": 0.3}}}], seen)
    assert systemone.ask("x", Q) == {"q": 0.3}
    assert seen[0]["url"] == systemone.URL and "Authorization" not in seen[0]["headers"]
    assert seen[0]["body"]["model"] == "clef-flash" and systemone.take_usage() is None
