"""Helper for exp004_overnight.sh. Reads MODEL (and SF) from the environment; the API key stays in the environment.

Default: find which state form the hosted model accepts and print "<form> <served model digest>".
CONTEXT_CHECK=1: send the longest test skill of each disjoint split and print how many tokens the model read.
"""
import os, sys
from svb import systemone

MODEL = os.environ["MODEL"]

def probe():
    last = None
    for form in ("string", "object"):
        systemone.configure("openrouter", MODEL, form)
        try:
            print(form, systemone.model_digest())
            return
        except RuntimeError as e:
            last = e
            print(f"state as a {form}: {e}", file=sys.stderr)
    sys.exit(f"no state form worked: {last}")

def context_check():
    from svb.checks import truncate
    from svb.data import load
    form = os.environ["SF"]
    systemone.configure("openrouter", MODEL, form)
    q = {"q": ("Is this text long?", {"true": "yes", "false": "no"})}
    for split in ("source_disjoint", "m_structural_disjoint"):
        df = load(split, "test")
        text, cut = truncate(df.text[df.text.str.len().idxmax()])
        state = {"skill_md": text} if form == "object" else text
        try:
            raw = systemone._post_openrouter(systemone._body(state, q, MODEL))
        except RuntimeError as e:
            print(f"{split}: longest test skill ({len(text)} characters) was refused: {e} "
                  "<- WARNING: long skills will be unscored")
            continue
        tok = (raw.get("usage") or {}).get("input_tokens")
        warn = (" <- WARNING: far fewer tokens than characters/4 suggests; the context window may be cutting long skills"
                if isinstance(tok, int) and tok < len(text) / 6 else "")
        print(f"{split}: longest test skill sent as {len(text)} characters (cut at 60,000: {cut}); "
              f"model read {tok} input tokens{warn}")

if __name__ == "__main__":
    context_check() if os.environ.get("CONTEXT_CHECK") else probe()
