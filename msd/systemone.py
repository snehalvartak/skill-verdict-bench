import json, urllib.request

URL = "http://localhost:11434/v1/systemone"
TAGS = "http://localhost:11434/api/tags"

def _extract(raw, ids):
    # answers[id] = {"type": "noul", "noul": P(true) in [0, 1]}
    answers = raw.get("answers", {}) if isinstance(raw, dict) else {}
    out = {}
    for i in ids:
        a = answers.get(i)
        v = a.get("noul") if isinstance(a, dict) else None
        out[i] = float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else None
    return out

def ask(state, questions, model="clef-flash", url=None):
    body = {"model": model, "state": state, "questions": {
        qid: {"type": "noul", "instructions": ins, "criteria": crit}
        for qid, (ins, crit) in questions.items()}}
    req = urllib.request.Request(url or URL, json.dumps(body).encode(),
                                 {"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return _extract(json.load(r), list(questions))
    except Exception:  # ponytail: any failure counts as unparseable; run.py reports the count
        return {q: None for q in questions}

def model_digest(model="clef-flash:latest"):
    with urllib.request.urlopen(TAGS, timeout=10) as r:
        return next(m["digest"] for m in json.load(r)["models"] if m["name"] == model)
