#!/usr/bin/env python3
"""Unit test of the analysis code on SYNTHETIC predictions with known ground truth (no models, no network).

Pulls the helper/analysis functions out of the notebook by name (AST) and feeds them fabricated per-item records.
Run 1 tests (kept): Part B inheritance analysis (belief carrier / truth-biased helper / non-specific) and the PREREG.md reading.
Run 2 tests (new, PREREG_run2): label-free cross-fit calibration, calibrated-receiver baseline, mismatched sharer on ALL items,
C vs C_mm answer agreement, the (e) thresholds (content-specific / non-specific / mixed), and the Part A generation-readout
mismatched-control statistics.

Needs numpy + nbformat only:   .venv/bin/python test_analysis.py [notebook]      (default: c2c_fidelity_run2.ipynb)
"""
import ast, random, sys
from pathlib import Path
import numpy as np
import nbformat

NB = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "c2c_fidelity_run2.ipynb"
src = "\n".join(c.source for c in nbformat.read(NB, as_version=4).cells if c.cell_type == "code")
tree = ast.parse(src)
want = {"boot_ci", "boot_ci_unpaired_diff", "fmt", "arrays", "analyze_B", "auto_reading",
        "_lp_vec", "cal_folds", "crossfit_calibrate", "cal_array", "analyze_run2", "auto_reading_run2", "gen_mismatch_stats"}
ns = {"np": np, "random": random, "CFG": {"N_BOOT": 1000, "MIN_CELL": 150, "CAL_SEED": 0}, "LETTERS": "ABCD", "RECORDS": {}, "ITEMS": {}}
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

# ======================================================================================= run 2 tests
print("\n--- run 2 tests: calibration, mismatched sharer on all items, thresholds (PREREG_run2)")
LET = "ABCD"

def mk_pred(z, partner=None):
    """prediction record from raw letter logits z (length 4): argmax, softmax p, log-softmax lp (as the notebook's to_pred)."""
    z = np.asarray(z, float)
    lp = z - (np.log(np.exp(z - z.max()).sum()) + z.max())
    d = {"a": LET[int(np.argmax(lp))], "p": [round(float(x), 4) for x in np.exp(lp)], "lp": [round(float(x), 5) for x in lp]}
    if partner is not None:
        d["partner"] = partner
    return d

BIAS = np.array([2.0, 0.0, 0.0, 0.0])      # receiver's letter-A bias (like the 73% "A" answers in run 1)

def synth_run2(kind, n=2400, seed=1, partner_cov=0.99):
    """Receiver: bias + noise + knowledge (p=0.40). Sharer: knowledge (p=0.45), no bias.
    kind = 'content'      C = debiased receiver + the sharer's answer; C_mm = debiased receiver only      -> content-specific
           'calibration'  C and C_mm both = debiased receiver (+ shared noise); the sharer is ignored      -> non-specific
           'mixed'        C and C_mm both = debiased receiver + a generic boost on what the receiver knows -> C - C_mm ~ 0 but C > calibrated R
    """
    rng = np.random.default_rng(seed)
    ns["RECORDS"].clear(); ns["ITEMS"].clear()
    ids = []
    for i in range(n):
        y = int(rng.integers(4))
        zr = rng.normal(0, 1, 4)                         # receiver item noise (shared with C, C_mm)
        knows = rng.random() < 0.40
        know_r = np.eye(4)[y] * 2.5 if knows else np.zeros(4)
        z_recv = BIAS + zr + know_r
        s_ans = y if rng.random() < 0.45 else int(rng.choice([l for l in range(4) if l != y]))
        z_shar = rng.normal(0, 1, 4) * 0.2 + np.eye(4)[s_ans] * 3.0
        base = zr + know_r                               # debiased receiver evidence
        small = rng.normal(0, 0.05, 4)
        if kind == "content":
            z_c, z_m = base + 1.6 * np.eye(4)[s_ans] + small, base + small
        elif kind == "calibration":
            z_c, z_m = base + small, base - small
        elif kind == "mixed":
            boost = np.eye(4)[y] * 1.2 if knows else np.zeros(4)
            z_c, z_m = base + boost + small, base + boost - small
        else:
            raise ValueError(kind)
        has_partner = rng.random() < partner_cov
        iid = f"i{i}"
        ns["RECORDS"][iid] = {"R": mk_pred(z_recv), "S": mk_pred(z_shar), "S_nat": mk_pred(z_shar), "C": mk_pred(z_c),
                              "C_mm": mk_pred(z_m, partner="p") if has_partner else None, "T": mk_pred(z_shar)}
        ns["ITEMS"][iid] = {"y": LET[y]}
        ids.append(iid)
    return ids

# ---- 1. cross-fit calibration mechanics -------------------------------------------------------------------------------
ids = synth_run2("calibration", n=600)
fold = ns["cal_folds"](ids)
sizes = [sum(1 for v in fold.values() if v == k) for k in (0, 1)]
check(abs(sizes[0] - sizes[1]) <= 1 and sum(sizes) == len(ids), f"2-fold split partitions the items evenly {sizes}")
check(fold == ns["cal_folds"](list(reversed(ids))), "fold assignment is deterministic and independent of the input order")
check(fold != ns["cal_folds"](ids, seed=1), "a different seed gives a different split")

cal = ns["crossfit_calibrate"](ids, "R", fold)
# by-hand check on one item: prior comes from the OTHER fold only
i0 = ids[0]; k0 = fold[i0]
other = [np.array(ns["RECORDS"][j]["R"]["lp"]) for j in ids if fold[j] != k0]
manual = LET[int(np.argmax(np.array(ns["RECORDS"][i0]["R"]["lp"]) - np.mean(other, axis=0)))]
check(cal[i0] == manual, "calibrated answer = argmax(lp - mean lp of the OTHER fold), checked by hand")

# independence from labels
before = dict(cal)
saved = {k: dict(v) for k, v in ns["ITEMS"].items()}
for v in ns["ITEMS"].values():
    v["y"] = "D"
after = ns["crossfit_calibrate"](ids, "R", fold)
ns["ITEMS"].update(saved)
check(before == after, "calibration is label-free (changing every label changes nothing)")

# cross-fit: perturbing another item of the SAME fold cannot change this item's calibrated answer
same = [j for j in ids if fold[j] == k0 and j != i0][0]
saved_rec = ns["RECORDS"][same]["R"]
ns["RECORDS"][same]["R"] = mk_pred([50.0, -50.0, -50.0, -50.0])
same_fold_change = ns["crossfit_calibrate"](ids, "R", fold)
ns["RECORDS"][same]["R"] = saved_rec
check(all(same_fold_change[j] == cal[j] for j in ids if fold[j] == k0 and j != same), "same-fold items never influence each other's prior (cross-fit)")
other_fold_item = [j for j in ids if fold[j] != k0][0]
saved_rec = ns["RECORDS"][other_fold_item]["R"]
ns["RECORDS"][other_fold_item]["R"] = mk_pred([-500.0, 500.0, 500.0, 500.0])
other_fold_change = ns["crossfit_calibrate"](ids, "R", fold)
ns["RECORDS"][other_fold_item]["R"] = saved_rec
check(any(other_fold_change[j] != cal[j] for j in ids if fold[j] == k0), "the prior does come from the other fold (sanity: perturbing it changes answers)")

# removes a constant letter bias: a knowledge-free, A-biased receiver is ~25% raw-A and ~uniform after calibration
rng = np.random.default_rng(3)
ns["RECORDS"].clear(); ns["ITEMS"].clear()
ids_b = []
for i in range(1200):
    ns["RECORDS"][f"b{i}"] = {"R": mk_pred(BIAS * 1.5 + rng.normal(0, 1, 4)), "S": mk_pred(rng.normal(0, 1, 4)), "C": mk_pred(rng.normal(0, 1, 4))}
    ns["ITEMS"][f"b{i}"] = {"y": LET[int(rng.integers(4))]}
    ids_b.append(f"b{i}")
raw_a = np.mean([ns["RECORDS"][i]["R"]["a"] == "A" for i in ids_b])
cal_b = ns["crossfit_calibrate"](ids_b, "R")
cal_a = np.mean([v == "A" for v in cal_b.values()])
check(raw_a > 0.6 and abs(cal_a - 0.25) < 0.06, f"removes a constant letter bias (share of 'A' answers {raw_a:.2f} -> {cal_a:.2f}; chance 0.25)")

# missing / non-finite predictions are skipped, not crashed on
ns["RECORDS"]["b0"]["R"] = {"a": "?", "p": [None] * 4, "lp": [None] * 4}
ns["RECORDS"]["b1"]["R"] = None
skip = ns["crossfit_calibrate"](ids_b, "R")
check("b0" not in skip and "b1" not in skip and len(skip) == len(ids_b) - 2, "items with missing or non-finite predictions are skipped")

# ---- 2. the three scenarios of the (e) table ------------------------------------------------------------------------------
res = {}
for kind, expect in [("content", "CONTENT-SPECIFIC"), ("calibration", "NON-SPECIFIC"), ("mixed", "MIXED")]:
    ids = synth_run2(kind)
    o = ns["analyze_run2"](ids)
    res[kind] = o
    c = o["comparisons"]
    print(f"      {kind:12s} acc R/Rcal/C/Cmm = {o['accuracy_all_point']['R']:.3f}/{o['accuracy_all_point']['Rcal']:.3f}/{o['accuracy_all_point']['C']:.3f}/"
          f"{o['accuracy_partner_subset_point']['C_mm']:.3f}  C-Cmm {c['C_minus_Cmm_all'][0]:+.3f} [{c['C_minus_Cmm_all'][1]:+.3f},{c['C_minus_Cmm_all'][2]:+.3f}]  "
          f"C-Rcal {c['C_minus_Rcal_all'][0]:+.3f} [{c['C_minus_Rcal_all'][1]:+.3f},{c['C_minus_Rcal_all'][2]:+.3f}]")
    check(o["reading_run2"].startswith(expect), f"scenario '{kind}' -> {o['reading_run2'][:34]}")

o = res["calibration"]
check(o["accuracy_all_point"]["Rcal"] > o["accuracy_all_point"]["R"] + 0.05, "calibration lifts a biased receiver (calibrated R > R by > 5 pts)")
check(o["agreement_C_vs_Cmm"]["all"]["same_answer"][0] > 0.95, f"calibration scenario: C and C_mm give the same answer ({o['agreement_C_vs_Cmm']['all']['same_answer'][0]:.2f})")
check(res["content"]["agreement_C_vs_Cmm"]["all"]["same_answer"][0] < 0.85, f"content scenario: C and C_mm disagree more ({res['content']['agreement_C_vs_Cmm']['all']['same_answer'][0]:.2f})")
check(res["content"]["comparisons"]["Ccal_minus_Cmmcal_all"][1] > 0, "content scenario: C - C_mm stays positive after calibrating both")
check(abs(res["calibration"]["comparisons"]["Ccal_minus_Cmmcal_all"][0]) < 0.02, "calibration scenario: calibrated C - calibrated C_mm ~ 0")
check(res["mixed"]["comparisons"]["C_minus_Rcal_all"][1] > 0 and res["mixed"]["reading_flags"]["C_minus_Cmm_CI_includes_0"],
      "mixed scenario: C beats calibrated R but not the wrong-question control")

# ---- 3. C_mm on ALL items: coverage, restriction to items with a partner -----------------------------------------------------
ids = synth_run2("content", partner_cov=0.9)
o = ns["analyze_run2"](ids)
cov = o["partner_coverage_all"]
check(abs(cov - 0.9) < 0.03 and o["n_with_partner"] == round(cov * o["n_items"]), f"partner coverage reported on all items ({cov:.3f}); comparisons use only items with a partner")
check(o["n_with_partner"] > 0.5 * o["n_items"] and o["agreement_C_vs_Cmm"]["all"]["n"] == o["n_with_partner"], "agreement is computed on exactly the items that have a partner")
check(o["agreement_C_vs_Cmm"]["D"]["n"] <= o["n_disagree"], "agreement on D is restricted to D")
cells_n = sum(o["agreement_C_vs_Cmm"][k]["n"] for k in "ABW")
check(cells_n == o["agreement_C_vs_Cmm"]["D"]["n"], "agreement cells A+B+W partition D (items with a partner)")

# thresholds are applied exactly as pre-registered
def fake(d_mm, d_cal):
    return {"comparisons": {"C_minus_Cmm_all": d_mm, "C_minus_Rcal_all": d_cal}}
cases = [("lower CI exactly +0.02 and beats cal -> content", fake((0.05, 0.02, 0.08), (0.04, 0.01, 0.07)), "CONTENT-SPECIFIC"),
         ("lower CI +0.019 -> not content", fake((0.05, 0.019, 0.08), (0.04, 0.01, 0.07)), "MIXED"),
         ("beats C_mm but calibrated R CI includes 0 -> not content", fake((0.05, 0.03, 0.07), (0.04, -0.01, 0.09)), "MIXED"),
         ("C-C_mm CI includes 0 and |C-Rcal| = 0.02 -> non-specific", fake((0.0, -0.01, 0.01), (0.02, 0.0, 0.04)), "NON-SPECIFIC"),
         ("C-C_mm CI includes 0 but C-Rcal = 0.03 -> not non-specific", fake((0.0, -0.01, 0.01), (0.03, 0.01, 0.05)), "MIXED"),
         ("C-C_mm CI excludes 0 negatively, Rcal ties -> mixed", fake((-0.03, -0.05, -0.01), (0.0, -0.02, 0.02)), "MIXED"),
         ("no partner data -> no claim", fake((float('nan'),) * 3, (0.0, -0.02, 0.02)), "NO CLAIM")]
for name, o_, expect in cases:
    r, _ = ns["auto_reading_run2"](o_)
    check(r.startswith(expect), f"threshold: {name}")

# ---- 4. Part A generation readout: mismatched sharer ---------------------------------------------------------------------------
rng = random.Random(5)
n = 400
yv = [rng.choice(LET) for _ in range(n)]
c_gen = [y if rng.random() < 0.55 else rng.choice(LET) for y in yv]
m_gen = [c if rng.random() < 0.9 else rng.choice(LET) for c in c_gen]       # mismatched run mostly reproduces C
r_gen = [y if rng.random() < 0.35 else rng.choice(LET) for y in yv]
has_mm = [rng.random() < 0.97 for _ in range(n)]
m_gen = [m if h else None for m, h in zip(m_gen, has_mm)]
m_gen[3] = None; has_mm[3] = True                                           # one unparsed C_mm output on an item with a partner
g = ns["gen_mismatch_stats"](c_gen, m_gen, r_gen, yv, has_mm)
idx = [i for i in range(n) if has_mm[i]]
exp_c = np.mean([c_gen[i] == yv[i] for i in idx]); exp_m = np.mean([m_gen[i] == yv[i] for i in idx])
exp_agree = np.mean([m_gen[i] is not None and c_gen[i] == m_gen[i] for i in idx])
check(g["n_with_partner"] == len(idx) and abs(g["acc_point"]["C"] - exp_c) < 1e-12 and abs(g["acc_point"]["C_mm"] - exp_m) < 1e-12, "gen readout: accuracies on the partner subset match a hand computation")
check(abs(g["agreement_C_vs_C_mm"][0] - exp_agree) < 1e-12 and g["unparsed_C_mm"] == 1, f"gen readout: agreement {g['agreement_C_vs_C_mm'][0]:.3f} and unparsed C_mm count are right")
check(abs(g["C_minus_C_mm_ci"][0] - (exp_c - exp_m)) < 1e-12 and g["C_minus_C_mm_ci"][1] <= g["C_minus_C_mm_ci"][0] <= g["C_minus_C_mm_ci"][2], "gen readout: paired C - C_mm difference and CI bracket")

print("\nRESULT:", "ALL TESTS PASSED" if ok else "FAILURES")
sys.exit(0 if ok else 1)
