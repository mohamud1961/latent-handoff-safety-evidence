#!/usr/bin/env python3
"""POST-HOC checks for PCS1 (not pre-registered). From pcs1/kaggle_out/results.json only.  .venv-smoke/bin/python pcs1/posthoc_pcs1.py"""
import json, numpy as np
from pathlib import Path
rng = np.random.default_rng(0)
r = json.load(open(Path(__file__).parent / "kaggle_out" / "results.json")); rec = r["records"]
ids = [i for i, v in rec.items() if "C" in v and "T" in v and all(f"C_mm{k}" in v for k in range(3))]
get = lambda c: np.array([rec[i][c]["a"] for i in ids])
meta = [rec[i]["_meta"] for i in ids]
ans, X, m = np.array([str(x["ans"]) for x in meta]), np.array([str(x["X"]) for x in meta]), np.array([x["m"] for x in meta])
R, C, T, Ss, Sf = get("R"), get("C"), get("T"), get("S_state"), get("S_full"); Cm = [get(f"C_mm{k}") for k in range(3)]
def ci(x, n=5000):
    x = np.asarray(x, float); b = x[rng.integers(0, len(x), (n, len(x)))].mean(1); return f"{x.mean()*100:5.1f}% [{np.percentile(b,2.5)*100:5.1f},{np.percentile(b,97.5)*100:5.1f}]"
right = Ss == X
print(f"n={len(ids)}  A's belief right on {right.mean()*100:.1f}%")
print("accuracy by A's belief:  T right-belief", ci((T == ans)[right]), "| wrong-belief", ci((T == ans)[~right]))
print("C right-belief", ci((C == ans)[right]), "| C wrong-belief", ci((C == ans)[~right]), "| Rcal-free R right-belief", ci((R == ans)[right]))
print("P(answer == A's state value S_state)  [a copy of A's belief; never the right answer]:")
print("   C", ci((C == Ss)), "| C_mm mean", ci(np.mean([(c == Ss) for c in Cm], axis=0)), "| R", ci(R == Ss), "| T", ci(T == Ss))
print("P(answer == true state X):  C", ci(C == X), "| C_mm mean", ci(np.mean([(c == X) for c in Cm], axis=0)), "| R", ci(R == X))
print("T (text handoff) uses the value: P(T == (S_state+m)%10) =", ci(T == np.array([str((int(s) + mm) % 10) for s, mm in zip(Ss, m)])))
print("C vs R agreement", ci(C == R), "| C vs C_mm0", ci(C == Cm[0]), "(the bridge changes B's answer on ~half the items, and wrong caches change it the same way)")
