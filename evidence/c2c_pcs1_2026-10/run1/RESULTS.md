# Results: C2C fidelity test, run 1 (2026-10-01)

Kaggle T4, fp16 (passed fp32 gate), 26.9 min, $0. Kernel `kaggle-user/pcs-c2c-fidelity` v1. Raw output in `kaggle_out/`.
Pair: receiver Qwen3-0.6B, sharer Qwen2.5-0.5B-Instruct, released fuser `nics-efc/C2C_Fuser/qwen3_0.6b+qwen2.5_0.5b_Fuser/final`.

## Pre-registered results
- **Part A, plumbing: OK.** OpenBookQA N=200, generation readout: receiver 34.0%, sharer 50.0%, C2C 51.5%. The paper reports 39.2 / 45.6 / 52.6. C2C minus receiver is +17.5 pts [+10.5, +25.0]. With projection off, the output matches the plain receiver on 100% of items.
- **Part B, fidelity: NON-SPECIFIC PERTURBATION** (PREREG decision table). N=2000, disagreement set D=858.
  - Overall: C2C 47.9% vs receiver 38.4%.
  - On D, C2C with the real sharer cache scores 43.8%. With a sharer cache computed on a *different question* of the same length (C_mm), it scores 43.9%.
  - Excess inheritance of the sharer's wrong answer: +0.004 [-0.009, +0.017].
- **Part C, planted false belief (exploratory): no transfer.**
  - Sharer adopts the planted letter: +39 pts.
  - Bridge passes it to the receiver: +0.2 pts [-0.4, +0.8].
  - Text handoff of the same note: +15.8 pts.

## Post-hoc checks (not pre-registered; done locally from saved per-item outputs)
- **C2C barely depends on the sharer's input.** On D, the answer with the real sharer cache equals the answer with a wrong-question sharer cache on 97.3% of items. Mean |Δprob| is 0.008.
- **The receiver has a strong letter bias.** It answers "A" 73% of the time; true answers are ~25% each. C2C shifts this distribution.
- **Calibration alone matches C2C.** Removing the receiver's per-letter prior with a 4-number log-prob calibration, 2-fold cross-fit, uses no sharer at all and scores **48.2%** vs C2C **47.9%**.
  - MMLU: receiver 34.4 → calibrated 44.3 vs C2C 42.2.
  - ARC: 43.7 → 52.8 vs 55.0.
  - OBQA: 40.3 → 50.5 vs 51.2.
- **After calibrating both, the sharer still makes no difference on D.** Calibrated C2C minus calibrated C_mm is -0.002 [-0.012, +0.007].

## Reading
For this released tiny pair, under a multiple-choice letter-logit readout, the measured C2C accuracy gain is explained by a generic shift of the receiver's output, most visibly removing its letter-A bias. It is not explained by information about the specific question flowing from the sharer.

Limits:
- One pair, and both models are near chance.
- MC logit readout only; the mismatched control was not run under the generation readout.
- Larger released C2C pairs may behave differently.

So this does **not** refute latent communication in general. It does show that accuracy-only evaluation can credit a bridge with "communication" that a wrong-question control and a calibration baseline reproduce.

## Next
1. Repeat on a larger released C2C pair that fits a T4, with the same controls plus the calibrated-receiver baseline. Add the mismatched control under the generation readout.
2. Make two controls standard in every PCS experiment:
   - the **mismatched-source control** (a source state computed on a different input);
   - a **calibrated-receiver baseline**.
