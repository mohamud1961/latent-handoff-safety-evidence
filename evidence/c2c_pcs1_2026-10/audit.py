#!/usr/bin/env python3
"""Independent audit of the C2C fidelity runs (1-3) and PCS1, from the sealed raw per-item outputs.

Standard library only. Run from this folder:  python3 audit.py > AUDIT_OUTPUT.txt
It (1) checks every raw results.json.gz against the sha256 recorded at custody time, (2) recomputes the headline
numbers directly from per-item records (not from the notebooks' summaries), and (3) adds the paired statistics
requested in PCS_C2C_PCS1_INDEPENDENT_REVIEW_AND_NEXT_GATE_2026-10-02.md for run 3: paired bootstrap CIs,
exact McNemar tests vs each wrong-state control, flip tables, and splits.

Calibration here is an independent re-implementation (label-free per-letter mean log-prob prior, 2-fold cross-fit,
folds from random.Random("audit:calfold")), so it can differ slightly from the notebooks' own fold assignment.
"""
import gzip, hashlib, json, math, random
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = {  # sealed file -> path of the original in the work folder, as recorded in RAW_RESULTS_ORIGINAL_SHA256.txt
    "run1/results.json.gz": "kaggle_out/results.json",
    "run2/results.json.gz": "run2/kaggle_out/results.json",
    "run3/results.json.gz": "run3/kaggle_out/results.json",
    "pcs1_pilot_v1/results.json.gz": "pcs1_pilot/kaggle_out_v1/results.json",
    "pcs1_pilot_v2/results.json.gz": "pcs1_pilot/kaggle_out/results.json",
    "pcs1/results.json.gz": "pcs1/kaggle_out/results.json",
}
LETTERS = "ABCD"
N_BOOT = 10000


def load(sealed):
    data = gzip.open(HERE / sealed, "rb").read()
    return hashlib.sha256(data).hexdigest(), json.loads(data)


def boot_ci(diffs, seed=0):
    n = len(diffs)
    rng = random.Random(seed)
    means = sorted(sum(diffs[rng.randrange(n)] for _ in range(n)) / n for _ in range(N_BOOT))
    return sum(diffs) / n, means[int(0.025 * N_BOOT)], means[int(0.975 * N_BOOT) - 1]


def fmt(m, lo, hi, pct=True):
    s = 100 if pct else 1
    return f"{m*s:+.1f} [{lo*s:+.1f}, {hi*s:+.1f}]" if pct else f"{m:+.3f} [{lo:+.3f}, {hi:+.3f}]"


def mcnemar_exact(b, c):
    """Two-sided exact McNemar (binomial on discordant pairs). b = X right & Y wrong, c = X wrong & Y right."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    p = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * p)


def ok(v, k):
    return isinstance(v.get(k), dict) and v[k].get("a") not in (None, "?")


def correct(v, k):
    return v[k]["a"] == v["_meta"]["y"]


def calibrated(items, key, labels=LETTERS, seed="audit:calfold"):
    """Label-free calibration: subtract per-label mean log-prob estimated on the other fold."""
    ids = sorted(range(len(items)), key=lambda i: str(i))
    random.Random(seed).shuffle(ids)
    fold = {i: j % 2 for j, i in enumerate(ids)}

    def lps(v):
        if "lp" in v[key]:
            return v[key]["lp"]
        return [math.log(max(p, 1e-6)) for p in v[key]["p"]]

    prior = []
    for f in (0, 1):
        mem = [lps(items[i]) for i in range(len(items)) if fold[i] == f]
        prior.append([sum(x[j] for x in mem) / len(mem) for j in range(len(labels))])
    out = []
    for i, v in enumerate(items):
        pr = prior[1 - fold[i]]
        s = [a - b for a, b in zip(lps(v), pr)]
        out.append(labels[max(range(len(labels)), key=lambda j: (s[j], -j))])
    return out


def mc_run(name, r, mm_keys):
    recs = list(r["records"].values())
    print(f"\n=== {name}: {len(recs)} items ===")
    for k in ("R", "S", "C"):
        its = [v for v in recs if ok(v, k)]
        print(f"  acc {k:<6} {100*sum(correct(v,k) for v in its)/len(its):5.1f}%  (n={len(its)})")
    its = [v for v in recs if ok(v, "R") and ok(v, "C")]
    rcal = calibrated(its, "R")
    print(f"  acc Rcal   {100*sum(a == v['_meta']['y'] for a, v in zip(rcal, its))/len(its):5.1f}%  (independent re-implementation)")
    for mk in mm_keys:
        both = [v for v in recs if ok(v, "C") and ok(v, mk)]
        d = [int(correct(v, "C")) - int(correct(v, mk)) for v in both]
        agree = sum(v["C"]["a"] == v[mk]["a"] for v in both) / len(both)
        print(f"  C - {mk:<6} {fmt(*boot_ci(d))} pts  | same answer {100*agree:.1f}%  (n={len(both)})")
    return recs


def run3_paired(recs):
    print("\n=== run 3 paired statistics (requested by the 2026-10-02 independent review) ===")
    mm = ["C_mm0", "C_mm1", "C_mm2"]
    full = [v for v in recs if ok(v, "C") and all(ok(v, k) for k in mm) and ok(v, "R") and ok(v, "S")]
    n = len(full)
    print(f"items with C, R, S and all three wrong-state controls: {n}")

    # Delta_specific: C minus mean of the three wrong states, paired per item
    d = [int(correct(v, "C")) - sum(int(correct(v, k)) for k in mm) / 3 for v in full]
    print(f"Delta_specific = C - mean(C_mm,k): {fmt(*boot_ci(d))} pts")

    print("\nexact McNemar, C vs each wrong state:")
    print("  control  C right/mm wrong  C wrong/mm right  net  p (two-sided)")
    for k in mm:
        b = sum(correct(v, "C") and not correct(v, k) for v in full)
        c = sum(not correct(v, "C") and correct(v, k) for v in full)
        print(f"  {k:<7}  {b:>16}  {c:>16}  {b-c:>+4}  {mcnemar_exact(b, c):.2e}")

    print("\nflip table vs receiver alone (R -> C):")
    for rc in (True, False):
        for cc in (True, False):
            cnt = sum(correct(v, "R") == rc and correct(v, "C") == cc for v in full)
            print(f"  R {'right' if rc else 'wrong'} -> C {'right' if cc else 'wrong'}: {cnt}")
    flips_mm = {k: (sum(not correct(v, "R") and correct(v, k) for v in full),
                    sum(correct(v, "R") and not correct(v, k) for v in full)) for k in mm}
    print("  same for wrong states (R wrong->mm right, R right->mm wrong):", flips_mm)

    rcal = calibrated(full, "R")
    dcal = [int(correct(v, "C")) - int(a == v["_meta"]["y"]) for v, a in zip(full, rcal)]
    print(f"\nC - Rcal (paired, independent calibration): {fmt(*boot_ci(dcal))} pts")
    ccal = calibrated(full, "C")
    mcal = [calibrated(full, k) for k in mm]
    dcc = [int(a == v["_meta"]["y"]) - sum(int(m[i] == v["_meta"]["y"]) for m in mcal) / 3
           for i, (v, a) in enumerate(zip(full, ccal))]
    print(f"Ccal - mean(C_mm,k cal): {fmt(*boot_ci(dcc))} pts")

    def split(label, pred):
        sub = [v for v in full if pred(v)]
        if len(sub) < 20:
            return
        dd = [int(correct(v, "C")) - sum(int(correct(v, k)) for k in mm) / 3 for v in sub]
        inh = [int(v["C"]["a"] == v["S"]["a"]) - sum(int(v[k]["a"] == v["S"]["a"]) for k in mm) / 3 for v in sub]
        print(f"  {label:<34} n={len(sub):>5}  Delta_specific {fmt(*boot_ci(dd))}  | excess P(=S) {fmt(*boot_ci(inh))}")

    print("\nsplits (Delta_specific = acc difference; excess P(=S) = agreement with the sharer's answer beyond wrong states):")
    split("source right", lambda v: correct(v, "S"))
    split("source wrong", lambda v: not correct(v, "S"))
    split("receiver-alone right", lambda v: correct(v, "R"))
    split("receiver-alone wrong", lambda v: not correct(v, "R"))
    split("source right, receiver wrong", lambda v: correct(v, "S") and not correct(v, "R"))
    split("source wrong, receiver right", lambda v: not correct(v, "S") and correct(v, "R"))
    for b in ("mmlu", "arc", "obqa"):
        split(f"benchmark {b}", lambda v, b=b: v["_meta"]["bench"] == b)
    for L in LETTERS:
        split(f"true answer {L}", lambda v, L=L: v["_meta"]["y"] == L)

    pa = None
    print("\nNote: the Part A paper-reproduction number (~55.5%, OBQA N=200, generation readout) is a different subset and "
          "readout from the main audit number above; they are reported separately on purpose.")
    return pa


def pcs1(r):
    recs = list(r["records"].values())
    ans = lambda v: str(v["_meta"]["ans"])
    print(f"\n=== PCS1 main: {len(recs)} items ===")
    for k in ("R", "S_full", "C", "C_mm0", "C_mm1", "C_mm2", "T"):
        its = [v for v in recs if isinstance(v.get(k), dict)]
        print(f"  acc {k:<6} {100*sum(v[k]['a'] == ans(v) for v in its)/len(its):5.1f}%")
    print(f"  A's belief (S_state == X): {100*sum(v['S_state']['a'] == str(v['_meta']['X']) for v in recs)/len(recs):.1f}%")
    full = [v for v in recs if all(isinstance(v.get(k), dict) for k in ("C", "C_mm0", "C_mm1", "C_mm2"))]
    d = [int(v["C"]["a"] == ans(v)) - sum(int(v[k]["a"] == ans(v)) for k in ("C_mm0", "C_mm1", "C_mm2")) / 3 for v in full]
    print(f"  Delta_specific: {fmt(*boot_ci(d))} pts")
    for k in ("C_mm0", "C_mm1", "C_mm2"):
        b = sum(v["C"]["a"] == ans(v) and v[k]["a"] != ans(v) for v in full)
        c = sum(v["C"]["a"] != ans(v) and v[k]["a"] == ans(v) for v in full)
        print(f"  McNemar C vs {k}: {b} vs {c}, p={mcnemar_exact(b, c):.2f}")


def main():
    want = {}
    for line in (HERE / "RAW_RESULTS_ORIGINAL_SHA256.txt").read_text().splitlines():
        h, p = line.split()
        want[p] = h
    print("=== custody: sha256 of decompressed raw results vs hashes recorded at custody time ===")
    data = {}
    for sealed, orig in RAW.items():
        h, r = load(sealed)
        status = "OK" if want.get(orig) == h else "MISMATCH"
        print(f"  {status}  {sealed}  {h[:16]}...")
        data[sealed] = r
    mc_run("run 1 (Qwen2.5-0.5B -> Qwen3-0.6B)", data["run1/results.json.gz"], ["C_mm"])
    mc_run("run 2 (Qwen2.5-1.5B -> Qwen3-1.7B)", data["run2/results.json.gz"], ["C_mm"])
    recs3 = mc_run("run 3 (Qwen3-4B -> Qwen3-0.6B)", data["run3/results.json.gz"], ["C_mm0", "C_mm1", "C_mm2"])
    run3_paired(recs3)
    pcs1(data["pcs1/results.json.gz"])


if __name__ == "__main__":
    main()
