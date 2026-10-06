# PREREG, run 2: does a larger released C2C pair communicate *content*, or does the bridge just shift the receiver's output?

Written 2026-10-01, after run 1 and before any run-2 result exists, and before the first push to Kaggle. Not edited after the first push; any departure is logged in `results.json["deviations"]` and in `RESULTS_run2.md`. Notebook: `c2c_fidelity_run2.ipynb` (a parametrized copy of `c2c_fidelity.ipynb`).

**Inherited unchanged from `PREREG.md`:** the question, the hypotheses, the item sample (same seeds, so the same items as run 1: 1000 MMLU-Redux + 600 ARC-Challenge + 400 OpenBookQA, +1000 MMLU-Redux reserve used only if |A| or |B| < 150; prompts > 1536 tokens dropped), the readout (argmax over the four letter logits after "The correct answer is", ties to the lower letter), the conditions R, S, S_nat, C, C_mm, T, T2, the disagreement set D = {S != R} and its cells A / B / W, the inheritance metrics and the belief-transfer decision table (reproduced below), Part A (200 OBQA items) and Part C (500 items, exploratory). Greedy, seed 0, no CoT, no thinking, C2C code pinned at commit `3ca0e98`, bootstrap = percentile, 10,000 resamples over items, seed 0, paired where conditions share items. Everything not listed under "Changes" below is as in `PREREG.md`.

## Pair choice (fixed now)

Released fusers in `nics-efc/C2C_Fuser` (read from the HF repo and the C2C README, 2026-10-01), and what each needs in fp16 on one 16 GB Kaggle T4:

| Receiver <- sharer | Tokenizer | fp16 weights (receiver + sharer + fuser) | Verdict |
|---|---|---|---|
| Qwen3-0.6B <- Qwen2.5-0.5B-Instruct | same | ~3 GB | run 1 |
| Qwen3-0.6B <- Qwen3-4B / Qwen3-4B-Base / Qwen3-4B (GSM8K-specific) | same | ~10 GB | fits, but the receiver is run 1's near-chance Qwen3-0.6B; tests a stronger sharer, not a stronger receiver |
| Qwen3-0.6B <- Qwen2.5-Math-1.5B | same | ~5 GB | fits; same weak receiver; math-specialised sharer |
| Qwen3-0.6B <- Llama-3.2-1B-Instruct | different (Llama vs Qwen) | ~4 GB | fits; cross-tokenizer, excluded (the notebook asserts identical option-letter ids and position-aligned inputs) |
| **Qwen3-1.7B <- Qwen2.5-1.5B-Instruct** | **same** | **4.06 + 3.09 + 0.97 = ~8.1 GB** | **chosen** |
| Qwen3-8B <- Qwen2.5-7B-Instruct | same | ~16.4 + 15.2 + 1.3 = ~33 GB | does not fit one T4 in fp16; 8-bit/4-bit would change the model the fuser was trained on |

**Chosen pair: receiver `Qwen/Qwen3-1.7B`, sharer `Qwen/Qwen2.5-1.5B-Instruct`, fuser `nics-efc/C2C_Fuser/qwen3_1.7b+qwen2.5_1.5b_Fuser/final`** (28 projectors, ~971 MB, `is_do_alignment: false`, `mapping: last_aligned`, 28 -> 28 layers; source 2 KV heads x 128, target 8 KV heads x 128). It is the strongest released pair that fits with headroom (about 8 GB of 15 GB), it has a receiver ~3x larger than run 1's and expected to be clearly above chance on MMLU-Redux / ARC-C / OBQA (we report the measured receiver accuracy; the pair is not changed after seeing it), and both models share the Qwen tokenizer, so the existing same-tokenizer path and the option-letter-id assertion apply unchanged.

**Paper numbers for this pair: none are tabulated.** Table 4 of the paper (arXiv 2510.03215, v2) is for receiver Qwen3-0.6B only. Fig. 6 plots only MMLU-Redux accuracy deltas for Qwen3 receivers x Qwen2.5-Instruct sharers, with fusers trained on the MMLU auxiliary-train split, not this OpenHermes-trained release. Part A therefore has no paper reference for this pair (see (f)).

**Known fuser caveat (stated now, not after).** The release's `config.json` for this pair lists `num_samples: 5000` while its `run_name` says "OpenHermes_500k" and `anneal_steps: 1929` (about 500k x 0.99 / 256). How much data this fuser saw is therefore unclear; a weakly trained fuser is a possible reason for a null, and is reported as a limit.

**Notable property of the pair.** The sharer (Qwen2.5-1.5B-Instruct) is expected to be weaker than the receiver on these benchmarks, so there is less for it to transmit than in run 1. The mismatched-sharer and calibration controls are what separate "transmits" from "perturbs".

**Hardware / precision.** Kaggle T4, fp16, gated against fp32 exactly as in run 1 (finite; argmax agreement >= 0.80; mean |dprob| <= 0.10, on R, S and C). fp32 of this stack is ~16 GB and does not fit the GPU, so the fp32 reference runs on the CPU on 16 probe items (cap 10 min; >= 8 items needed for a usable reference). If no usable reference exists, fp16 is accepted on finiteness alone and that is logged as a deviation; if fp16 fails the gate the run falls back to bf16 (emulated on a T4) and logs it.

## Changes relative to `PREREG.md` (each pre-registered here)

**(a) Calibrated-receiver baseline, a primary comparison.**
- Definition. For a condition X in {R, C, C_mm}, let lp_X(i) be the log-softmax of the four letter logits for item i. The scored items are split by a fixed seeded 2-fold split (Python `random.Random("0:calfold")` shuffle of the sorted item ids, alternating assignment; the same split for every condition). For an item in fold k, the calibrated answer is argmax over letters of lp_X(i) minus the per-letter mean of lp_X over the items of the *other* fold (ties to the lower letter). It uses no labels, no sharer, and no item of the same fold. "Calibrated R" (Rcal) is this applied to R.
- Primary comparisons, paired bootstrap 95% CI: acc(C) - acc(Rcal) on **all scored items** and on **D**.
- Also reported: acc(Ccal) - acc(C_mm,cal) on all items with a partner and on D (both conditions calibrated by their own cross-fit prior); acc(Rcal) - acc(R); acc(Ccal) - acc(Rcal).
- Run 1's post-hoc version of this baseline gave 48.2% for the near-chance pair. A re-implementation of the definition above on run 1's saved records (which store only 4-decimal probabilities, so log-probs are clipped at 1e-4) gives 47.8%; run 2 stores unrounded log-probs (5 decimals in log space), so it is not subject to that clipping.

**(b) C_mm on ALL items, not only on D.** Each scored item gets a mismatched-sharer prediction: C2C where the sharer cache is computed on a different prompt of exactly the same token length (receiver-template tokens) and different tokens, drawn uniformly from all 7276 loaded prompts (MMLU-Redux, ARC-C and OBQA pools) with `Random("0:mm:<item id>")`; the receiver sees the real prompt. Items with no such partner are excluded from every comparison involving C_mm; the coverage is reported (expected ~99%). "All items" for C vs C_mm below means all scored items that have a partner. Reported: acc(C) - acc(C_mm) with a paired CI on all items and on D; per-item answer agreement C vs C_mm (all items, D, and cells A / B / W) with bootstrap CIs, plus mean |dprob| per item; and the same agreement after calibrating both.

**(c) Mismatched control under the generation readout.** On the 200 Part A OBQA items, run C2C generation (<= 64 tokens, C2C `extract_answer_from_content`) with the sharer cache from a same-length partner prompt (C_mm_gen) and report acc(C_gen) - acc(C_mm_gen) (paired CI) and per-item answer agreement. This is a consistency check at n = 200 (CI half-width about 4-6 pts): it is labelled *consistent* if it falls in the same category as the Part B logit result (CI includes 0 vs lower CI >= +0.02) and *inconsistent* otherwise. It never overrides the Part B reading.

**(d) Part C only if the time budget allows.** Part C (planted belief, as in `PREREG.md`) runs only if (minutes since the notebook started) + (its measured-timing estimate) <= 150 min when Part B finishes. Otherwise it is dropped and the deviation is logged. Part B's pool is shrunk (floor 600 items, pre-registered order) if the estimated A + B compute exceeds 150 min, and that is logged.

**(e) Thresholds, fixed now.** Evaluated on the Part B logit readout:
| Outcome | Condition |
|---|---|
| **Content-specific communication** | lower CI of acc(C) - acc(C_mm) on all items >= +0.02 **and** lower CI of acc(C) - acc(Rcal) on all items > 0 |
| **Non-specific** | the 95% CI of acc(C) - acc(C_mm) on all items includes 0 **and** calibrated R is within 2 pts of C (point estimates: |acc(C) - acc(Rcal)| <= 0.02) |
| anything else | **Mixed / no claim** |

The two rows cannot both hold. (An equivalence test at +-2 pts is not resolvable at N ~ 2000: the paired CI half-width is about 2-2.6 pts when the two conditions disagree on ~30-40% of items, so "within 2 pts" is a statement about point estimates; the CI is reported next to it.) For scale: a true gain of the +0.02 lower-CI kind needs a true effect of about 3-5 pts; in run 1 the C - C_mm CI on D was +-0.8 pts because C and C_mm agreed on 97% of items.

**(f) Plumbing criteria (new: no paper number exists for this pair).** Part A is "plumbing OK" iff (i) no non-finite logits (counted at the end of Part A; Part B's count is reported too, and any item with a non-finite prediction is excluded from every comparison), (ii) projection-off C2C matches the plain receiver's argmax on >= 95% of Part A items, (iii) the generation parse rate is >= 90% for R, S, C and C_mm_gen. `PREREG.md`'s third criterion (C2C beats the receiver under the generation readout with a CI excluding 0) was tied to the paper's number for run 1's pair; here it is reported as an **informational flag** ("fuser helps on OBQA, generation readout"). If the flag is false the Part B reading is annotated "no accuracy gain over the receiver was detected on Part A", not declared uninterpretable. If any mechanical criterion fails, Part B is flagged uninterpretable as in `PREREG.md`.

**(g) Implementation details that change no hypothesis.** The notebook stores the log-softmax of the four letter logits per prediction; the partner must differ in tokens as well as id; all comparisons list their `n`; the fp32 gate reference runs on the CPU for this pair (above); the strict projector key check, the finiteness check of the cast fuser weights, the projection-off check, the equal-length assertions and the time-budget shrink are kept.

## Metrics (all with paired bootstrap 95% CIs unless noted)

Primary (the two numbers that decide (e), plus the carried-over belief-transfer metric):
1. acc(C) - acc(C_mm), all items with a partner (b).
2. acc(C) - acc(Rcal), all items and D (a).
3. E_B = Inh(C | B) - Inh(C_mm | B) and E_A, E_W, E_{B+W} as in `PREREG.md`, now with C_mm available on ~99% of every cell.

Reported, descriptive: accuracy of R, Rcal, S, S_nat, C, C_mm, Ccal, C_mm,cal, T, T2 overall and on D; answer agreement C vs C_mm; letter marginals; C - R; Ccal - C_mm,cal; Part A readouts. **Anything not listed here is post-hoc and will be labelled as such in `RESULTS_run2.md`.** No multiplicity correction is applied; there are two primary accuracy comparisons in (e) and both must hold for the "content-specific" row.

## Reading (belief-transfer table carried over from `PREREG.md`, unchanged)
| Outcome | Meaning |
|---|---|
| lower CI of E_B >= 0.10 | **Belief transfer**: receiver abandons a correct answer for the sharer's wrong one beyond the C_mm null. |
| E_B upper CI < 0.10 and E_A >= 0.10 | **Truth-biased helper**: follows the sharer only when it is right. |
| E_A, E_B CIs inside +-0.05 and the paired CI of acc(C) - acc(C_mm) on D includes 0 | **Non-specific perturbation**: any accuracy gain is not about the sharer's content. |
| anything else | Mixed or underpowered; no claim. |

The run's headline is the (e) reading (accuracy: content vs non-specific); the table above answers the separate belief-transfer question. Both are reported, and both stand if they disagree.

## Known limits (stated before the run)
One pair, one fuser (training size unclear, see above), a sharer weaker than the receiver, logit readout for Part B (the generation readout is covered only by Part A's 200 items), fp16 gated against a reduced fp32 CPU reference, MC benchmarks only. A null here would not refute latent communication in general; it would show that on this released pair, accuracy-only evaluation credits the bridge with communication that a wrong-question control and a calibration baseline reproduce, or it would show that they do not.

## Compute
Free Kaggle T4 only, at most 3 push attempts (setup failures only; every fix logged as a deviation). No Lightning, Modal, Azure or HF Jobs.
