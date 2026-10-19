"""Decision-model client: local Ollama (/v1/systemone) or hosted OpenRouter (/api/alpha/decisions).

Both take {model, state, questions:{id:{type:"noul", instructions, criteria}}} and return answers[id].noul.
Pick the backend once per process with configure(); methods call ask() unchanged.
"""
import json, os, sys, threading, time, urllib.error, urllib.request

URL = "http://localhost:11434/v1/systemone"
TAGS = "http://localhost:11434/api/tags"
OPENROUTER_URL = os.environ.get("SVB_OPENROUTER_URL", "https://openrouter.ai/api/alpha/decisions")  # override only for tests
RETRY_CODES = {408, 429, 500, 502, 503, 504}
BACKEND = {"name": "ollama", "model": "clef-flash", "state_format": "string", "provider": None}
_tl = threading.local()  # per-thread usage, so concurrent workers each see only their own calls

def configure(backend="ollama", model=None, state_format="string", provider=None):
    """Choose where ask() sends questions. OpenRouter reads its key from OPENROUTER_API_KEY, never from args.
    `provider`: OpenRouter provider slug (e.g. cloudflare) that serves every call, with no fallback to others."""
    if backend not in ("ollama", "openrouter"):
        raise ValueError(f"unknown backend {backend!r}: use ollama or openrouter")
    if state_format not in ("string", "object"):
        raise ValueError("state_format must be string or object")
    if provider and backend != "openrouter":
        raise ValueError("--provider only applies to --backend openrouter")
    if backend == "openrouter":
        if not model:
            raise ValueError("--backend openrouter needs --model, e.g. cloudflare/clef-flash")
        if not os.environ.get("OPENROUTER_API_KEY"):
            raise ValueError("set the OPENROUTER_API_KEY environment variable to use --backend openrouter")
    BACKEND.update(name=backend, model=model or "clef-flash", state_format=state_format, provider=provider or None)
    _tl.usage = None

def _extract(raw, ids):
    # answers[id] = {"type": "noul", "noul": P(true) in [0, 1]}
    answers = raw.get("answers", {}) if isinstance(raw, dict) else {}
    out = {}
    for i in ids:
        a = answers.get(i)
        v = a.get("noul") if isinstance(a, dict) else None
        out[i] = float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else None
    return out

def _body(state, questions, model):
    return {"model": model, "state": state, "questions": {
        qid: {"type": "noul", "instructions": ins, "criteria": crit}
        for qid, (ins, crit) in questions.items()}}

def _record(raw):
    u = getattr(_tl, "usage", None)
    if u is None:
        u = _tl.usage = {"calls": 0, "input_tokens": 0, "cost": 0.0, "served": []}
    usage = raw.get("usage", {}) if isinstance(raw, dict) else {}
    u["calls"] += 1
    u["input_tokens"] += usage.get("input_tokens") or 0
    u["cost"] += usage.get("cost") or 0.0
    served = f"{raw.get('model')}|{raw.get('provider')}" if isinstance(raw, dict) else None
    if served and served not in u["served"]:
        u["served"].append(served)

def take_usage():
    """Usage of this thread's calls since the last take (hosted backend only), then reset."""
    u, _tl.usage = getattr(_tl, "usage", None), None
    return u

def _slug(name):
    return "".join(c for c in str(name).lower() if c.isalnum())

def _post_openrouter(body, attempts=5):
    pin = BACKEND["provider"]
    if pin:  # every call on one provider: providers differ in context handling (one truncates silently)
        body = {**body, "provider": {"only": [pin], "allow_fallbacks": False}}
    req = urllib.request.Request(OPENROUTER_URL, json.dumps(body).encode(), {
        "Content-Type": "application/json", "Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"]})
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                raw = json.load(r)
            if pin and isinstance(raw, dict) and _slug(raw.get("provider")) != _slug(pin):
                raise RuntimeError(f"OpenRouter served {raw.get('provider')!r}, not the pinned provider {pin!r}")
            return raw
        except urllib.error.HTTPError as e:
            if e.code not in RETRY_CODES or attempt == attempts - 1:
                detail = e.read()[:300].decode("utf-8", "replace")  # the response body, never the request headers
                raise RuntimeError(f"OpenRouter HTTP {e.code}: {detail}") from None
            wait = e.headers.get("Retry-After", "") if e.headers else ""
            time.sleep(min(30.0, float(wait)) if wait.replace(".", "", 1).isdigit() else 2 ** attempt)
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt == attempts - 1:
                raise RuntimeError(f"OpenRouter unreachable: {type(e).__name__}") from None
            time.sleep(2 ** attempt)

def ask(state, questions, model=None, url=None):
    model = model or BACKEND["model"]
    try:
        if BACKEND["name"] == "openrouter":
            st = {"skill_md": state} if BACKEND["state_format"] == "object" else state
            raw = _post_openrouter(_body(st, questions, model))
            _record(raw)
            return _extract(raw, list(questions))
        req = urllib.request.Request(url or URL, json.dumps(_body(state, questions, model)).encode(),
                                     {"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=300) as r:
            return _extract(json.load(r), list(questions))
    except Exception as e:  # ponytail: any failure counts as unparseable; score.py reports the count
        print(f"systemone call failed: {type(e).__name__}: {e}", file=sys.stderr)
        return {q: None for q in questions}

def model_digest(model="clef-flash:latest"):
    """Local: the Ollama digest. Hosted: the dated model slug and provider OpenRouter actually serves,
    from one tiny call, so a silent version change shows up as a different digest."""
    if BACKEND["name"] == "openrouter":
        st = {"skill_md": "ping"} if BACKEND["state_format"] == "object" else "ping"
        raw = _post_openrouter(_body(st, {"q": ("Is this text empty?", {"true": "yes", "false": "no"})}, BACKEND["model"]))
        served = raw.get("model") or BACKEND["model"]
        pinned = served != BACKEND["model"]  # a dated slug differs from the alias we asked for
        return f"{served}|{raw.get('provider')}" + ("" if pinned else "|unpinned")
    with urllib.request.urlopen(TAGS, timeout=10) as r:
        return next(m["digest"] for m in json.load(r)["models"] if m["name"] == model)
