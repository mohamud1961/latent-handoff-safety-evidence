# 20: COGMON1, monitoring transferred state at the handoff: read → predict → intervene (pilot): FREEZE

**Claude (Opus), designer, 2026-10-05.** Profile: `modal-new-account`.

## Question
Before B acts, can a monitor at the handoff:
- **(read)** recover several independently varying properties of A's transferred state;
- **(predict)** say what B will answer;
- **(intervene)** edit one identified property in the handoff object, so that B's behaviour changes as predicted on that property only?

This upgrades MON2 (clean vs corrupted) to *behaviourally relevant state is observable and controllable at the handoff*.

## Base
The **sealed PCS3c neural bridge and data**, copied to `modal-new-account` with shas verified:
- bridge `317b1ff3…`;
- source bundle `23d09853…`;
- split and handoff manifest `90e479c5…`.

The setup:
- A = Qwen3-4B holds three registers a, b, c, independently varying digits (0–9).
- The bridge maps A's multi-position state to a 4-slot prefix for B = Qwen3-1.7B, frozen.
- B answers PCS3c's own selector queries ("which value does register a/b/c hold", per PCS3c's evaluation prompts).
- Train / val / test = PCS3c's sealed splits: 512 / 128 / 959 states.
- **The monitor uses train and val only.** Test is used once. Bootstrap seed 0, 10k state-cluster resamples.

**Handoff object H** is the bridge output prefix, 4 × 2048, flattened. Standardise on train, then PCA to 128 dimensions (fit on train).

## Read
Per register r ∈ {a, b, c}: a multinomial L2-logistic probe on H predicts A's register value. C is chosen on val.

## Predict
Per selector query: a logistic model on H, plus a one-hot of the selector, predicts **B's actual answer digit**. It is fit on train, using B's actual train answers obtained by running B on train states.

Baselines:
- **A-value baseline:** predict B = A's value for the queried register;
- **P-only baseline:** predict from the public problem's features.

## Intervene (mean-difference editing in H-space, computed on train only)
For a test state and a target register r currently at value u (A's value), choose a target u′ ≠ u. u′ is seeded (20261023) and must not equal the other registers' values.
- Edit: H′ = H + (μ_r[u′] − μ_r[u]), where μ_r[k] is the train mean of H over states whose register r = k.
- Map back to prefix space (inverse PCA plus de-standardisation) and give the result to B.
- Query B on all three selectors.

Arms:
- **EDIT-r:** edit target r.
- **RAND:** add a random direction of the same norm (seed 0).
- **WRONG-REG:** apply the mean-difference for a different register.
- **NONE:** unedited H.

Run all three registers as targets for every test state.

## Criteria (test)
1. **Read:**
   - mean per-register balanced accuracy **≥ 0.60** (chance 0.10), each register ≥ 0.50;
   - all three correct jointly **≥ 0.25**.
2. **Predict:** accuracy at predicting B's actual answer **≥ 0.65**, with the bootstrap lower bound **above the A-value baseline**.
3. **Intervene: on-target:** under EDIT-r, B answers u′ (+ the query's update, if any) on register r's query at rate **≥ 40%**, vs RAND **≤ 10%**. Δ ≥ 30 pts, CI > 0, McNemar.
4. **Intervene: off-target preserved:** under EDIT-r, B's answers on the *other two* registers stay the same as under NONE in **≥ 80%** of cases, and within 10 pts of RAND's preservation rate.

## Claim if 1–4 pass
"Behaviourally relevant state crossing a latent handoff can be read (several independent properties), its effect on the receiver predicted before the receiver acts, and a single identified property edited at the handoff, changing the receiver's behaviour on that property while leaving the others intact."

**Limits.**
- One bridge and toy registers.
- Linear monitor and mean-difference edits.
- The full COGMON programme (more properties, other channels, adversarial states) is BlueDot Stage II.

## Compute
B inference plus small probes. About $1–3 on L4. Requires a ≤ 10-min GPU smoke first.
