# Results: PCS1, inherit -> new evidence -> new deduction (2026-10-02)

Kaggle T4, fp16 (passed the fp32 gate on a 12-item CPU reference: argmax agreement 1.0, |dprob| <= 0.0008), kernel `kaggle-user/pcs1-new-deduction` v1, one push, no fixes, $0. Main run 63.3 min notebook wall (item loop 57 min). Raw output `pcs1/kaggle_out/`. `PREREG_pcs1.md` sha256 `1263e28993fcf37d` (full hash in `validation_logs/pcs1_hashes.txt`), frozen before the push; deviations logged by the notebook: none.
Bridge: frozen general fuser Qwen3-4B (A) -> Qwen3-0.6B (B). **This fuser was trained for one-shot QA on identical inputs, not for continuation with new evidence.** Frozen design: addition-only variable programs, **depth 1 only** (pilot v2: S_state 93.0% vs R 7.5%; depths 2 and 3 failed; depth 0 sanity: A reads the stored value 100%), N = 3000, K = 3 same-length wrong-P caches.

## Pre-registered results (N = 3000, A's belief wrong on 224 = 7.5%; chance 10%)
| condition | U-answer accuracy |
|---|---|
| R (B alone, P+U) | 10.5% [9.5, 11.7] |
| Rcal (calibrated) | 9.8% [8.7, 10.9] |
| S_full (A alone, P+U) | 22.7% [21.2, 24.2] |
| S_state (A's belief, P only) | 92.5% [91.6, 93.5] |
| **C** (bridge) | **10.5% [9.4, 11.6]** |
| C_mm (mean of 3 wrong-P caches) | 10.5% [9.5, 11.7] |
| T (text handoff of A's value) | 17.0% [15.7, 18.4] |

- **New-deduction gain:** Delta_specific = acc(C) - mean acc(C_mm,k) = **-0.001 [-0.004, +0.003]**; calibrated both +0.003 [-0.001, +0.007]. **C - Rcal = +0.007 [-0.005, +0.018].** C - R = -0.001.
- **Fidelity** (A's belief wrong, n = 224, g = U-answer implied by A's wrong belief): P(C == g) 6.7% [3.6, 10.3] vs mean P(C_mm,k == g) 6.5%; **excess +0.001 [-0.006, +0.009]**; P(C == g) minus the 1/10 chance reference -0.033 [-0.064, +0.003]. Wrong caches are not followed either: P(C_mm,k == its own implied answer) 10.1% [9.5, 10.6].
- **Bridge vs text:** C - T = -0.065 [-0.079, -0.052]; T - Rcal = +0.072 [+0.058, +0.086].
- Checks: no non-finite logits; projection-off equals the receiver on 100% of the first 40 items.
- **Pre-registered reading: NULL.** Both the Delta_specific CI and the fidelity-excess CI include 0.

## Post-hoc (not pre-registered; `pcs1/posthoc_pcs1.py`, `validation_logs/pcs1_main_posthoc.txt`)
- The bridge does change B's answers: C differs from R on 48% of items. But a wrong-P cache gives the same answer as the right-P cache on 92.6% [91.6, 93.5] of items. The perturbation carries no information about A's state.
- No sign of A's state flowing into B even as a copy: P(C == A's state value) = 11.9%, the same as C_mm (11.9%), and R (12.1%). P(C == true state) is 12.3% for C, C_mm and R alike.
- B itself is a weak receiver for this step: R is at chance on P+U at depth 1, and the text handoff, which states A's value outright, gives only 17.0%. In T, B copies the stated value instead of adding m on 70% of items (P(T == A's value) = 70.1%). So the task has a low ceiling for B even with perfect transfer; the bridge's null sits beside a weak text control, not beside a strong one.
- Part of the headroom exists: T beats Rcal by +7.2 pts [+5.8, +8.6], so the stated value is usable by B, while the cache is not.

## Reading
On this task, the frozen general C2C bridge does **not** let B continue from A's computed state: no new-deduction gain beyond wrong-P caches or a calibrated receiver, no fidelity to A's wrong belief, and no state flow detectable even as a copy. A text handoff of A's value does move B (+7 pts), though weakly.

Limits:
- One pair, one fuser trained for one-shot QA on identical inputs; a null here does not say a bridge trained for continuation would fail.
- Only depth 1 was reachable for A (93% state accuracy; depths 2-3 are out of reach in one forward pass), and B is near chance on the step, so the test is low-ceiling.
- The fidelity set is 224 items (CI half-width about +-1 pt on the excess because all rates are near 6-7%, but little power to see a small effect).
- No chain of thought by design (a scratchpad variant is a separate later experiment). Single-digit readout; synthetic task.

## Kaggle minutes
Main 63.3 min notebook wall. Pilots: v2 4.9 min, v1 6.2 min, plus one setup failure of about 2 min. Total about 77 min, free T4 only.

## Files
`PREREG_pcs1.md`, `RESULTS_pcs1.md`, `RESULTS_pcs1_pilot.md` (pilot v1; v2 table is in the PREREG), `pcs1/` (notebook, metadata, `kaggle_out/`, `posthoc_pcs1.py`), `pcs1_pilot/` (v2 notebook, `kaggle_out/` v2, `kaggle_out_v1/`), `test_pcs1.py` (22 checks), `validation_logs/pcs1_*`.
