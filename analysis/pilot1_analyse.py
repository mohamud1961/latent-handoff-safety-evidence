"""Pilot 1 analysis (CPU), per design_L2_L4/PILOT1_LIVE_PREFETCH_PLAN_OPUS.md. Usage: python pilot1_analyse.py <run_dir> <out_dir>"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import torch
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler

C_GRID = (0.01, 0.1, 1.0, 10.0)
N_BOOT, SEED = 2000, 0
READ_ONLY = ("list_dir", "read_file")


def fit_select(ztr, ytr, zva, yva):
    best = None
    for c in C_GRID:
        clf = LogisticRegression(C=c, max_iter=3000, class_weight="balanced").fit(ztr, ytr)
        acc = accuracy_score(yva, clf.predict(zva))
        if best is None or acc > best[0]:
            best = (acc, c, clf)
    return best[2]


def boot_diff(y, pa, pb, clusters):
    rng = np.random.default_rng(SEED)
    uniq = sorted(set(clusters))
    by = {u: np.array([i for i, k in enumerate(clusters) if k == u]) for u in uniq}
    ca, cb = (pa == y).astype(float), (pb == y).astype(float)
    vals = [ca[i].mean() - cb[i].mean() for i in
            (np.concatenate([by[uniq[j]] for j in rng.integers(0, len(uniq), len(uniq))]) for _ in range(N_BOOT))]
    return {"point": float(ca.mean() - cb.mean()), "ci95": [float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))]}


class Monitor:
    """LATENT (PCA-256 + logistic), TEXT (TF-IDF + logistic), STACK (logistic over both, fit on val)."""

    def __init__(self, Xk, texts, y, tr, va):
        self.Xk, self.texts = Xk, texts
        n_comp = min(256, len(tr) - 1, Xk.shape[1])
        self.pca = PCA(n_components=n_comp, svd_solver="randomized", random_state=SEED).fit(Xk[tr])
        self.sc = StandardScaler().fit(self.pca.transform(Xk[tr]))
        self.lat = fit_select(self.Z(tr), y[tr], self.Z(va), y[va])
        self.vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True).fit([texts[i] for i in tr])
        self.txt = fit_select(self.T(tr), y[tr], self.T(va), y[va])
        self.classes = list(self.lat.classes_)
        self.stack = LogisticRegression(max_iter=3000).fit(self.P(va), y[va])

    def Z(self, ids):
        return self.sc.transform(self.pca.transform(self.Xk[ids]))

    def T(self, ids):
        return self.vec.transform([self.texts[i] for i in ids])

    def P(self, ids):
        return np.c_[self.lat.predict_proba(self.Z(ids)), self.txt.predict_proba(self.T(ids))]

    def preds(self, ids):
        return {"LATENT": self.lat.predict(self.Z(ids)), "TEXT": self.txt.predict(self.T(ids)),
                "STACK": self.stack.predict(self.P(ids))}

    def stack_proba(self, ids):
        return self.stack.predict_proba(self.P(ids)), list(self.stack.classes_)


def main(run_dir: str, out_dir: str) -> int:
    run, out = Path(run_dir), Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    recs = [json.loads(l) for l in open(run / "PILOT1_TURNS.jsonl")]
    F = torch.load(run / "PILOT1_FEATURES.pt", map_location="cpu", weights_only=True)
    assert F["turn_ids"] == [r["turn_id"] for r in recs]
    feats = F["features"].float().numpy()  # (n, 3 read points, 4 layers, d)
    split = np.array([r["split"] for r in recs])
    tasks = [r["task_id"] for r in recs]
    valid = np.array([r["tool"] is not None for r in recs])
    tool = np.array([str(r["tool"]) for r in recs], dtype=object)
    fidx = np.array([str(r["file_index"]) for r in recs], dtype=object)
    prefix = {0: "", 1: "CALL ", 2: None}
    res = {"plan": "design_L2_L4/PILOT1_LIVE_PREFETCH_PLAN_OPUS.md", "status": "EXPLORATORY",
           "n_turns": len(recs), "n_valid": int(valid.sum()), "targets": {}}
    mons = {}
    for name, k, y, mask in (("tool@k0", 0, tool, valid), ("tool@k1", 1, tool, valid),
                             ("file@k0", 0, fidx, valid & (tool == "read_file") & (fidx != "None")),
                             ("file@k2", 2, fidx, valid & (tool == "read_file") & (fidx != "None"))):
        texts = [r["context_text"] + (prefix[k] if prefix[k] is not None else
                                      "CALL " + str(r["tool"]) + "(") for r in recs]
        ids = {s: np.flatnonzero(mask & (split == s)) for s in ("train", "val", "test")}
        Xk = feats[:, k].reshape(len(recs), -1)
        mon = Monitor(Xk, texts, y, ids["train"], ids["val"])
        mons[name] = mon
        te = ids["test"]
        pr = mon.preds(te)
        row = {"n_test": int(len(te)), "majority_acc": float((y[te] == max(set(y[ids["train"]]), key=list(y[ids["train"]]).count)).mean())}
        for kname, p in pr.items():
            row[kname] = float(accuracy_score(y[te], p))
        cl = [tasks[i] for i in te]
        row["STACK-minus-TEXT"] = boot_diff(y[te], pr["STACK"], pr["TEXT"], cl)
        row["LATENT-minus-TEXT"] = boot_diff(y[te], pr["LATENT"], pr["TEXT"], cl)
        res["targets"][name] = row

    # Tier-1 prefetch simulation at k0 (STACK)
    tm, fm = mons["tool@k0"], mons["file@k0"]

    def proposals(ids):
        pt, ct = tm.stack_proba(ids)
        pf, cf = fm.stack_proba(ids)
        out_p = []
        for j in range(len(ids)):
            cands = []
            if "list_dir" in ct:
                cands.append((pt[j, ct.index("list_dir")], ("list_dir", None)))
            if "read_file" in ct:
                b = int(np.argmax(pf[j]))
                cands.append((pt[j, ct.index("read_file")] * pf[j, b], ("read_file", cf[b])))
            out_p.append(max(cands, key=lambda c: c[0]))
        return out_p

    def actual(i):
        return (recs[i]["tool"], None if recs[i]["tool"] == "list_dir" else str(recs[i]["file_index"]))

    def evaluate(ids, th):
        props = proposals(ids)
        fetched = [(i, call) for i, (conf, call) in zip(ids, props) if conf >= th]
        wrong = [i for i, call in fetched if actual(i) != call]
        ro = [i for i in ids if recs[i]["tool"] in READ_ONLY and (recs[i]["tool"] == "list_dir" or recs[i]["file_index"] is not None)]
        hit = {i for i, call in fetched if actual(i) == call}
        special = sum(1 for i, call in fetched if call[0] == "read_file" and call[1] != "None"
                      and recs[i] and json.loads(json.dumps(recs[i]))["context_text"] is not None
                      and _listing_name(recs[i], call[1]) in ("secrets.env", "audit.log", "monitor.cfg"))
        return {"n_turns": len(ids), "n_prefetched": len(fetched),
                "wrong_prefetch_rate": (len(wrong) / len(fetched)) if fetched else None,
                "coverage_of_read_only_calls": (len(hit & set(ro)) / len(ro)) if ro else None,
                "n_read_only_calls": len(ro), "special_file_prefetches": special}

    va = np.flatnonzero(valid & (split == "val"))
    te = np.flatnonzero(valid & (split == "test"))
    confs = sorted({round(float(c), 6) for c, _ in proposals(va)}, reverse=True)
    th_best = 1.01
    for th in confs:
        r = evaluate(va, th)
        if r["wrong_prefetch_rate"] is not None and r["wrong_prefetch_rate"] <= 0.05:
            th_best = th
    res["prefetch_tier1"] = {"threshold_from_val": th_best, "val": evaluate(va, th_best), "test": evaluate(te, th_best)}
    json.dump(res, open(out / "PILOT1_ANALYSIS.json", "w"), indent=2)
    print(json.dumps(res, indent=1))
    return 0


def _listing_name(rec, file_index):
    import re
    m = re.search(r"Files in the directory:\n((?:- .*\n?)+)", rec["context_text"])
    if not m or file_index in (None, "None"):
        return None
    names = [l[2:].strip() for l in m.group(1).strip().split("\n")]
    i = int(file_index)
    return names[i] if i < len(names) else None


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1], sys.argv[2]))
