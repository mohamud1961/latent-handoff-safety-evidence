"""Independent audit of PCS2b pre-answer state realization (Claude Opus, 2026-10-03).

Own re-implementation; does not import or reuse the executor's pcs2b_audit.py.
Inputs: raw/pcs2b_results.json, raw/pcs2b_source_cache.pt (hashes checked against PCS2B_RUN_MANIFEST.json).
Run with a Python that has torch (CPU is enough).
"""
import hashlib, json, random, sys
from collections import defaultdict
from pathlib import Path

import torch

RAW = Path(__file__).parent / "raw"
EXPECT = {
    "pcs2b_results.json": "07fd9ad60d39089a5f03a0c1b70bf3fa862aad7e8d4776e8249924e7230be558",
    "pcs2b_source_cache.pt": "42f419d69f5ebda6270ecbd335b2e8de72123cf757d0ebc2327c1620bd8c048f",
    "pcs2b_bridge.pt": "87de8fb8a70d62aea0a2545faeb3c5b12890832dfd24d1b64e0b4a84cea8a771",
    "pcs2b_preanswer_bridge.py": "29c47aa64ef482e0654052df223dc1b9596c0a23bfbb93ddb5d5959562b8949c",
}
ARMS = ("restart", "oracle", "text", "pcs", "wrong0", "wrong1", "wrong2", "zero", "random")
B = 10000


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def cluster_boot(rows, stat, seed=0):
    """Bootstrap over source states (clusters), not rows."""
    by = defaultdict(list)
    for r in rows:
        by[r["id"]].append(r)
    keys = sorted(by)
    rng = random.Random(seed)
    vals = []
    for _ in range(B):
        sample = [r for k in (rng.choice(keys) for _ in keys) for r in by[k]]
        vals.append(stat(sample))
    vals.sort()
    return stat(rows), vals[int(0.025 * B)], vals[int(0.975 * B) - 1]


def acc(rows, arm, tgt):
    return sum(r[arm] == r[tgt] for r in rows) / len(rows)


def pct(t):
    return f"{100*t[0]:.2f}% [{100*t[1]:.2f}, {100*t[2]:.2f}]"


def main():
    print("== custody")
    for fn, h in EXPECT.items():
        got = sha(RAW / fn)
        print(f"  {'OK ' if got == h else 'BAD'} {fn}")
        if got != h:
            sys.exit(1)

    res = json.load(open(RAW / "pcs2b_results.json"))
    ev = res["result"]
    rows = ev["records"]
    cache = torch.load(RAW / "pcs2b_source_cache.pt", map_location="cpu", weights_only=True)
    items = cache["items"]
    by_id = {it["id"]: it for it in items}

    print("\n== split integrity")
    split_ids = defaultdict(set)
    split_P = defaultdict(set)
    for it in items:
        split_ids[it["split"]].add(it["id"])
        split_P[it["split"]].add(it["P"])
    for a in ("train", "val", "test"):
        for b in ("train", "val", "test"):
            if a < b:
                print(f"  {a}/{b}: shared ids {len(split_ids[a] & split_ids[b])}, shared problem texts {len(split_P[a] & split_P[b])}")
    test_ids = {r["id"] for r in rows}
    print(f"  records {len(rows)}, states {len(test_ids)}, all test-split: {test_ids <= split_ids['test']}")
    print(f"  m values: {sorted({r['m'] for r in rows})}; held-out flags consistent: "
          f"{all(r['heldout_m'] == (r['m'] >= 5) for r in rows)}")

    print("\n== record consistency vs source cache")
    bad = sum(by_id[r["id"]]["A_belief"] != r["A_belief"] or by_id[r["id"]]["X"] != r["X"]
              or r["fidelity_target"] != (r["A_belief"] + r["m"]) % 10 for r in rows)
    print(f"  mismatched rows: {bad}")
    print(f"  source checkpoint ends immediately before the answer token for every test state: "
          f"{all(by_id[i]['A_predigit_argmax_token'] == by_id[i]['answer_token_id'] for i in test_ids)}")

    for name, sub in (("ALL", rows), ("HELD-OUT m=5..9", [r for r in rows if r["heldout_m"]])):
        print(f"\n== {name} (n={len(sub)} rows, {len({r['id'] for r in sub})} states); state-cluster bootstrap")
        for arm in ARMS:
            print(f"  {arm:<8} fidelity {pct(cluster_boot(sub, lambda s, a=arm: acc(s, a, 'fidelity_target')))}"
                  f"   objective {100*acc(sub, arm, 'objective_target'):.2f}%")
        print(f"  readback fidelity {100*acc(sub, 'readback', 'A_belief'):.2f}%")
        eff = cluster_boot(sub, lambda s: acc(s, "pcs", "fidelity_target")
                           - sum(acc(s, f"wrong{k}", "fidelity_target") for k in range(3)) / 3)
        print(f"  Delta_specific (pcs - mean wrong): {100*eff[0]:+.2f} pts [{100*eff[1]:+.2f}, {100*eff[2]:+.2f}]")
        ovo = cluster_boot(sub, lambda s: acc(s, "pcs", "fidelity_target") - acc(s, "oracle", "fidelity_target"))
        print(f"  pcs - exact-state text oracle: {100*ovo[0]:+.2f} pts [{100*ovo[1]:+.2f}, {100*ovo[2]:+.2f}]")

    # Rebuild the wrong-state partners exactly as the runner does (matched_wrong_maps, seed cfg.seed+909).
    print("\n== wrong-state controls: does B follow the PARTNER's belief?")
    seed = cache["config"]["seed"] + 909
    test_idx = [i for i, it in enumerate(items) if it["split"] == "test"]
    rng = random.Random(seed)
    maps = []
    for k in range(3):
        mp = {}
        for i in test_idx:
            it = items[i]
            cand = [j for j in test_idx if j != i and items[j]["v"] == it["v"] and items[j]["A_belief"] != it["A_belief"]]
            if not cand:
                cand = [j for j in test_idx if j != i and items[j]["A_belief"] != it["A_belief"]]
            cand.sort(key=lambda j: (abs(items[j]["checkpoint_tokens"] - it["checkpoint_tokens"]), j))
            w = cand[: min(16, len(cand))]
            mp[i] = w[(k + rng.randrange(len(w))) % len(w)]
        maps.append(mp)
    id_to_idx = {items[i]["id"]: i for i in test_idx}
    for k in range(3):
        same_var = sum(items[maps[k][i]]["v"] == items[i]["v"] for i in test_idx) / len(test_idx)
        dlen = sum(abs(items[maps[k][i]]["checkpoint_tokens"] - items[i]["checkpoint_tokens"]) for i in test_idx) / len(test_idx)
        follow = sum(r[f"wrong{k}"] == (items[maps[k][id_to_idx[r['id']]]]["A_belief"] + r["m"]) % 10 for r in rows) / len(rows)
        print(f"  wrong{k}: partner same variable {100*same_var:.1f}%, mean |length diff| {dlen:.1f} tokens, "
              f"B follows partner's belief {100*follow:.2f}%")

    print("\n== source-mistake fidelity (A wrong)")
    wr = [r for r in rows if not r["A_correct"]]
    print(f"  states with wrong A belief: {len({r['id'] for r in wr})}, rows {len(wr)}")
    for arm in ("pcs", "oracle", "wrong0", "restart"):
        t = cluster_boot(wr, lambda s, a=arm: acc(s, a, "fidelity_target"))
        print(f"  {arm:<8} follows A's wrong belief {pct(t)}   hits truth {100*acc(wr, arm, 'objective_target'):.2f}%")

    print("\n== where is A's belief decodable? (linear probe per source layer, train->test)")
    feats = cache["features"].float()
    layers = cache["source_layers"]
    tr = [i for i, it in enumerate(items) if it["split"] == "train"]
    te = test_idx
    ytr = torch.tensor([items[i]["A_belief"] for i in tr])
    yte = torch.tensor([items[i]["A_belief"] for i in te])
    for li, L in enumerate(layers):
        Xtr, Xte = feats[tr, li], feats[te, li]
        mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-6
        Xtr, Xte = (Xtr - mu) / sd, (Xte - mu) / sd
        torch.manual_seed(0)
        W = torch.zeros(Xtr.shape[1], 10, requires_grad=True)
        b = torch.zeros(10, requires_grad=True)
        opt = torch.optim.LBFGS([W, b], max_iter=200)

        def closure():
            opt.zero_grad()
            loss = torch.nn.functional.cross_entropy(Xtr @ W + b, ytr) + 1e-2 * W.pow(2).sum()
            loss.backward()
            return loss
        opt.step(closure)
        a = ((Xte @ W + b).argmax(1) == yte).float().mean().item()
        print(f"  layer {L:>2}: held-out probe accuracy {100*a:.1f}%")


if __name__ == "__main__":
    main()
