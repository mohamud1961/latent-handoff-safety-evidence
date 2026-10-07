"""Pilot 0 (exploratory): read the next tool call from pre-output state. See design_L2_L4/PILOT0_ACTION_FROM_STATE_PLAN_OPUS.md.

CPU only; uses saved MON3b records and source features. Usage: python pilot0_action_from_state.py <src_dir> <out_dir>
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

import numpy as np
import torch
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.preprocessing import StandardScaler

C_GRID = (0.01, 0.1, 1.0, 10.0)
N_BOOT, SEED = 2000, 0
READ_ONLY = {"list_dir", "read_file"}


def calls_of(e):
    c = e["a_calls"]
    return ast.literal_eval(c) if isinstance(c, str) else c


def fit_select(ztr, ytr, zva, yva):
    best = None
    for c in C_GRID:
        clf = LogisticRegression(C=c, max_iter=3000, class_weight="balanced").fit(ztr, ytr)
        acc = accuracy_score(yva, clf.predict(zva))
        if best is None or acc > best[0]:
            best = (acc, c, clf)
    return best


def boot_diff(y, pa, pb, clusters):
    rng = np.random.default_rng(SEED)
    uniq = sorted(set(clusters))
    by = {u: [i for i, k in enumerate(clusters) if k == u] for u in uniq}
    ca, cb = (pa == y).astype(float), (pb == y).astype(float)
    vals = []
    for _ in range(N_BOOT):
        idx = np.concatenate([by[uniq[j]] for j in rng.integers(0, len(uniq), len(uniq))])
        vals.append(ca[idx].mean() - cb[idx].mean())
    return float(ca.mean() - cb.mean()), [float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))]


def main(src: str, out: str) -> int:
    src_p, out_p = Path(src), Path(out)
    out_p.mkdir(parents=True, exist_ok=True)
    eps = json.load(open(src_p / "MON3B_SOURCE_RECORDS.json"))
    feats = torch.load(src_p / "MON3B_SOURCE_FEATURES.pt", map_location="cpu", weights_only=True)
    assert feats["episode_ids"] == [e["episode_id"] for e in eps]
    X = feats["features"].float().flatten(1).numpy()
    text = [e["system"] + "\n" + e["P"] for e in eps]
    split = np.array([e["split"] for e in eps])
    cl = [e["task_id"] for e in eps]
    calls = [calls_of(e) for e in eps]
    targets = {
        "T1_first_tool": [c[0]["tool"] if c else None for c in calls],
        "T2_second_tool": [c[1]["tool"] if len(c) > 1 else None for c in calls],
        "T3_first_is_read_only": [(c[0]["tool"] in READ_ONLY) if c else None for c in calls],
    }
    tr_all = np.flatnonzero(split == "train")
    pca = PCA(n_components=256, svd_solver="randomized", random_state=SEED).fit(X[tr_all])
    Z = pca.transform(X)
    res = {"plan": "design_L2_L4/PILOT0_ACTION_FROM_STATE_PLAN_OPUS.md", "status": "EXPLORATORY", "targets": {}}
    for name, y_all in targets.items():
        keep = np.array([v is not None for v in y_all])
        y_all = np.array([str(v) for v in y_all], dtype=object)
        idx = {s: np.flatnonzero((split == s) & keep) for s in ("train", "val", "test", "testU")}
        sc = StandardScaler().fit(Z[idx["train"]])
        lat = fit_select(sc.transform(Z[idx["train"]]), y_all[idx["train"]], sc.transform(Z[idx["val"]]), y_all[idx["val"]])
        vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True).fit([text[i] for i in idx["train"]])
        T = lambda ids: vec.transform([text[i] for i in ids])  # noqa: E731
        txt = fit_select(T(idx["train"]), y_all[idx["train"]], T(idx["val"]), y_all[idx["val"]])
        classes = list(lat[2].classes_)
        assert classes == list(txt[2].classes_)

        def probs(ids):
            return np.c_[lat[2].predict_proba(sc.transform(Z[ids])), txt[2].predict_proba(T(ids))]
        stack = LogisticRegression(max_iter=3000, C=1.0).fit(probs(idx["val"]), y_all[idx["val"]])
        tres = {"classes": classes, "C_latent": lat[1], "C_text": txt[1],
                "train_class_counts": {c: int((y_all[idx["train"]] == c).sum()) for c in classes}}
        for s in ("test", "testU"):
            ids = idx[s]
            if len(ids) == 0 or len(set(y_all[ids])) < 2:
                continue
            y = y_all[ids]
            pl = lat[2].predict(sc.transform(Z[ids]))
            pt = txt[2].predict(T(ids))
            ps = stack.predict(probs(ids))
            majority = max(set(y_all[idx["train"]]), key=list(y_all[idx["train"]]).count)
            row = {"n": int(len(ids)), "majority_class_acc": float((y == majority).mean())}
            for k, p in (("LATENT", pl), ("TEXT", pt), ("STACK", ps)):
                row[k] = {"acc": float(accuracy_score(y, p)), "macro_f1": float(f1_score(y, p, average="macro"))}
            cls = [cl[i] for i in ids]
            for a, b, pa, pb in (("STACK", "TEXT", ps, pt), ("LATENT", "TEXT", pl, pt)):
                pt_, ci = boot_diff(y, pa, pb, cls)
                row[f"{a}-minus-{b}_acc"] = {"point": pt_, "ci95": ci}
            tres[s] = row
        if name == "T1_first_tool" and "list_dir" in classes:
            j = classes.index("list_dir")
            pv = stack.predict_proba(probs(idx["val"]))[:, list(stack.classes_).index("list_dir")]
            yv = y_all[idx["val"]] == "list_dir"
            best_th = 1.0
            for th in np.sort(np.unique(pv))[::-1]:
                fl = pv >= th
                if fl.sum() and (~yv[fl]).mean() <= 0.05:
                    best_th = th
            op = {"threshold_from_val": float(best_th)}
            for s in ("test", "testU"):
                ids = idx[s]
                p = stack.predict_proba(probs(ids))[:, list(stack.classes_).index("list_dir")]
                yy = y_all[ids] == "list_dir"
                fl = p >= best_th
                op[s] = {"true_list_dir_caught": float(fl[yy].mean()) if yy.any() else None,
                         "wrong_prefetch_rate": float((~yy[fl]).mean()) if fl.any() else None,
                         "n_true_list_dir": int(yy.sum())}
            res["T4_list_dir_prefetch_STACK"] = op
        res["targets"][name] = tres
    json.dump(res, open(out_p / "PILOT0.json", "w"), indent=2)
    print(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1], sys.argv[2]))
