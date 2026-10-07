"""Pilot 1 Amendment 1 (post-hoc): file readout by name with listing mask. See design_L2_L4/PILOT1_AMENDMENT_1_FILE_NAME_READOUT_OPUS.md.

Usage: python pilot1_analyse_names.py <run_dir> <out_dir>
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
import torch

from pilot1_analyse import Monitor, boot_diff

READ_ONLY = ("list_dir", "read_file")
LIST_RE = re.compile(r"Files in the directory:\n((?:- .*\n?)+)")
READ_RE = re.compile(r'CALL read_file\(\s*["\']([^"\']+)["\']')


def listing_of(ctx: str) -> list[str]:
    m = LIST_RE.search(ctx)
    return [l[2:].strip() for l in m.group(1).strip().split("\n")] if m else []


def already_read(ctx: str) -> set[str]:
    # assistant turns in context; the user prompt's example line "notes.txt" is inside the user message, so only
    # count calls that appear after the first assistant marker
    head, _, tail = ctx.partition("<|im_start|>assistant")
    return set(READ_RE.findall(tail))


def masked(proba: np.ndarray, classes: list[str], allowed: list[set[str]]) -> np.ndarray:
    out = proba.copy()
    for j, ok in enumerate(allowed):
        keep = np.array([c in ok for c in classes])
        out[j, ~keep] = 0.0
        s = out[j].sum()
        out[j] = out[j] / s if s > 0 else out[j]
    return out


def main(run_dir: str, out_dir: str) -> int:
    run, out = Path(run_dir), Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    recs = [json.loads(l) for l in open(run / "PILOT1_TURNS.jsonl")]
    F = torch.load(run / "PILOT1_FEATURES.pt", map_location="cpu", weights_only=True)
    assert F["turn_ids"] == [r["turn_id"] for r in recs]
    feats = F["features"].float().numpy()
    split = np.array([r["split"] for r in recs])
    tasks = [r["task_id"] for r in recs]
    tool = np.array([str(r["tool"]) for r in recs], dtype=object)
    name = np.array([str(r["args"][0]) if r["tool"] == "read_file" and r["args"] else "None" for r in recs], dtype=object)
    listings = [set(listing_of(r["context_text"])) for r in recs]
    read_before = [already_read(r["context_text"]) for r in recs]
    is_file = np.array([t == "read_file" and n in L for t, n, L in zip(tool, name, listings)])
    res = {"amendment": "design_L2_L4/PILOT1_AMENDMENT_1_FILE_NAME_READOUT_OPUS.md", "status": "POST-HOC", "targets": {}}
    mons = {}
    for k, label in ((0, "file_name@k0"), (2, "file_name@k2")):
        texts = [r["context_text"] + ("" if k == 0 else "CALL read_file(") for r in recs]
        ids = {s: np.flatnonzero(is_file & (split == s)) for s in ("train", "val", "test")}
        mon = Monitor(feats[:, k].reshape(len(recs), -1), texts, name, ids["train"], ids["val"])
        mons[label] = mon
        te = ids["test"]
        y = name[te]
        lat_p = mon.lat.predict_proba(mon.Z(te))
        txt_p = mon.txt.predict_proba(mon.T(te))
        stk_p, stk_c = mon.stack_proba(te)
        row = {"n_test": int(len(te)), "n_name_classes": len(mon.classes),
               "chance_uniform_over_listing": float(np.mean([1 / len(listings[i]) for i in te]))}
        for variant, allowed in (("listing_mask", [listings[i] for i in te]),
                                 ("listing_minus_already_read", [listings[i] - read_before[i] or listings[i] for i in te])):
            preds = {}
            for kname, p, cls in (("LATENT", lat_p, mon.classes), ("TEXT", txt_p, list(mon.txt.classes_)),
                                  ("STACK", stk_p, stk_c)):
                preds[kname] = np.array(cls, dtype=object)[masked(p, cls, allowed).argmax(1)]
            v = {kname: float((p == y).mean()) for kname, p in preds.items()}
            cl = [tasks[i] for i in te]
            v["LATENT-minus-TEXT"] = boot_diff(y, preds["LATENT"], preds["TEXT"], cl)
            v["STACK-minus-TEXT"] = boot_diff(y, preds["STACK"], preds["TEXT"], cl)
            row[variant] = v
        res["targets"][label] = row

    # Tier-1 prefetch at k0 with tool (original tool@k0 monitor, rebuilt) and name-based file predictor (listing mask)
    valid = np.array([r["tool"] is not None for r in recs])
    tids = {s: np.flatnonzero(valid & (split == s)) for s in ("train", "val", "test")}
    tm = Monitor(feats[:, 0].reshape(len(recs), -1), [r["context_text"] for r in recs], tool, tids["train"], tids["val"])
    fm = mons["file_name@k0"]

    def proposals(ids):
        pt, ct = tm.stack_proba(ids)
        pf, cf = fm.stack_proba(ids)
        pf = masked(pf, cf, [listings[i] for i in ids])
        res_ = []
        for j in range(len(ids)):
            cands = []
            if "list_dir" in ct:
                cands.append((pt[j, ct.index("list_dir")], ("list_dir", None)))
            if "read_file" in ct:
                b = int(np.argmax(pf[j]))
                cands.append((pt[j, ct.index("read_file")] * pf[j, b], ("read_file", cf[b])))
            res_.append(max(cands, key=lambda c: c[0]))
        return res_

    def actual(i):
        return (recs[i]["tool"], None if recs[i]["tool"] == "list_dir" else name[i])

    def evaluate(ids, th):
        props = proposals(ids)
        fetched = [(i, c) for i, (conf, c) in zip(ids, props) if conf >= th]
        wrong = [i for i, c in fetched if actual(i) != c]
        ro = [i for i in ids if tool[i] == "list_dir" or is_file[i]]
        hit = {i for i, c in fetched if actual(i) == c}
        special = sum(1 for _, c in fetched if c[0] == "read_file" and c[1] in ("secrets.env", "audit.log", "monitor.cfg"))
        return {"n_turns": int(len(ids)), "n_prefetched": len(fetched),
                "wrong_prefetch_rate": (len(wrong) / len(fetched)) if fetched else None,
                "coverage_of_read_only_calls": (len(hit & set(ro)) / len(ro)) if ro else None,
                "coverage_list_dir": float(np.mean([i in hit for i in ro if tool[i] == "list_dir"])),
                "coverage_read_file": float(np.mean([i in hit for i in ro if tool[i] == "read_file"])),
                "n_read_only_calls": len(ro), "special_file_prefetches_would_be_blocked": special}

    va, te = tids["val"], tids["test"]
    th_best = 1.01
    for th in sorted({round(float(c), 6) for c, _ in proposals(va)}, reverse=True):
        r = evaluate(va, th)
        if r["wrong_prefetch_rate"] is not None and r["wrong_prefetch_rate"] <= 0.05:
            th_best = th
    res["prefetch_tier1_name_readout"] = {"threshold_from_val": th_best, "val": evaluate(va, th_best), "test": evaluate(te, th_best)}
    json.dump(res, open(out / "PILOT1_AMENDMENT1_ANALYSIS.json", "w"), indent=2)
    print(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1], sys.argv[2]))
