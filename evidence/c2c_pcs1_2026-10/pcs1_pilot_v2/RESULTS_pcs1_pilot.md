# PCS1 pilot (2026-10-02): can Qwen3-4B (A) derive the state in one forward pass?

Kaggle T4, fp16, kernel `kaggle-user/pcs1-pilot` v2 (v1 failed in setup on a missing config key, fixed, no results lost), notebook wall 6.2 min, $0. Raw output `pcs1_pilot/kaggle_out/`. Only R and A were run; no fuser, no C, as specified. No PREREG_pcs1.md was frozen, because no depth qualified.

Task: program P of three initial digit assignments plus d update steps `x = (y * k + z) % 10` (a dependency chain; k in 1..9), then new evidence U = `Now e = (x * k' + m) % 10. What is e?` (k' in {1,3,7,9}; answer differs from every final variable value). Readout: logits over the ten digit tokens after "The answer is ", thinking off, no CoT. 200 items per depth, same seeds for all conditions.

| depth | n | R (P+U) | Rcal (P+U) | R_state (P only) | S_full (P+U) | S_state (P only) | S_state - R | qualifies |
|---|---|---|---|---|---|---|---|---|
| 1 | 200 | 7.0% [3.5, 11.0] | 8.5% | 14.5% | 15.0% | 23.5% [18.0, 29.5] | +16.5 | no |
| 2 | 200 | 13.5% [9.0, 18.5] | 17.5% | 15.0% | 14.5% | 14.5% [10.0, 19.5] | +1.0 | no |
| 3 | 200 | 18.0% [12.5, 23.5] | 19.0% | 8.5% | 7.5% | 9.5% [5.5, 13.5] | -8.5 | no |
| 4 | 200 | 17.0% [12.0, 22.5] | 19.0% | 8.5% | 13.0% | 13.5% [9.0, 18.5] | -3.5 | no |
| 6 | 200 | 16.0% [11.0, 21.0] | 22.0% | 6.5% | 10.0% | 14.0% [9.5, 19.0] | -2.0 | no |

Chance is 10%. **No depth qualifies** (rule: S_state - R >= 20 pts and S_state >= 60%). Even at depth 1, A's own state answer is 23.5%. By the instruction, I stopped here.

## Reading
A (Qwen3-4B) cannot derive the state of this program in a forward pass, so there is no A belief to inherit and a PCS1 test on this task would be uninterpretable (B would have nothing correct to receive; "A's belief is wrong" would be the typical case, not the informative one).

## Post-hoc diagnostics (not pre-registered; from saved records, `validation_logs/pcs1_posthoc.txt`)
- The blocker is the multiplication, not the readout or the format. At depth 1, A's state accuracy is 53.6% (n=28) when the step multiplier is 1 (pure addition `x = (y + z) % 10`), 14.5% (n=62) for k in 2..4 and 20.9% (n=110) for k in 5..9. That is a post-hoc subgroup on a small n, but it points to modular multiplication.
- A's answers are heavily biased toward even digits (2: 28%, 6: 32%, 8: 14%) while true values are near uniform, another sign it is guessing on the hard items.
- No non-finite logits; the readout tokens are single, identical digit tokens in both tokenizers (checked at load).

## What I validated before the pilot
Static checks, unit tests (`test_pcs1.py`, 22 checks: program semantics, the constraint that the U-answer differs from every variable, K=3 same-length wrong-P partners with distinct values of the queried variable, U never in the fused section, analysis and decision rule on synthetic data) and CPU smoke runs of both notebooks with tiny random models. The main notebook (`pcs1/pcs1_new_deduction.ipynb`, MODE=main) exists and passes smoke; it was not pushed.

## Options (needs a decision, not made here)
1. Redesign the update rule so one forward pass can do it: addition-only updates (`x = (y + z) % 10`, possibly with a small set of constants), where depth 1 is already 54%. Re-run the pilot at d in {1,2,3}; the same pre-registered pipeline then applies.
2. A depth-0 control (read a stored value) to confirm the pipeline end to end at about 100%; cheap, worth adding to option 1.
3. Give A a short scratchpad (CoT) when forming its state; this changes "A's cognition is its forward pass over P", so it is a design change for you to approve.
