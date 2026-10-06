# Results: C2C fidelity test, run 2 (2026-10-01)

Kaggle T4, fp16 (passed the fp32 gate), kernel `kaggle-user/pcs-c2c-fidelity-run2` v1, one push, no fixes, $0. Notebook wall time 40.6 min (about 41 min on the T4 session; about 9 of those were setup, dataset download and the CPU fp32 reference, GPU mostly idle). Raw output in `run2/kaggle_out/`.
Pair: receiver Qwen3-1.7B, sharer Qwen2.5-1.5B-Instruct, released fuser `nics-efc/C2C_Fuser/qwen3_1.7b+qwen2.5_1.5b_Fuser/final`. Same 2000 Part B items and 200 Part A items as run 1. `PREREG_run2.md` was frozen before the push (sha256 `6f8c3bb52099333adc285efd35ba159218761ede9f78fcbd527c8b73bb09b37e`, unchanged at collection). Deviations logged by the notebook: none.

## Pre-registered results

- **Part A, plumbing: OK** (PREREG_run2 (f) mechanical criteria). OpenBookQA N=200.
  - No non-finite logits. Projection-off C2C matches the plain receiver on 100% of items. Generation parse rate 100% / 99.5% / 100% / 100% for R / S / C / C_mm_gen.
  - fp16 gate vs an fp32 CPU reference (16 of 16 probe items, 255 s): argmax agreement 1.0 on R, S and C, mean |dprob| at most 0.0008.
  - Informational flag "C2C beats the receiver on OBQA, generation readout": **false**. Generation readout: R 68.0%, S 68.5%, C 65.5%; C - R = -2.5 pts [-7.0, +1.5]. Logit readout: R 67.5%, S 66.5%, C 63.5%; C - R = -4.0 [-8.5, 0.0]. No paper number exists for this pair. By (f), Part B is annotated: *no accuracy gain over the receiver was detected on Part A*.
  - (c) Mismatched sharer under the generation readout: C_mm_gen 65.5% = C_gen 65.5%; C - C_mm_gen = +0.0 [0.0, 0.0]; the two give the same extracted answer on 99.0% of items [97.5, 100].
- **Part B, accuracy (logit readout), N=2000, 98.8% have a same-length partner (D=774; cells A=280, B=332, W=162).**

  | | all items | on D |
  |---|---|---|
  | R receiver alone | 66.6% [64.5, 68.7] | 42.9% |
  | **Rcal** calibrated receiver | 66.3% [64.2, 68.4] | 43.7% |
  | S sharer alone | 64.0% [61.9, 66.1] | 36.2% |
  | **C** C2C | 61.2% [59.1, 63.3] | 41.9% |
  | **C_mm** wrong-question sharer cache | 60.7% (items with a partner; C there: 61.4%) | 41.7% |
  | Ccal (all items) / Ccal and C_mm,cal (partner subset) | 65.8% / 65.9% and 65.4% | 46.9% / 46.3% (C_mm,cal on D with a partner) |
  | T text handoff / T2 with rationale | - | 48.1% / 49.5% |

- **Part B, paired differences (95% CI):**
  - **C - C_mm, all items: +0.007 [+0.001, +0.014]**; on D: +0.005 [-0.005, +0.016].
  - **C - Rcal, all items: -0.051 [-0.070, -0.035]**; on D: -0.018 [-0.047, +0.010].
  - Both calibrated, Ccal - C_mm,cal: all +0.005 [-0.002, +0.012]; on D +0.009 [-0.005, +0.024].
  - C - R: -0.054 [-0.071, -0.037]. Rcal - R: -0.003 [-0.009, +0.004].
- **Per-item answer agreement C vs C_mm (b): 97.1% [96.4, 97.8]** on all items (D 96.7%, cell A 96.7%, B 97.3%, W 95.6%); mean |dprob| 0.008. After calibrating both: 97.4%.
- **Part B reading, PREREG_run2 (e): MIXED / NO CLAIM.** Flags: lower CI of C - C_mm is +0.001, not >= +0.02 (fails); C does not beat calibrated R (it is 5.1 pts below; fails); the C - C_mm CI excludes 0 by 0.1 pt (so "non-specific" fails on that clause); calibrated R is not within 2 pts of C (fails). Neither row holds. I am not relabelling it.
- **Belief-transfer table (carried over): NON-SPECIFIC PERTURBATION.** E_B = +0.006 [-0.006, +0.018]; E_A = +0.019 [+0.004, +0.037]; both inside +-0.05; C - C_mm on D includes 0. Not belief transfer (lower CI of E_B is far below 0.10). Inh(C | B) = 5.7% vs null 4.8%; text handoff 25.0%.
- **(c) consistency label.** The rule's two categories (CI includes 0 / lower CI >= +0.02) do not classify Part B's CI, which excludes 0 by 0.1 pt but is far below +0.02. So I cannot call it consistent or inconsistent by the letter of the rule. Both readouts show at most +0.7 pt; neither reaches +2.
- **Part C, planted false belief (exploratory; ran, 5 min): no transfer.** Sharer effect (planted note vs control) over all 500 items: +54.0 pts [+49.6, +58.2]; the sharer adopted the planted letter (and not under the control) on 270 items. Bridge passes it to the receiver: +0.4 pts [0.0, +1.1] on those 270 items. Text handoff of the same note: +34.2 pts. Mask sanity: masked-pad receiver equals plain receiver with the same position gap on 100% of items.

## Post-hoc checks (not pre-registered; `run2/posthoc_run2.py`, from saved per-item outputs; ties out to the numbers above)

- **The bridge shifts the receiver's letter prior, and here the shift hurts.** The receiver is roughly unbiased (answers A/B/C/D 29/27/20/24%; true answers 24/25/25/26%). C2C answers "A" 44% of the time (C_mm: 45%). Accuracy by true letter, R -> C: A 74 -> 87, B 69 -> 66, C 59 -> 48, D 65 -> 45. After calibration the loss disappears (Ccal 65.8% vs Rcal 66.3%). In run 1 the receiver was the biased one (73% "A") and C2C moved that to 30%, which is why it "helped" there. Same mechanism, opposite sign.
- **Almost everything C2C changes is independent of the sharer's cache.** C differs from R on 20.8% of items; for 94.9% of those, the wrong-question cache C_mm gives the identical changed answer.
- **There is a small real sharer-dependent component.** C and C_mm differ on 57 items (2.9%). Of the items where exactly one is correct, C is right on 28 and C_mm on 14 (two-sided sign test p = 0.044, uncorrected). On those items C moves onto the sharer's answer 29 times vs 9. Net about +0.7 pt, matching C - C_mm. It is detectable but about 3x below the +2 pt bar, and tiny next to the text handoff (when the sharer is right and the receiver wrong, text makes the receiver adopt the sharer's answer 44% of the time; the bridge 9.3% vs 7.4% for the null).
- **By benchmark (descriptive, subgroup looks are uncorrected).** C - C_mm: MMLU +1.4 [+0.3, +2.6], ARC -0.2 [-0.8, +0.3], OBQA +0.3 [-1.3, +1.8]. C - R: MMLU -6.4, ARC -4.7, OBQA -4.0 (all CIs exclude 0).
- **After calibrating both, on D** (S != R): Ccal - Rcal = +3.2 [-0.1, +6.7], but Ccal - C_mm,cal = +0.9 [-0.5, +2.4]. The residual lift on D is not attributable to the sharer's content.
- **Run 1 vs run 2 on the same 2000 items:** C - R was +9.5 pts [+7.0, +11.9] (0.6B <- 0.5B) and is -5.4 [-7.1, -3.7] here (1.7B <- 1.5B). Different receiver, sharer and fuser, so descriptive only.

## Reading
For this released pair, under a multiple-choice letter-logit readout, the bridge **does not lift accuracy**: C2C scores 5.4 pts below the plain receiver and 5.1 pts below a calibrated receiver, and a wrong-question sharer cache scores nearly the same as the real one (agreement 97%). The pre-registered table gives **MIXED / NO CLAIM**: C is not within 2 pts of calibrated R (so the "non-specific" row is not met), and the C - C_mm CI excludes 0 by 0.1 pt. The belief-transfer table gives **non-specific perturbation**, and the planted-premise test finds no transfer.
Put plainly: on this larger pair, again there is no detectable content-specific communication at the pre-registered size (+2 pts), no belief transfer, and nothing the bridge does that a calibrated receiver does not match or beat on all items. The only sharer dependence found is about +0.7 pt.

Limits:
- **This tests a bridge that does not help.** Run 1's bridge had a large accuracy gain to explain; this one has a loss. So run 2 is weaker evidence about "a working bridge" than run 1 was. It cannot separate "this released fuser is poor" from "C2C does not carry content".
- The release's `config.json` lists `num_samples: 5000` but its run name says 500k; how much data this fuser saw is unclear.
- The sharer is not stronger than the receiver here (64.0% vs 66.6%; on D, 36.2% vs 42.9%), so there is less to transmit than with a strong sharer such as Qwen3-4B (not run).
- One pair, one fuser, logit readout for Part B (the generation readout is covered only by Part A's 200 items, where C is also below R), multiple-choice benchmarks only.
- The fp32 gate reference ran on 16 items on the CPU because fp32 does not fit a T4; it agreed on every probe, but it is a small sample.

So this does **not** refute latent communication in general. It adds a second released pair where accuracy-based evaluation, read against a wrong-question control and a calibrated-receiver baseline, finds no content-specific communication.

## Next
1. The strongest remaining test within free compute is a strong sharer into a weak receiver, `qwen3_0.6b+qwen3_4b_Fuser` (fp16 about 10 GB, fits a T4), where there is the most to transmit; run it with the same two controls.
2. Keep both controls standard in every PCS experiment: the mismatched-source control and a calibrated-receiver baseline. Report the plain receiver alongside, since a bridge can lose accuracy as well as gain it.
3. A latent-transfer claim for PCS should be tested on belief or state transfer with text-handoff ceilings, not accuracy alone. Here the text handoff moves the receiver 44% of the time when the sharer is right; the bridge moves it 2 pts beyond a null.

## Files
`PREREG_run2.md` (frozen), `c2c_fidelity_run2.ipynb` (also in `run2/`, byte-identical), `run2/kernel-metadata.json`, `run2/kaggle_out/` (`results.json`, `results_partial.json`, kernel log), `run2/posthoc_run2.py`, `test_analysis.py` (extended, 38 checks pass), `validation_logs/run2_*` (static check, unit tests, smoke runs for both pairs and the CPU-reference gate paths, post-hoc output).
