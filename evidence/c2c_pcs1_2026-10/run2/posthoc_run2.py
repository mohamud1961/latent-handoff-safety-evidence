#!/usr/bin/env python3
"""POST-HOC checks for run 2 (not pre-registered). Reads kaggle_out/results.json only; no models, no network.
Reuses the notebook's own helper functions (AST-extracted) so calibrated numbers tie out to the pre-registered ones.
    ../.venv-smoke/bin/python posthoc_run2.py        (numpy + nbformat)
"""
import ast, json, random, sys
from collections import Counter
from pathlib import Path
import numpy as np
import nbformat

HERE = Path(__file__).parent
R_ = json.load(open(HERE / "kaggle_out" / "results.json"))
REC = R_["records"]
src = "\n".join(c.source for c in nbformat.read(HERE / "c2c_fidelity_run2.ipynb", as_version=4).cells if c.cell_type == "code")
want = {"boot_ci", "fmt", "arrays", "_lp_vec", "cal_folds", "crossfit_calibrate", "cal_array"}
ns = {"np": np, "random": random, "CFG": {"N_BOOT": 10000, "MIN_CELL": 150, "CAL_SEED": 0}, "LETTERS": "ABCD",
      "RECORDS": REC, "ITEMS": {i: {"y": r["_meta"]["y"]} for i, r in REC.items()}}
for n in ast.parse(src).body:
    if isinstance(n, ast.FunctionDef) and n.name in want:
        exec(compile(ast.Module([n], []), "nb", "exec"), ns)
boot_ci, fmt, arrays, cal_array, cal_folds = (ns[k] for k in ("boot_ci", "fmt", "arrays", "cal_array", "cal_folds"))

ids = sorted(i for i in REC if all(k in REC[i] for k in ("R", "S", "C")))
y = np.array([REC[i]["_meta"]["y"] for i in ids])
bench = np.array([REC[i]["_meta"]["bench"] for i in ids])
fold = cal_folds(ids)
R, S, C, Cm = (arrays(ids, k) for k in ("R", "S", "C", "C_mm"))
Rcal, Ccal, Cmcal = (cal_array(ids, k, fold) for k in ("R", "C", "C_mm"))
ok = (R != "?") & (S != "?") & (C != "?")
hm = ~np.isin(Cm, ["", "?"]); okm = ok & hm
D = ok & (S != R)
corr = lambda a: (a == y).astype(float)
print("tie-out with the notebook's pre-registered numbers: acc R %.4f Rcal %.4f C %.4f Ccal %.4f (n=%d)" % (corr(R)[ok].mean(), corr(Rcal)[ok].mean(), corr(C)[ok].mean(), corr(Ccal)[ok].mean(), ok.sum()))

print("\n[P1] accuracy by benchmark (all scored items; C_mm on items with a partner)")
print(f"{'bench':6s} {'n':>5s} {'R':>6s} {'Rcal':>6s} {'S':>6s} {'C':>6s} {'C_mm':>6s} {'Ccal':>6s}   C-R [95% CI]            C-Cmm [95% CI]")
for b in ("mmlu", "arc", "obqa"):
    m = ok & (bench == b); mm = m & hm
    cr = boot_ci((corr(C) - corr(R))[m]); cc = boot_ci((corr(C) - corr(Cm))[mm])
    print(f"{b:6s} {m.sum():5d} " + " ".join(f"{corr(a)[m].mean()*100:6.1f}" for a in (R, Rcal, S, C)) + f" {corr(Cm)[mm].mean()*100:6.1f} {corr(Ccal)[m].mean()*100:6.1f}   {fmt(cr)}   {fmt(cc)}")

print("\n[P2] where does C2C lose accuracy? letter shift")
true_share = Counter(y[ok]); n = ok.sum()
print("true-letter share :", {l: round(true_share[l] / n, 3) for l in "ABCD"})
for nm, a in (("R", R), ("Rcal", Rcal), ("S", S), ("C", C), ("C_mm", Cm), ("Ccal", Ccal)):
    m = ok if nm != "C_mm" else okm
    print(f"{nm:5s} answer share:", {l: round(float((a[m] == l).mean()), 3) for l in "ABCD"})
print("accuracy by TRUE letter (R -> C):", {l: f"{corr(R)[ok & (y == l)].mean()*100:.0f}->{corr(C)[ok & (y == l)].mean()*100:.0f}" for l in "ABCD"})
print("(calibrated)               (Rcal -> Ccal):", {l: f"{corr(Rcal)[ok & (y == l)].mean()*100:.0f}->{corr(Ccal)[ok & (y == l)].mean()*100:.0f}" for l in "ABCD"})

print("\n[P3] how much of what C2C changes is independent of the sharer's content?")
ch = ok & (C != R)
print(f"C != R on {ch.mean()*100:.1f}% of items ({ch.sum()}); of those, with a partner: C_mm gives the SAME changed answer on {((C == Cm)[ch & hm]).mean()*100:.1f}%")
only = okm & (C != Cm)
print(f"C != C_mm on {only.sum()} items ({only.sum()/okm.sum()*100:.1f}% of items with a partner):  acc(C) {corr(C)[only].mean()*100:.1f}% vs acc(C_mm) {corr(Cm)[only].mean()*100:.1f}%;  "
      f"C moves onto S's answer on {int(((C == S) & (Cm != S))[only].sum())} items, C_mm onto S's on {int(((Cm == S) & (C != S))[only].sum())}")
print("   sign test, items where exactly one of C / C_mm is correct: C right", int(((C == y) & (Cm != y))[okm].sum()), "| C_mm right", int(((Cm == y) & (C != y))[okm].sum()))

print("\n[P4] calibration: accuracy-after-calibration comparisons on D (S != R) and all items (paired 95% CI)")
for nm, a, b_, m in (("Ccal - Rcal, all", Ccal, Rcal, ok), ("Ccal - Rcal, D", Ccal, Rcal, D), ("Ccal - Cmmcal, D", Ccal, Cmcal, D & hm),
                     ("Ccal - Cmmcal, all", Ccal, Cmcal, okm), ("Ccal - R, all", Ccal, R, ok), ("S - R, all", S, R, ok)):
    print(f"  {nm:20s} {fmt(boot_ci((corr(a) - corr(b_))[m]))}")
print("  note: S (sharer alone) is not calibrated here; Scal:", f"{corr(cal_array(ids, 'S', fold))[ok].mean()*100:.1f}%")

print("\n[P5] disagreement-set composition under the two receivers")
cells = {"A (S right, R wrong)": D & (S == y), "B (S wrong, R right)": D & (S != y) & (R == y), "W (both wrong)": D & (S != y) & (R != y)}
for k, m in cells.items():
    print(f"  {k:22s} n={m.sum():4d}   acc(C) {corr(C)[m].mean()*100:5.1f}%  acc(C_mm) {corr(Cm)[m & hm].mean()*100:5.1f}%  Inh(C) {((C == S)[m]).mean()*100:5.1f}%  Inh(C_mm) {((Cm == S)[m & hm]).mean()*100:5.1f}%")

print("\n[P6] comparison with run 1 on the items both runs scored (different receiver / sharer / fuser, so descriptive only)")
p1 = HERE.parent / "kaggle_out" / "results.json"
if p1.exists():
    r1 = json.load(open(p1))["records"]
    common = [i for i in ids if i in r1 and "C" in r1[i] and "R" in r1[i]]
    yy = np.array([REC[i]["_meta"]["y"] for i in common])
    g = lambda recs, k: np.array([recs[i][k]["a"] for i in common])
    print(f"  common items: {len(common)}")
    for nm, recs in (("run 1 (0.6B <- 0.5B)", r1), ("run 2 (1.7B <- 1.5B)", REC)):
        r_, c_, s_ = g(recs, "R"), g(recs, "C"), g(recs, "S")
        d = ((c_ == yy).astype(float) - (r_ == yy).astype(float))
        print(f"  {nm}: R {np.mean(r_ == yy)*100:.1f}%  S {np.mean(s_ == yy)*100:.1f}%  C {np.mean(c_ == yy)*100:.1f}%   C-R {fmt(boot_ci(d))}")
    for nm, recs in (("run 1", r1), ("run 2", REC)):
        c_, r_ = g(recs, "C"), g(recs, "R")
        print(f"  {nm}: share of 'A' answers  R {np.mean(r_ == 'A')*100:.0f}%  C {np.mean(c_ == 'A')*100:.0f}%")
