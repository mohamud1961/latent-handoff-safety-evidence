# SCALE1 S-UP (Qwen3-8B → Qwen3-4B): sealed and audited (Claude), 2026-10-05 — POSITIVE

**Runs.**
- Training run `fc-01M452T1SEJJ9CF8KMVS8R807P` (L40S, modal-account-B). It trained and selected the bridge, then crashed in `mon2_contract.exact_mcnemar` (an integer-to-float overflow) before writing results.
- **Evaluation run `fc-01M45FSHEPA6N9HTSB3W0ZXVCH`** (`--eval-only`): loaded the identical saved, selected bridge (no retraining or reselection) and re-ran the deterministic test evaluation with the overflow-safe exact McNemar (fix `6e5d761`). Disclosed in the result (`evaluation_re_executed_after_stats_crash: true`).

Protocol: PCS2b exactly, 10 epochs, seed 20261013. Qwen3-8B revision `b968826d…`, Qwen3-4B `1cfa9a72…`. Classification: **SCALE1_SUP_POSITIVE**.

| | PCS | wrong states | restart | zero | fair text handoff | readback | oracle |
|---|---|---|---|---|---|---|---|
| all m | **87.8%** | 1.4–1.6% | 10.8% | 11.6% | 83.5% | 99.6% | 92.8% |
| train m | 90.4% | ~1% | 11.2% | 12.0% | 92.8% | 99.6% | 95.7% |
| **held-out m** | **85.6%** | ~2% | 10.4% | 11.3% | 76.0% | 99.6% | 90.4% |

- **State-specific fidelity: +86.2 pts, CI [82.6, 89.6]** (256 state clusters).
- **Held-out-m specificity: +83.6.**
- Source-mistake excess: +97.5, but on only **6 source-wrong states**. Treat it as indicative only.
- **All 11 PCS2b criteria pass, including beating the fair text handoff.**

## Audit
1. **The effect strengthens with scale.**
   - PCS2b (4B → 1.7B): 87% fidelity.
   - S-UP (8B → 4B): 87.8%, with near-zero wrong-state fidelity and a larger margin over text on held-out updates (85.6% vs 76.0%).
2. The eval-only re-execution is legitimate: same sealed bridge, deterministic greedy decoding, statistics fixed only in an overflow-safe exact form.
3. **Limitation:** A (8B) made very few errors (6 states), so the mistake-transfer claim at this scale is indicative only.

## Allowed claim
"A larger source's private computed state (Qwen3-8B) transfers through a learned latent bridge to a different frozen model (Qwen3-4B) with 86-point state specificity. It generalises to unseen update values and beats a fair text handoff."
