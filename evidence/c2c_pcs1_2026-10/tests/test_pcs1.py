#!/usr/bin/env python3
"""Unit tests for the PCS1 notebook (no weights): task generator semantics, wrong-P partner properties, analysis and decision rule on synthetic data.
   .venv-smoke/bin/python test_pcs1.py [notebook]"""
import ast, random, re, sys
from pathlib import Path
import numpy as np, nbformat
from transformers import AutoTokenizer

NB = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "pcs1" / "pcs1_new_deduction.ipynb"
src = "\n".join(c.source for c in nbformat.read(NB, 4).cells if c.cell_type == "code")
tree = ast.parse(src)
tok = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")
ns = {"np": np, "random": random, "re": re, "RECORDS": {}, "ITEMS": {}, "LETTERS": "0123456789", "SEED": 0, "TOK_R": tok, "TOK_S": tok,
      "CFG": {"N_BOOT": 1000, "K_MM": 3, "CAL_SEED": 0, "DEPTHS": [2, 3], "N_PER_DEPTH": 10}}
want = {"boot_ci", "fmt", "arrays", "_lp_vec", "cal_folds", "crossfit_calibrate", "cal_array", "gen_program", "chat_split", "enc", "make_item", "build_items",
        "note_ids", "analyze_pcs1", "reading_pcs1"}
for n in tree.body:
    if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") in ("HEADER", "VARS", "K_INVERTIBLE"):
        exec(compile(ast.Module([n], []), "nb", "exec"), ns)
    if isinstance(n, ast.FunctionDef) and n.name in want:
        exec(compile(ast.Module([n], []), "nb", "exec"), ns)
ok = True
def check(c, m):
    global ok; ok &= bool(c); print(("PASS  " if c else "FAIL  ") + m)

# ---- generator semantics
good = True; depth_ok = True
for d in (0, 1, 2, 3, 4):
    for i in range(60):
        it = ns["make_item"](d, i, "t")
        env = {}
        for line in it["lines"]:
            lhs, rhs = line.split(" = ")
            env[lhs.strip()] = eval(rhs.replace("%", "%"), {}, env) % 10 if "(" in rhs else int(rhs)   # evaluate the program text itself
        good &= env == it["vals"] and env[it["xvar"]] == it["X"]
        good &= it["ans"] == (it["X"] * it["k"] + it["m"]) % 10 and it["ans"] not in it["vals"].values() and it["k"] == 1
        good &= len(it["lines"]) == 3 + d
        # U depends on the final value of xvar only; for wrong belief X' != X the implied answer differs (bijection)
        good &= all(((x * it["k"] + it["m"]) % 10) != it["ans"] for x in range(10) if x != it["X"])
check(good, "program text evaluates to the stored values; U-answer = (X*k+m)%10, differs from EVERY final variable value; k invertible; wrong belief => different answer")
it = ns["make_item"](3, 0, "t")
chain = re.findall(r"^(\w) = \((\w) \+ ", "\n".join(it["lines"][3:]), flags=re.M)
check(all(chain[j][1] == it["lines"][3 + j - 1][0] for j in range(1, len(chain))), "each update reads the variable updated at the previous step (dependency chain: depth is real)")
check(it["ids_full"][: it["n_p1"]] == it["p1"] and it["ids_full"][it["n_p1"]:] == it["p2U"] and it["ids_state"][: it["n_p1"]] == it["p1"], "fused section p1 is the common prefix; U is only in the tail")
txt = tok.decode(it["p1"])
check("Now e" not in txt and "What is" not in txt and it["U_text"].split(".")[0] not in txt, "the fused section (all A ever reads through the bridge) contains no U text")
check(tok.decode(it["p2U"]).endswith("The answer is ") and tok("3", add_special_tokens=False)["input_ids"] == [18], "response ends at 'The answer is ' so the next token is a digit")
# partners
pf = True
for i in range(40):
    it = ns["make_item"](4, i, "t")
    xs = [p["Xp"] for p in it["partners"]]
    pf &= len(it["partners"]) == 3 and all(len(p["p1"]) == len(it["p1"]) for p in it["partners"]) and it["X"] not in xs and len(set(xs)) == 3
    pf &= all(p["p1"] != it["p1"] for p in it["partners"]) and all(p["g_mm"] == (p["Xp"] * it["k"] + it["m"]) % 10 and p["g_mm"] != it["ans"] for p in it["partners"])
check(pf, "K=3 wrong-P partners: exactly the same token length, different programs, distinct values of the queried variable (all differ from the true one), implied answers differ from the true answer")
a, b = ns["make_item"](3, 5, "t"), ns["make_item"](3, 5, "t")
check(a["ids_full"] == b["ids_full"] and [p["p1"] for p in a["partners"]] == [p["p1"] for p in b["partners"]], "items and partners are deterministic (seeded)")
nid = ns["note_ids"](a, "7")
check(nid[: a["n_p1"]] == a["p1"] and "computed" in tok.decode(nid[a["n_p1"]:]) and a["xvar"] + " = 7" in tok.decode(nid[a["n_p1"]:]), "text handoff T puts A's value in the tail, after the same P")

# ---- analysis on synthetic records
def pred(d, rng, sharp=3.0):
    z = rng.normal(0, 1, 10); z[d] += sharp
    lp = z - (np.log(np.exp(z - z.max()).sum()) + z.max())
    return {"a": str(int(np.argmax(lp))), "p": [round(float(x), 4) for x in np.exp(lp)], "lp": [round(float(x), 5) for x in lp]}
def synth(kind, n=1500, seed=1):
    rng = np.random.default_rng(seed); ns["RECORDS"].clear(); ns["ITEMS"].clear(); ids = []
    for i in range(n):
        d = [2, 3][i % 2]
        it = ns["make_item"](d, i, "syn") if i < 60 else None
        if it is None:
            base = ns["ITEMS"][ids[i % 60]]
            it = dict(base); it["id"] = f"d{d}:{i}"; it["depth"] = d
        X, k, m, ans = it["X"], it["k"], it["m"], it["ans"]
        belief = X if rng.random() < 0.65 else int(rng.choice([x for x in range(10) if x != X]))     # A's state answer, 65% right
        g = (belief * k + m) % 10
        rec = {"R": pred(int(rng.integers(10)), rng, 0.5), "S_full": pred(ans, rng), "S_state": pred(belief, rng), "T": pred(g, rng)}
        rec["R_state"] = rec["R"]
        if kind == "faithful":      # B reasons from A's belief: answers g
            rec["C"] = pred(g, rng, 2.0)
        elif kind == "generic":      # C is a perturbation of R: ignores the cache content
            rec["C"] = pred(int(rng.integers(10)), rng, 0.5)
        elif kind == "copies_truth":  # C is more accurate but only because the cache carries the true state (not A's wrong belief)
            rec["C"] = pred(ans if rng.random() < 0.3 else int(rng.integers(10)), rng, 2.0)
        for kk in range(3):
            pt = it["partners"][kk]
            rec[f"C_mm{kk}"] = pred(pt["g_mm"] if kind == "faithful" else int(rng.integers(10)), rng, 2.0 if kind == "faithful" else 0.5)
            rec[f"C_mm{kk}"]["g_mm"] = pt["g_mm"]
        iid = it["id"]; ns["ITEMS"][iid] = it; ns["RECORDS"][iid] = rec; ids.append(iid)
    return ids
res = {}
for kind in ("faithful", "generic", "copies_truth"):
    ids = synth(kind); o = ns["analyze_pcs1"](ids); res[kind] = o
    P = o["pooled"]; f = o["fidelity"]
    print(f"      {kind:13s} acc R/Rcal/C/Cmm/T = " + "/".join(f"{P['acc'][k][0]:.2f}" for k in ("R", "Rcal", "C", "C_mm_mean", "T")) + f"  Delta {P['Delta_specific'][0]:+.3f}  C-Rcal {P['C_minus_Rcal'][0]:+.3f}  fidelity excess {f['excess'][0]:+.3f} [{f['excess'][1]:+.3f},{f['excess'][2]:+.3f}] (n wrong belief {f['n']})")
check(res["faithful"]["n_A_wrong_belief"] > 400 and abs(res["faithful"]["n_A_wrong_belief"] / res["faithful"]["n_items"] - 0.35) < 0.05, "wrong-belief set is about 35% of items (synthetic A is 65% right)")
check(res["faithful"]["fidelity"]["excess"][1] > 0.3 and res["faithful"]["reading"].startswith("FIDELITY SUPPORTED") or res["faithful"]["reading"].startswith("NEW DEDUCTION SUPPORTED and FIDELITY"), "faithful scenario: fidelity excess large, reading reports fidelity")
check(res["generic"]["reading"].startswith("NULL") and res["generic"]["fidelity"]["excess"][1] <= 0.0 <= res["generic"]["fidelity"]["excess"][2], "generic-perturbation scenario -> NULL")
o = res["copies_truth"]
check(o["pooled"]["Delta_specific"][1] >= 0.02 and o["pooled"]["C_minus_Rcal"][1] > 0 and o["fidelity"]["excess"][2] < 0.1 and o["reading"].startswith("NEW DEDUCTION SUPPORTED (fidelity not supported)"),
      "C accurate via the true state but not following A's WRONG belief -> new deduction supported, fidelity not")
check(abs(res["faithful"]["fidelity"]["P_C_eq_g"][0] - np.mean([1.0]) ) < 1.01 and res["faithful"]["wrong_cache_following"]["P_Cmm_eq_g_mm_mean"][0] > 0.5, "wrong-cache following statistic is high when C_mm follows the (wrong) cache")
ids = synth("generic"); o = ns["analyze_pcs1"](ids)
W = o["fidelity"]; chance = W["P_C_eq_g_minus_chance"]
check(abs(W["P_C_eq_g"][0] - 0.1) < 0.05 and chance[1] < 0 < chance[2] + 0.06, "generic C sits at the 1/10 chance reference on the wrong-belief set")
# decision rule
def fake(d, dc, f): return {"pooled": {"Delta_specific": d, "C_minus_Rcal": dc}, "fidelity": {"excess": f}}
cases = [("deduction + fidelity", fake((.05, .03, .07), (.04, .01, .07), (.1, .05, .15)), "NEW DEDUCTION SUPPORTED and FIDELITY"),
         ("deduction only (lower CI exactly .02)", fake((.05, .02, .07), (.04, .01, .07), (.0, -.03, .03)), "NEW DEDUCTION SUPPORTED (fidelity not"),
         ("Delta lower .019 -> not deduction; fidelity ok -> fidelity only", fake((.05, .019, .07), (.04, .01, .07), (.1, .05, .15)), "FIDELITY SUPPORTED (new"),
         ("both CIs include 0 -> null", fake((.0, -.01, .01), (.0, -.02, .02), (.0, -.03, .03)), "NULL"),
         ("Delta positive (<.02) but fidelity CI includes 0 -> partial", fake((.01, .003, .017), (.0, -.02, .02), (.0, -.03, .03)), "PARTIAL"),
         ("Delta big but C not above Rcal, fidelity null -> partial", fake((.05, .03, .07), (.0, -.02, .02), (.0, -.03, .03)), "PARTIAL"),
         ("Delta negative CI -> partial", fake((-.03, -.05, -.01), (.0, -.02, .02), (.0, -.03, .03)), "PARTIAL"),
         ("missing -> no claim", fake((float('nan'),) * 3, (0, 0, 0), (0, 0, 0)), "NO CLAIM")]
for name, o_, expect in cases:
    check(ns["reading_pcs1"](o_)[0].startswith(expect), f"rule: {name}")
print("\nRESULT:", "ALL TESTS PASSED" if ok else "FAILURES"); sys.exit(0 if ok else 1)
