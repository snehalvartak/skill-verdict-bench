import importlib.util, pathlib

spec = importlib.util.spec_from_file_location("build_dashboard", pathlib.Path(__file__).resolve().parent.parent / "scripts/build_dashboard.py")
bd = importlib.util.module_from_spec(spec); spec.loader.exec_module(bd)

def skill(i, y, src, **s):
    return {"id": i, "y": y, "src": src, "s": s}

def test_no_harm_drops_the_source_and_pairs_the_rest():
    both = lambda m, g: dict(max=m, AST04=m, logreg=m, ast10=m, generic=g)
    skills = [skill("a", 1, "X", **both(.9, .6)), skill("b", 1, "X", **both(.8, .4)),
              skill("c", 0, "X", **both(.1, .5)), skill("d", 0, "X", **both(.2, .7)),
              skill("h", 1, "SkillHarm", **both(.0, .9))]  # would flip the result if it were kept
    r = bd.no_harm(skills, n_boot=200)
    assert (r["n"], r["n_malicious"]) == (4, 2)
    m = r["vs_generic"]["max"]
    assert (m["auc"], m["generic"], m["diff"]) == (1.0, .25, .75)
    assert m["ci"][0] <= m["diff"] <= m["ci"][1]

def test_no_harm_is_none_when_the_source_is_absent():
    assert bd.no_harm([skill("a", 1, "X", generic=.5)], n_boot=10) is None
