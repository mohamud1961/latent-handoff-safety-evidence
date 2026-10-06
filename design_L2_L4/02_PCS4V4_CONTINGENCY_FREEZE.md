# 02: PCS4v4 contrastive label-free objective (L3 contingency): FREEZE

## Trigger (mechanical)
Run **only if** PCS4v3 (`PCS4V3_INFORMATION_WEIGHTED_OBJECTIVE_FREEZE_2026-10-04.md`) fails its pre-stated read. That is: the token-identity Arm F does not beat matched wrong states on derived beliefs, judged by the cluster-CI lower bound being ≤ 0.

If PCS4v3's token-identity arm passes but its neural arm does not, run PCS4v4 on the neural arm only.

## Objective (only change from PCS4v3)
Arm F's loss is the information-weighted trace loss (from PCS4v3), plus a **contrastive term**. Per training episode i, with its correct prefix p_i and 3 matched wrong prefixes p_j drawn from other train episodes with the same depth and similar length:

`L = L_w(trace_i | p_i) + λ · mean_j max(0, m − [L_w(trace_i | p_j) − L_w(trace_i | p_i)])`

with **λ = 1.0** and **m = 0.5 nats** (per-token weighted mean).

- `L_w` is the PCS4v3 information-weighted cross-entropy: per-token weights from B-restart surprisal, clipped above the per-episode median.
- The term pushes the prefix to carry what *distinguishes* this episode's trace from others. This is information B lacks.
- **No labels:** no variables, coordinates or answers are named. Wrong prefixes come from other episodes.

## Unchanged
Everything else is as in PCS4v3:
- multi-position features;
- the token-identity arm as writer ceiling;
- 40 epochs and val selection on the same composite loss;
- Arm T;
- the strict 17-coordinate probe set and relation types;
- seal-before-probe with a new seed from the new Arm F hash;
- criteria;
- the EXPLORATORY label (source decodability gate 17/27).

## Read
- **L3 reached (exploratory):** neural Arm F beats matched wrong states on derived beliefs (cluster-CI lower bound > 0), **and** on source mistakes, as an excess over wrong states, provided n ≥ 25 probes across ≥ 10 episodes.
- **Confirmatory L3:** needs a fresh-data rerun with a source set that passes the ≥18/27 decodability gate.
- **If null:** record "trace-based label-free objectives insufficient at K=4". The fallback for L4 is the supervised objective; see design 04, decision rule D1.
