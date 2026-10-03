import re

# ponytail: naive keyword scanner baseline; the point is to be beatable
PATTERNS = {
    "pipe_to_shell": r"(curl|wget)[^\n|]*\|\s*(ba)?sh",
    "secret_paths": r"~/\.ssh|\.env\b|\.aws/credentials|id_rsa",
    "base64_blob": r"[A-Za-z0-9+/]{120,}={0,2}",
    "webhook": r"(discord(app)?\.com/api/webhooks|hooks\.slack\.com|webhook\.site)",
    "concealment": r"(do not|don't|never)\s+(mention|tell|reveal|show)[^\n]{0,40}\buser\b",
}
_COMPILED = {k: re.compile(v, re.I) for k, v in PATTERNS.items()}

def regex(skill_text):
    hits = [k for k, p in _COMPILED.items() if p.search(skill_text)]
    return {"flag": bool(hits), "evidence": ",".join(hits), "scores": {}}
