#!/usr/bin/env python3
"""Run-3 unit test of the analysis code on SYNTHETIC predictions with known ground truth (no models, no network).
Covers: K=3 wrong-question controls (Delta_specific, per-k agreement, spread), calibrated receiver, the numeric-task statistics
(exact-match, numeric inheritance, leak check), and the PREREG_run3 decision rule (content-specific / partial / non-specific / mixed).
Run-1/run-2 checks that still apply are kept.

Pulls the helper/analysis functions out of the notebook by name (AST) and feeds them fabricated per-item records.
Run 1 tests (kept): Part B inheritance analysis (belief carrier / truth-biased helper / non-specific) and the PREREG.md reading.
Run 2 tests (new, PREREG_run2): label-free cross-fit calibration, calibrated-receiver baseline, mismatched sharer on ALL items,
C vs C_mm answer agreement, the (e) thresholds (content-specific / non-specific / mixed), and the Part A generation-readout
mismatched-control statistics.

Needs numpy + nbformat only:   .venv/bin/python test_analysis.py [notebook]      (default: c2c_fidelity_run3.ipynb)
"""
import ast, random, sys
from pathlib import Path
import numpy as np
import nbformat

NB = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "c2c_fidelity_run3.ipynb"
src = "\n".join(c.source for c in nbformat.read(NB, as_version=4).cells if c.cell_type == "code")
tree = ast.parse(src)
want = {"boot_ci", "boot_ci_unpaired_diff", "fmt", "arrays", "analyze_B", "auto_reading",
        "_lp_vec", "cal_folds", "crossfit_calibrate", "cal_array", "analyze_run3", "auto_reading_run3", "gen_mismatch_stats",
        "analyze_numeric", "numeq"}
ns = {"np": np, "random": random, "CFG": {"N_BOOT": 1000, "MIN_CELL": 150, "CAL_SEED": 0, "K_MM": 3}, "LETTERS": "ABCD", "RECORDS": {}, "ITEMS": {}}
for n in tree.body:
    if isinstance(n, ast.FunctionDef) and n.name in want:
        exec(compile(ast.Module([n], []), "nb", "exec"), ns)
missing = want - {k for k in ns if k in want}
assert not missing, missing

ok = True
def check(good, msg):
    global ok
    ok &= bool(good)
    print(f"{'PASS' if good else 'FAIL'}  {msg}")

# ======================================================================================= run 1 tests (unchanged logic)
def pred(a):
    return {"a": a, "p": [0.25] * 4}

def scenario(name, c_rule, n=2500, seed=0):
    rng = random.Random(seed)
    ns["RECORDS"].clear(); ns["ITEMS"].clear()
    ids = []
    for i in range(n):
        y = rng.choice("ABCD")
        wrong = [l for l in "ABCD" if l != y]
        r = y if rng.random() < 0.40 else rng.choice(wrong)       # receiver 40%
        s = y if rng.random() < 0.45 else rng.choice(wrong)       # sharer 45%
        c, c_mm = c_rule(rng, y, r, s)
        rec = {"R": pred(r), "S": pred(s), "S_nat": pred(s), "C": pred(c), "C_mm": {**pred(c_mm), "partner": "none"},
               "T": pred(s if rng.random() < 0.7 else r)}
        ns["RECORDS"][f"i{i}"] = rec
        ns["ITEMS"][f"i{i}"] = {"y": y}
        ids.append(f"i{i}")
    return ns["analyze_B"](ids)

def noise(rng, y, r, s):   # generic perturbation: moves away from the receiver's answer 25% of the time, to a random letter
    return rng.choice("ABCD") if rng.random() < 0.25 else r

def belief_carrier(rng, y, r, s):
    c = s if (s != r and rng.random() < 0.55) else noise(rng, y, r, s)
    return c, noise(rng, y, r, s)

def truth_biased(rng, y, r, s):
    c = s if (s == y and s != r and rng.random() < 0.55) else noise(rng, y, r, s)
    return c, noise(rng, y, r, s)

def nonspecific(rng, y, r, s):
    return noise(rng, y, r, s), noise(rng, y, r, s)

print("--- run 1 tests: Part B inheritance analysis (PREREG.md decision table)")
for name, rule, expect in [("belief carrier", belief_carrier, "BELIEF TRANSFER"),
                           ("truth-biased helper", truth_biased, "TRUTH-BIASED HELPER"),
                           ("non-specific perturbation", nonspecific, "NON-SPECIFIC PERTURBATION")]:
    out = scenario(name, rule)
    B, A = out["inheritance"]["B"], out["inheritance"]["A"]
    good = out["reading"].startswith(expect)
    ok &= good
    print(f"{'PASS' if good else 'FAIL'}  {name:28s} cells={out['cell_sizes']}  E_B={out['inheritance']['B']['E_excess'][0]:+.3f}  "
          f"E_A={A['E_excess'][0]:+.3f}  ->  {out['reading'][:42]}")

tot = out["cell_sizes"]["A"] + out["cell_sizes"]["B"] + out["cell_sizes"]["W"]
check(tot == out["n_disagree"] and out["cell_sizes"]["B+W"] == out["cell_sizes"]["B"] + out["cell_sizes"]["W"],
      f"A+B+W partition D ({tot} == {out['n_disagree']})")
m, lo, hi = ns["boot_ci"](np.array([1, 0, 1, 1, 0, 1] * 50))
check(abs(m - 2 / 3) < 1e-9 and lo < m < hi, f"bootstrap CI brackets the mean ({m:.3f} [{lo:.3f},{hi:.3f}])")

# ======================================================================================= run 3 tests
print("\n--- run 3 tests: K wrong states, calibration, numeric task, decision rule (PREREG_run3)")
LET = "ABCD"
K = 3

def mk_pred(z, partner=None):
    z = np.asarray(z, float)
    lp = z - (np.log(np.exp(z - z.max()).sum()) + z.max())
    d = {"a": LET[int(np.argmax(lp))], "p": [round(float(x), 4) for x in np.exp(lp)], "lp": [round(float(x), 5) for x in lp]}
    if partner is not None:
        d["partner"] = partner
    return d

BIAS = np.array([2.0, 0.0, 0.0, 0.0])

def synth(kind, n=2400, seed=1, partner_p=(0.0, 0.01, 0.03)):
    """Receiver: A-bias + noise + knowledge (p=0.40). Sharer: knowledge (p=0.45).
    content: C = debiased receiver + sharer answer; every C_mm,k = debiased receiver only.
    calibration: C and all C_mm,k = debiased receiver (+ independent tiny noise).
    partial: C = debiased receiver + a weak sharer pull (small, real).
    one_bad_state: like calibration, but wrong state k=2 is strongly harmful (spread across k)."""
    rng = np.random.default_rng(seed)
    ns["RECORDS"].clear(); ns["ITEMS"].clear()
    ids = []
    for i in range(n):
        y = int(rng.integers(4))
        zr = rng.normal(0, 1, 4)
        knows = rng.random() < 0.40
        know_r = np.eye(4)[y] * 2.5 if knows else np.zeros(4)
        z_recv = BIAS + zr + know_r
        s_ans = y if rng.random() < 0.45 else int(rng.choice([l for l in range(4) if l != y]))
        z_shar = rng.normal(0, 1, 4) * 0.2 + np.eye(4)[s_ans] * 3.0
        base = zr + know_r
        pull = {"content": 1.6, "partial": 0.30}.get(kind, 0.0)
        z_c = base + pull * np.eye(4)[s_ans] + rng.normal(0, 0.05, 4)
        rec = {"R": mk_pred(z_recv), "S": mk_pred(z_shar), "S_nat": mk_pred(z_shar), "C": mk_pred(z_c), "T": mk_pred(z_shar)}
        n_have = int(rng.choice([0, 1, 2, 3], p=[partner_p[0], partner_p[1], partner_p[2], 1 - sum(partner_p)]))
        for k in range(K):
            zm = base + rng.normal(0, 0.05, 4)
            if kind == "one_bad_state" and k == 2:
                zm = zm - 1.5 * np.eye(4)[y] * (1.0 if knows else 0.0)
            rec[f"C_mm{k}"] = mk_pred(zm, partner=f"p{k}") if k < n_have else None
        rec["C_mm"] = rec["C_mm0"]
        iid = f"i{i}"
        ns["RECORDS"][iid] = rec
        ns["ITEMS"][iid] = {"y": LET[y]}
        ids.append(iid)
    return ids

# ---- 1. cross-fit calibration mechanics (unchanged behaviour from run 2)
ids = synth("calibration", n=600)
fold = ns["cal_folds"](ids)
sizes = [sum(1 for v in fold.values() if v == k) for k in (0, 1)]
check(abs(sizes[0] - sizes[1]) <= 1 and sum(sizes) == len(ids), f"2-fold split partitions the items evenly {sizes}")
cal = ns["crossfit_calibrate"](ids, "R", fold)
i0 = ids[0]; k0 = fold[i0]
other = [np.array(ns["RECORDS"][j]["R"]["lp"]) for j in ids if fold[j] != k0]
manual = LET[int(np.argmax(np.array(ns["RECORDS"][i0]["R"]["lp"]) - np.mean(other, axis=0)))]
check(cal[i0] == manual, "calibrated answer = argmax(lp - mean lp of the OTHER fold), checked by hand")
saved = {k: dict(v) for k, v in ns["ITEMS"].items()}
for v in ns["ITEMS"].values():
    v["y"] = "D"
check(ns["crossfit_calibrate"](ids, "R", fold) == cal, "calibration is label-free")
ns["ITEMS"].update(saved)

# ---- 2. scenarios of the MC rule
res = {}
for kind in ("content", "calibration", "partial", "one_bad_state"):
    ids = synth(kind)
    o = ns["analyze_run3"](ids)
    res[kind] = o
    c = o["comparisons"]
    print(f"      {kind:14s} acc R/Rcal/C/meanCmm = {o['accuracy_all_point']['R']:.3f}/{o['accuracy_all_point']['Rcal']:.3f}/{o['accuracy_all_point']['C']:.3f}/{o['accuracy_K_complete_point']['mean_C_mm']:.3f}"
          f"  Delta {c['Delta_specific'][0]:+.3f} [{c['Delta_specific'][1]:+.3f},{c['Delta_specific'][2]:+.3f}]  C-Rcal {c['C_minus_Rcal_all'][0]:+.3f} [{c['C_minus_Rcal_all'][1]:+.3f},{c['C_minus_Rcal_all'][2]:+.3f}]  Kcomplete {o['n_K_complete']}/{o['n_items']}")
check(res["content"]["reading_mc_only"].startswith("PARTIAL") and res["content"]["reading_flags_mc"]["Delta_lowerCI>=+0.02"],
      "content scenario: MC criteria met; without numeric corroboration the rule returns PARTIAL (not CONTENT-SPECIFIC)")
check(res["calibration"]["reading_mc_only"].startswith("NON-SPECIFIC"), "calibration scenario -> NON-SPECIFIC")
check(res["partial"]["comparisons"]["Delta_specific"][1] > 0 and res["partial"]["comparisons"]["Delta_specific"][1] < 0.02 and res["partial"]["reading_mc_only"].startswith("PARTIAL"),
      "partial scenario: 0 < lower CI of Delta < +0.02 -> PARTIAL")
o = res["calibration"]
check(abs(o["comparisons"]["Delta_specific"][0]) < 0.01 and o["comparisons"]["Delta_specific_cal"][1] <= 0 <= o["comparisons"]["Delta_specific_cal"][2], "calibration scenario: Delta ~ 0 raw and calibrated")
check(o["accuracy_all_point"]["Rcal"] > o["accuracy_all_point"]["R"] + 0.05, "calibration lifts a biased receiver")
check(all(p_["agreement_all"]["same_answer"][0] > 0.95 for p_ in o["per_k"]), "calibration scenario: C agrees with every C_mm,k (> 95%)")
check(all(p_["agreement_all"]["same_answer"][0] < 0.85 for p_ in res["content"]["per_k"]), "content scenario: C disagrees with every C_mm,k more")
ob = res["one_bad_state"]
sp = ob["spread_across_k"]
check(sp["acc_C_mm_range"] > 0.05 and sp["acc_C_mm_points"][2] == min(sp["acc_C_mm_points"]), f"spread across k exposes the one harmful wrong state (range {sp['acc_C_mm_range']:.3f})")
check(ob["comparisons"]["C_minus_Cmm2_all"][0] > ob["comparisons"]["C_minus_Cmm0_all"][0] + 0.05, "per-k differences are reported separately")
check(abs(ob["comparisons"]["Delta_specific"][0] - np.mean([ob["comparisons"][f"C_minus_Cmm{k}_all"][0] for k in range(K)])) < 1e-9, "Delta_specific equals the mean over k of the per-k differences")
check(abs(sp["acc_C_mm_sd"] - np.std(sp["acc_C_mm_points"])) < 1e-12 and len(sp["wrong_states_pairwise_same_answer"]) == 3, "spread statistics (sd, 3 pairwise agreements)")

# ---- 3. K-complete restriction and coverage
o = res["content"]
cov = o["coverage_K_all"]
check(0.9 < cov < 1.0 and o["n_K_complete"] == round(cov * o["n_items"]) and o["coverage_any_partner"] > cov, f"K-complete coverage reported ({cov:.3f}); any-partner coverage is higher ({o['coverage_any_partner']:.3f})")
check(all(p_["agreement_all"]["n"] == o["n_K_complete"] for p_ in o["per_k"]), "every per-k comparison uses exactly the K-complete items")
check(o["n_K_complete_D"] <= o["n_disagree"], "D restriction")

# ---- 4. decision rule (thresholds applied as pre-registered)
def fake(d, dc, numv="unavailable", ncd=None):
    mc = {"comparisons": {"Delta_specific": d, "C_minus_Rcal_all": dc}}
    num = {"verdict": numv, "n": 150, "C_minus_Cmm_ci": ncd or (0.0, -0.05, 0.05)}
    return mc, num
cases = [
 ("specific MC + numeric positive", fake((0.05, 0.03, 0.07), (0.04, 0.01, 0.07), "positive", (0.06, 0.01, 0.11)), "CONTENT-SPECIFIC"),
 ("lower CI exactly +0.02, beats calR, numeric positive", fake((0.05, 0.02, 0.08), (0.04, 0.01, 0.07), "positive"), "CONTENT-SPECIFIC"),
 ("lower CI +0.019, numeric positive -> partial", fake((0.05, 0.019, 0.08), (0.04, 0.01, 0.07), "positive"), "PARTIAL"),
 ("specific MC, numeric null -> partial (tasks disagree)", fake((0.05, 0.03, 0.07), (0.04, 0.01, 0.07), "null"), "PARTIAL"),
 ("specific MC, numeric negative -> partial", fake((0.05, 0.03, 0.07), (0.04, 0.01, 0.07), "negative"), "PARTIAL"),
 ("specific MC, numeric not run -> partial", fake((0.05, 0.03, 0.07), (0.04, 0.01, 0.07), "unavailable"), "PARTIAL"),
 ("0 < lower CI < 0.02 -> partial", fake((0.012, 0.003, 0.021), (0.0, -0.02, 0.02), "null"), "PARTIAL"),
 ("Delta >= +0.02 lower CI but C not above calibrated R -> partial", fake((0.05, 0.03, 0.07), (0.0, -0.02, 0.02), "null"), "PARTIAL"),
 ("non-specific MC but numeric positive -> partial", fake((0.0, -0.01, 0.01), (0.01, -0.01, 0.03), "positive"), "PARTIAL"),
 ("non-specific: CI includes 0, |C-Rcal| = 0.02", fake((0.0, -0.01, 0.01), (0.02, 0.0, 0.04), "null"), "NON-SPECIFIC"),
 ("non-specific with numeric negative / unavailable", fake((0.0, -0.01, 0.01), (-0.01, -0.03, 0.01), "negative"), "NON-SPECIFIC"),
 ("CI includes 0 but C-Rcal = 0.03 -> mixed", fake((0.0, -0.01, 0.01), (0.03, 0.01, 0.05), "null"), "MIXED"),
 ("Delta CI excludes 0 negatively -> mixed", fake((-0.03, -0.05, -0.01), (0.0, -0.02, 0.02), "null"), "MIXED"),
 ("no wrong-state data -> no claim", fake((float('nan'),) * 3, (0.0, -0.02, 0.02), "null"), "NO CLAIM")]
for name, (mc, num), expect in cases:
    r, _ = ns["auto_reading_run3"](mc, num)
    check(r.startswith(expect), f"rule: {name}")
r, _ = ns["auto_reading_run3"](*fake((0.012, 0.003, 0.021), (0.0, -0.02, 0.02), "null", (0.01, -0.03, 0.05)))
check("+0.012" in r and "numeric C - C_mm +0.010" in r, "PARTIAL reading states the magnitudes")
# full path: content scenario + numeric positive -> CONTENT-SPECIFIC
r, fl = ns["auto_reading_run3"](res["content"], {"verdict": "positive", "n": 200, "C_minus_Cmm_ci": (0.08, 0.02, 0.14)})
check(r.startswith("CONTENT-SPECIFIC") and fl["C_beats_calibratedR_lowerCI>0"], "content scenario + numeric positive -> CONTENT-SPECIFIC")
r, _ = ns["auto_reading_run3"](res["calibration"], {"verdict": "null", "n": 200, "C_minus_Cmm_ci": (0.0, -0.05, 0.05)})
check(r.startswith("NON-SPECIFIC"), "calibration scenario + numeric null -> NON-SPECIFIC")

# ---- 5. numeric task statistics
rng = np.random.default_rng(7)
def numeric_rows(n=300, c_follows_s=0.0, leak=0.0, c_better=0.0, m_noise=0.0, seed=7):
    rng = np.random.default_rng(seed)
    rows = []
    gold = rng.integers(1, 200, n).astype(float)
    snum = np.where(rng.random(n) < 0.55, gold, rng.integers(1, 200, n).astype(float))   # sharer right 55%
    for i in range(n):
        g = gold[i]
        r_ok = rng.random() < 0.40
        rn = g if r_ok else float(rng.integers(1, 200))
        cn = rn
        if rng.random() < c_better and not r_ok:
            cn = g
        if rng.random() < c_follows_s:
            cn = snum[i]
        mn = rn if rng.random() >= m_noise else float(rng.integers(1, 200))
        rows.append(dict(gold=g, num={"R": rn, "S": snum[i], "C": cn, "M": mn}, ok={"R": rn == g, "S": snum[i] == g, "C": cn == g, "M": mn == g},
                         partner_S_num=None, partner_S_ok=False, ctrl_S_num=None))
    for i, r in enumerate(rows):
        p = rows[(i + 1) % n]; c = rows[(i + 7) % n]
        r["partner_S_num"], r["partner_S_ok"], r["ctrl_S_num"] = p["num"]["S"], p["ok"]["S"], c["num"]["S"]
        if rng.random() < leak:
            r["num"]["M"] = p["num"]["S"]; r["ok"]["M"] = r["num"]["M"] == r["gold"]
    return rows
a0 = ns["analyze_numeric"](numeric_rows())
check(a0["n"] == 300 and a0["verdict"] in ("null", "negative") and abs(a0["inheritance"]["S_wrong"]["excess"][0]) < 0.08, f"numeric null scenario: verdict {a0['verdict']}, inheritance excess ~ 0")
a1 = ns["analyze_numeric"](numeric_rows(c_better=0.5, m_noise=0.1, seed=8))
check(a1["verdict"] == "positive" and a1["C_minus_M_ci"][1] > 0, f"numeric scenario where C is better than C_mm: verdict {a1['verdict']} ({a1['C_minus_M']})")
a2 = ns["analyze_numeric"](numeric_rows(c_follows_s=0.4, seed=9))
check(a2["inheritance"]["S_wrong"]["excess"][1] > 0.15 and a2["inheritance"]["S_wrong"]["n"] > 50, f"numeric inheritance detects a bridge that copies the sharer's wrong number ({ns['fmt'](a2['inheritance']['S_wrong']['excess'])})")
a3 = ns["analyze_numeric"](numeric_rows(leak=0.5, seed=10))
check(a3["leak"]["all"]["excess"][1] > 0.2 and a0["leak"]["all"]["excess"][1] <= 0.05, f"leak check: C_mm copying the PARTNER's sharer number is flagged ({ns['fmt'](a3['leak']['all']['excess'])}), none in the null")
check(ns["analyze_numeric"](numeric_rows(n=40))["verdict"] == "unavailable", "N < 60 -> numeric verdict unavailable")
check(ns["numeq"](18.0, 18.0) and not ns["numeq"](18.0, 19.0) and not ns["numeq"](None, 18.0) and ns["numeq"](5.5, 5.5000001), "numeq tolerance and None handling")
rows_small = numeric_rows(n=100)
for r in rows_small[:10]:
    r["num"]["C"] = None
a4 = ns["analyze_numeric"](rows_small)
check(a4["no_number_extracted"]["C"] == 10, "unparsed outputs are counted, not crashed on")

# ---- 6. real extractor / grader (only if math_verify and the C2C clone are importable)
try:
    sys.path.insert(0, str(Path(__file__).parent / "C2C"))
    from math_verify import parse as mv_parse, ExprExtractionConfig, LatexExtractionConfig
    from latex2sympy2_extended import NormalizationConfig
    from rosetta.utils.matheval import GSM8KEvaluator
    GSM = GSM8KEvaluator()
    tree_ = ast.parse(src)
    ns2 = {"re": __import__("re"), "mv_parse": mv_parse, "ExprExtractionConfig": ExprExtractionConfig, "LatexExtractionConfig": LatexExtractionConfig, "NormalizationConfig": NormalizationConfig, "GSM": GSM}
    for n_ in tree_.body:
        if isinstance(n_, ast.FunctionDef) and n_.name in ("extract_number", "is_correct"):
            exec(compile(ast.Module([n_], []), "nb", "exec"), ns2)
    samples = [("So 3+4=7.\n\nAnswer: 7", "7", 7.0), ("Answer: $1,200", "1200", 1200.0), ("\\boxed{72}", "72", 72.0), ("Answer: 5.50", "5.5", 5.5), ("Answer: 18 dollars", "18", 18.0)]
    good = all(ns2["extract_number"](s) == num and ns2["is_correct"](s, g) for s, g, num in samples) and ns2["extract_number"]("no digits here") is None and not ns2["is_correct"]("no digits here", "3") and not ns2["is_correct"]("Answer: 8", "7")
    check(good, "extract_number / is_correct agree with C2C's GSM8KEvaluator on formats it accepts (and reject wrong / missing answers)")
except Exception as e_:
    print("SKIP  real extractor test (math_verify / C2C clone not importable):", repr(e_)[:100])

# ---- 7. Part A generation readout: mismatched sharer stats (unchanged)
rng = random.Random(5)
n = 400
yv = [rng.choice(LET) for _ in range(n)]
c_gen = [y if rng.random() < 0.55 else rng.choice(LET) for y in yv]
m_gen = [c if rng.random() < 0.9 else rng.choice(LET) for c in c_gen]
r_gen = [y if rng.random() < 0.35 else rng.choice(LET) for y in yv]
has_mm = [rng.random() < 0.97 for _ in range(n)]
m_gen = [m if h else None for m, h in zip(m_gen, has_mm)]
m_gen[3] = None; has_mm[3] = True
g = ns["gen_mismatch_stats"](c_gen, m_gen, r_gen, yv, has_mm)
idx = [i for i in range(n) if has_mm[i]]
exp_agree = np.mean([m_gen[i] is not None and c_gen[i] == m_gen[i] for i in idx])
check(g["n_with_partner"] == len(idx) and abs(g["agreement_C_vs_C_mm"][0] - exp_agree) < 1e-12 and g["unparsed_C_mm"] == 1, "gen readout mismatched-sharer statistics match a hand computation")

print("\nRESULT:", "ALL TESTS PASSED" if ok else "FAILURES")
sys.exit(0 if ok else 1)
