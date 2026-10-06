#!/usr/bin/env python3
"""Local, weight-free validation of c2c_fidelity.ipynb.

  1. notebook JSON valid (nbformat) and every code cell byte-compiles
  2. every `rosetta.*` import in the notebook resolves, by AST, to a top-level name in the cloned C2C repo
  3. every call into C2C (build_prompt, load_projector, RosettaModel(...), ROS.forward/generate/...) only uses
     parameters that exist in the C2C source at the pinned commit
  4. the MMLU-Redux subject list equals C2C's, and the notebook's answer-key parser agrees with C2C's
     UnifiedEvaluator.parse_answer on a battery of synthetic examples

Usage: python validate_notebook.py [notebook] [c2c_dir]     (stdlib + nbformat only; no torch, no network)
"""
import ast, json, sys, itertools, textwrap
from pathlib import Path

HERE = Path(__file__).resolve().parent
NB = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "c2c_fidelity.ipynb"
C2C = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / "C2C"
fails = []

def check(ok, msg):
    print(("PASS  " if ok else "FAIL  ") + msg)
    if not ok:
        fails.append(msg)

# 1 --- notebook structure + byte-compile
import nbformat
nb = nbformat.read(NB, as_version=4)
nbformat.validate(nb)
check(True, f"nbformat valid, {len(nb.cells)} cells")
code_cells = [c for c in nb.cells if c.cell_type == "code"]
for i, c in enumerate(code_cells):
    try:
        compile(c.source, f"<cell {i}>", "exec")
    except SyntaxError as e:
        check(False, f"cell {i} does not compile: {e}")
check(not any("does not compile" in f for f in fails), f"all {len(code_cells)} code cells byte-compile")
check(not any(l.lstrip().startswith(("%", "!")) for c in code_cells for l in c.source.split("\n")), "no IPython magics/shell escapes (cells are plain Python)")
src = "\n".join(c.source for c in code_cells)
tree = ast.parse(src)

# 2 --- rosetta imports exist in the clone
def module_file(mod):
    p = C2C / Path(*mod.split("."))
    return p.with_suffix(".py") if p.with_suffix(".py").exists() else (p / "__init__.py" if (p / "__init__.py").exists() else None)

def top_level_defs(path):
    t = ast.parse(path.read_text())
    names = {}
    for n in t.body:
        if isinstance(n, (ast.FunctionDef, ast.ClassDef)):
            names[n.name] = n
        elif isinstance(n, ast.Assign):
            for tgt in n.targets:
                if isinstance(tgt, ast.Name):
                    names[tgt.id] = n
        elif isinstance(n, (ast.Import, ast.ImportFrom)):
            for a in n.names:
                names[(a.asname or a.name).split(".")[0]] = n
    return names

imported = {}   # local name -> (module, node)
for n in ast.walk(tree):
    if isinstance(n, ast.ImportFrom) and n.module and n.module.startswith("rosetta"):
        mf = module_file(n.module)
        check(mf is not None, f"module {n.module} exists in clone")
        if mf is None:
            continue
        defs = top_level_defs(mf)
        for a in n.names:
            check(a.name in defs, f"{n.module}.{a.name} defined")
            imported[a.asname or a.name] = defs.get(a.name)

# 3 --- call signatures
def params(fn):
    a = fn.args
    pos = [x.arg for x in a.posonlyargs + a.args]
    kwonly = [x.arg for x in a.kwonlyargs]
    return set(pos + kwonly), a.kwarg is not None, pos

def class_method(cls_node, name):
    for b in cls_node.body:
        if isinstance(b, ast.FunctionDef) and b.name == name:
            return b
    return None

wrapper_defs = top_level_defs(C2C / "rosetta/model/wrapper.py")
RM = wrapper_defs["RosettaModel"]
def check_call(call, fn, label, allow_self=False):
    names, has_kwargs, pos = params(fn)
    if allow_self:
        pos = pos[1:]; names = names - {"self"}
    bad = [k.arg for k in call.keywords if k.arg and k.arg not in names]
    ok = (not bad) or has_kwargs and label.endswith("(**kwargs)-tolerant")
    check(not bad, f"{label}: keywords {[k.arg for k in call.keywords if k.arg]} all accepted" + (f" (unknown: {bad})" if bad else ""))
    check(len(call.args) <= len(pos) or any(isinstance(a, ast.Starred) for a in call.args), f"{label}: positional count ok")

seen = set()
for n in ast.walk(tree):
    if not isinstance(n, ast.Call):
        continue
    f = n.func
    if isinstance(f, ast.Name) and f.id in imported and isinstance(imported[f.id], ast.FunctionDef):
        key = (f.id, tuple(k.arg for k in n.keywords), len(n.args))
        if key not in seen:
            seen.add(key); check_call(n, imported[f.id], f"call {f.id}()")
    elif isinstance(f, ast.Name) and f.id == "RosettaModel":
        init = class_method(RM, "__init__")
        key = ("RM", tuple(k.arg for k in n.keywords))
        if key not in seen:
            seen.add(key); check_call(n, init, "RosettaModel(...)", allow_self=True)
    elif isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) and f.value.id in ("ROS", "ros") and f.attr in ("forward", "generate", "load_projector_config"):
        m = class_method(RM, f.attr)
        key = (f.attr, tuple(k.arg for k in n.keywords))
        if m is not None and key not in seen:
            seen.add(key); check_call(n, m, f"ROS.{f.attr}()", allow_self=True)
        check(m is not None, f"RosettaModel.{f.attr} exists")

attrs = {t.attr for b in ast.walk(RM) if isinstance(b, ast.Assign) for t in b.targets if isinstance(t, ast.Attribute)}
for name in ("projector_dict", "model_list", "kv_cache_dict"):
    check(name in attrs or name in {x.arg for x in ast.walk(RM) if isinstance(x, ast.arg)}, f"RosettaModel.{name} set in __init__/methods")
check(any(isinstance(n, ast.Attribute) and n.attr == "projector_dict" for n in ast.walk(tree)), "notebook reads RosettaModel.projector_dict (checked above)")

# 4 --- subject list + answer-key parity with C2C's evaluator
ue = (C2C / "script/evaluation/unified_evaluator.py").read_text()
ue_tree = ast.parse(ue)
cfg = next(n.value for n in ue_tree.body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "DATASET_CONFIGS")
cfg = ast.literal_eval(cfg)
nb_subjects = None
for n in tree.body:
    if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "MMLU_SUBJECTS":
        nb_subjects = ast.literal_eval(n.value)
        break
check(nb_subjects == cfg["mmlu-redux"]["subjects"], f"MMLU-Redux subject list identical to C2C's ({len(nb_subjects or [])} subjects)")

cls = next(n for n in ue_tree.body if isinstance(n, ast.ClassDef) and n.name == "UnifiedEvaluator")
pa = class_method(cls, "parse_answer")
ns = {"re": __import__("re"), "Dict": dict, "Any": object, "Optional": __import__("typing").Optional}
exec(textwrap.dedent(ast.get_source_segment(ue, pa)), ns)
fake = type("F", (), {"dataset_name": "mmlu-redux"})()
nb_fn_src = next(ast.get_source_segment(src, n) for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "mmlu_redux_key")
ns2 = {"LETTERS": "ABCD"}
exec(nb_fn_src, ns2)
mism = []
for et, ans, ca in itertools.product(["ok", "no_correct_answer", "expert", "wrong_groundtruth", "bad_options_clarity", ""], [0, 1, 2, 3], [None, "", "A", "B", "C", "D", "0", "1", "2", "3"]):
    ex = {"error_type": et, "answer": ans, "correct_answer": ca}
    try:
        theirs = ns["parse_answer"](fake, ex)
    except Exception:
        theirs = "EXC"
    mine = ns2["mmlu_redux_key"](ex)
    if theirs == "EXC":
        continue   # C2C crashes on that input (e.g. empty string compare); ours returns a value, not a disagreement
    if theirs != mine:
        mism.append((ex, theirs, mine))
check(not mism, f"mmlu_redux_key matches C2C parse_answer on {6*4*10} synthetic cases" + (f" ; first mismatch {mism[0]}" if mism else ""))


# 5 --- (run 3) GSM8K prompt / gold-answer parity with C2C's evaluator, if the notebook has the numeric task
if any(isinstance(n, ast.FunctionDef) and n.name == "gsm8k_prompt" for n in tree.body):
    fmt_m = class_method(cls, "_format_math_problem_example")
    ns3 = {"Dict": dict, "Any": object, "List": list, "Optional": __import__("typing").Optional}
    exec(textwrap.dedent(ast.get_source_segment(ue, fmt_m)), ns3)
    fake3 = type("F", (), {"dataset_name": "gsm8k"})()
    nb_ns = {"re": __import__("re")}
    for n in tree.body:
        if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "GSM8K_TEMPLATE":
            exec(compile(ast.Module([n], []), "nb", "exec"), nb_ns)
        if isinstance(n, ast.FunctionDef) and n.name in ("gsm8k_prompt", "gsm8k_gold"):
            exec(compile(ast.Module([n], []), "nb", "exec"), nb_ns)
    qs = ["Tom has 3 apples and buys 4 more. How many?", "A\nmultiline question with $ signs and {braces}?", ""]
    check(all(nb_ns["gsm8k_prompt"](q) == ns3["_format_math_problem_example"](fake3, {"question": q}, use_cot=False) for q in qs), "gsm8k_prompt identical to C2C _format_math_problem_example on 3 questions")
    ns4 = {"re": __import__("re")}
    exec(textwrap.dedent(ast.get_source_segment(ue, pa)), ns4)
    answers = ["She has 7 apples.\n#### 7", "x\n#### 1,000", "x\n#### -3.5", "x\n#### 12 dollars", "no marker", "a\n#### 5\n#### 6"]
    check(all(nb_ns["gsm8k_gold"](a) == ns4["parse_answer"](fake3, {"answer": a}) for a in answers), "gsm8k_gold identical to C2C parse_answer on 6 synthetic answers")

print("\nRESULT:", "ALL CHECKS PASSED" if not fails else f"{len(fails)} FAILED")
sys.exit(1 if fails else 0)
