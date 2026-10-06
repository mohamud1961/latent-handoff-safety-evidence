# PREREG, PCS1: inherit -> new evidence -> new deduction

Written 2026-10-02 after the two pilots and before any main-run result exists; frozen before the main push. Notebook `pcs1/pcs1_new_deduction.ipynb` (MODE=main), kernel `kaggle-user/pcs1-new-deduction`. Any departure is logged in `results.json["deviations"]` and `RESULTS_pcs1.md`.

## Bridge
Frozen, no training: released general fuser `nics-efc/C2C_Fuser/qwen3_0.6b+qwen3_4b_Fuser/final`; A (sharer) = `Qwen/Qwen3-4B`, B (receiver) = `Qwen/Qwen3-0.6B`; C2C code at commit `3ca0e98`. **The fuser was trained for one-shot QA on identical inputs for both models, not for continuation: it was never trained to hand a state to a receiver that then reads new evidence A did not see.** This tests whether an existing bridge supports PCS-style continuation. It is not a test of the PCS idea in general.

## Task (synthetic, exactly checkable, single-digit answer, no chain of thought)
- **P (fused section, read by A):** a header, three initial digit assignments `a = 3`, `b = 7`, `c = 2`, then `d` addition-only update steps mod 10, each `x = (y + z) % 10` or `x = (y + c) % 10`, where y is the variable updated at the previous step (a dependency chain, so depth is real), z a random variable, c a constant in 1..9. The queried variable x is the one updated last. Multiplicative updates were piloted first (v1) and A could not do them in one forward pass.
- **U (new evidence):** `Now e = (x + m) % 10. What is e? Answer with a single digit.` with m in 1..9. The U-answer = (X + m) % 10 differs from **every** variable's value at the end of P (rejection sampling), so B cannot answer by copying a state value. Because addition of a nonzero m is a bijection, a wrong belief about X always implies a wrong U-answer.
- **Placement:** the fused section is the chat prefix + header + P (kv_cache_index [1,0]); U, the answer prompt and "The answer is " are the unfused tail ([-1,0]). A never sees U. A's "cognition" is its forward pass over P.
- **Readout:** logits over the ten digit tokens "0".."9" (single, identical tokens in both tokenizers) after "The answer is ", thinking off. Chance is 10%.
- **Calibrated receiver (Rcal):** per-digit mean log-prob prior, label-free, 2-fold cross-fit (seed 0, one split for all conditions); a calibrated version of any condition uses its own cross-fit prior.

## Pilots and the frozen depth
Pilot v1 (multiplicative updates, depths 1,2,3,4,6, 200 items each): no depth qualified (A's state accuracy 23.5% at depth 1, near chance beyond); see `RESULTS_pcs1_pilot.md`. **Pilot v2 (addition-only, 200 items per depth, `pcs1_pilot/kaggle_out/`):**

| depth | R (P+U) | Rcal | R_state | S_full (P+U) | S_state (P only) | S_state - R | |
|---|---|---|---|---|---|---|---|
| 0 | 42.5% | 49.5% | 99.0% | 95.5% | 100.0% | +57.5 | sanity (excluded) |
| 1 | 7.5% | 8.5% | 17.0% | 18.5% | 93.0% [89.5, 96.5] | +85.5 | **qualifies** |
| 2 | 13.0% | 15.0% | 9.5% | 11.5% | 18.0% | +5.0 | no |
| 3 | 11.5% | 8.5% | 9.5% | 11.5% | 15.0% | +3.5 | no |

Qualification rule (fixed before v2): S_state - R >= 20 pts and S_state >= 60%, depth 0 excluded. **Frozen: depth 1 only.** Depth 0 shows the pipeline works (A reads the stored value 100%).

## Main run (frozen)
- **N = 3000 items at depth 1** (seeded generator, salt "main", processed in a fixed shuffled order). N is larger than the 1500 first aimed for because A's belief is wrong on only about 7% of items and the fidelity test needs those: expected about 200 wrong-belief items.
- **Conditions:** R (B alone on P+U); Rcal; R_state (B alone on P only, informational); S_full (A alone on P+U, reference); S_state (A alone on P + "What is x now?": **A's belief**); **C** (C2C on P, then U); **C_mm,k, k=1..3**: the sharer cache computed on a different program of exactly the same token length whose value of the queried variable differs from the true one and from the other two wrong caches (so the three wrong states differ; B always sees the real P+U); **T** (text handoff: B alone, with the line "A model that read the program above computed x = <S_state>." before U).
- **g** = the U-answer implied by A's belief = (S_state + m) % 10. On items where S_state is wrong (W), g differs from the true answer.
- **Time cap:** the item loop stops (logged) after 120 minutes; target total Kaggle wall time under 2.5 h. If it stops early, N is reported as achieved; controls are never dropped.

## Metrics (paired bootstrap 95% CIs over items, 10,000 resamples, seed 0)
1. **New-deduction gain:** Delta_specific = acc(C) - mean_k acc(C_mm,k) on U-answers (all items); C - Rcal; also C - R, C - T, T - Rcal, calibrated versions.
2. **Fidelity (the key PCS number):** on W, **excess = P(C == g) - mean_k P(C_mm,k == g)** (paired), with P(C == g) vs the 1/10 chance reference, and P(R == g), P(Rcal == g), P(T == g) for context. Also: does C_mm,k follow its own wrong cache's implied answer.
3. **Bridge vs text:** C vs T.
4. Diagnostics: agreement C vs C_mm,k, C vs R; digit marginals.

## Decision rule (fixed now)
- **New deduction supported:** lower CI of Delta_specific >= +0.02 **and** lower CI of C - Rcal > 0.
- **Fidelity supported:** lower CI of the excess > 0.
- **Null:** the CIs of Delta_specific and of the excess both include 0.
- **Partial:** anything else. (If both of the first two hold the reading says so explicitly.)

## Safety checks (as in runs 2-3)
Strict projector key check and finite-weight check; fp16 on the T4 gated against an fp32 reference (finite, argmax agreement >= 0.80, mean |dprob| <= 0.10 on R, S, C) with the reference on the CPU (12 probe items, 7-minute cap, >= 8 needed, only if >= 23.6 GiB host RAM is free, else fp16 is accepted on finiteness and logged; fallback bf16 if the gate fails); equal-length assertion on every C2C call and an assertion that a wrong cache differs only inside the fused section; projection-off == receiver argmax on the first 40 items (must be >= 95%, else Part flagged uninterpretable); no non-finite logits. No paper reference exists for this task.

## Known limits (stated now)
One pair, one frozen fuser trained for one-shot QA; a synthetic one-step addition task; A's belief is right on about 93% of items, so the fidelity set is about 200 items (CI half-width on the excess about +-4 pts); no chain of thought (a scratchpad variant is a separate later experiment); depth 2-3 programs are out of A's reach, so only depth 1 is tested; B reads the state from a cache not trained for continuation, so a null may reflect the fuser's training, not the idea. Anything not listed here is post-hoc and will be labelled so. Free Kaggle T4 only; no paid compute.
