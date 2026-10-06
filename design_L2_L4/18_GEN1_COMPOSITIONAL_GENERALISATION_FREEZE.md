# 18: GEN1, reusable state or update-specific shortcuts? (compositional generalisation): FREEZE

**Claude (Opus), designer, 2026-10-05.** Profile: `modal-new-account`.

## Trigger
The same failure appeared in three experiments: performance collapsed on update values held out from bridge training.

| Experiment | Held-out update values | Pre-registered bar |
|---|---|---|
| PCS7b | 48.8% | 50% |
| CHAIN1 | 46.4% | 50% |
| SCALE1 X-FAM | 0.3% | — |

**Counter-evidence:** SCALE1 S-UP (8B → 4B) generalised (85.6%).

## Question
Does the bridge carry A's value as a **reusable state**, or as **update-specific shortcuts**? And is the failure an artefact of the training distribution, i.e. of never seeing m = 5–9?

## Base
The PCS7b P1 regime, unchanged except where stated:
- A = Qwen3-4B with a private 10-entry map g, answering v = g(d) silently.
- B = Qwen3-1.7B, which never sees g.
- Capture at the last 2 prompt positions, layers 4–36 step 4.
- Models pinned per G1.
- Fresh data: 1,600 episodes, seed 20261021, split 900 / 200 / ≥ 400.
- D1-b objective, 40 epochs, val-loss selection.
- Seal plus probe commitment sha256(bridge ‖ "GEN1-<arm>").

## Arms (same source data and captures; only the bridge-training queries differ)
- **REP (replicate the failure):** train on single-step queries e = (v + m) % 10 with m ∈ {1–4}. Test on m ∈ {5–9}.
- **COMP (treatment):** train on all m ∈ {1–9}, **except** a fixed set of 20 held-out (v, m) combinations: for each v, m ∈ {((v + 3) % 9) + 1, ((v + 7) % 9) + 1}. These are fixed now, before any data exists. Every v and every m appear in training; only those *combinations* never do.
  - **Primary test set:** the held-out combinations, on test episodes.
  - Seen combinations are reported as secondary.
- Both arms include the readback auxiliary (λ = 0.25).
- **Two-step unseen composition (secondary, both arms):** e = (v + m1 + m2) % 10, never used in training.

## Controls (test)
- PCS;
- 3 matched-wrong states (different A answer, nearest prompt length);
- swap (follow the partner's A answer + m);
- zero and random;
- B_restart;
- oracle ("Intermediate result: v = …");
- token-identity ceiling.

## Criteria (COMP arm, held-out combinations; state-cluster bootstrap 10k, seed 0; exact McNemar)
1. **Fidelity** to A's answer + m: **≥ 60%**.
2. **Specificity:** PCS − mean matched wrong **≥ 30 pts**, CI > 0, McNemar p < 0.05 against each partner.
3. **Swap ≥ 40%.**
4. **Beats restart by ≥ 20 pts.**

The REP arm is expected to reproduce the failure (held-out m < 50%). It is **descriptive**, with no pass/fail; it confirms the failure is reproducible.

## Interpretation (fixed now)
- **COMP passes:** the bridge can carry a reusable value when training covers the operation space, and the earlier near misses were a training-distribution artefact. This licenses new, separately pre-registered **PCS7c and PCS3d** using the COMP recipe.
- **COMP fails:** the bridge encodes query-specific mappings even with full operation coverage. Generalisation is a core unsolved problem, and it becomes the first goal of the funded phase.

## Compute
About $3–5 on L4 (`modal-new-account`). Requires a ≤ 10-min GPU smoke first.
