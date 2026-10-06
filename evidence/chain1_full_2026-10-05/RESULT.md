# CHAIN1 inherit → evolve → pass on (A → B → C): sealed and audited (Claude), 2026-10-05 — NEAR MISS

**Runs.**
- Training run `fc-01M454Y0TDAB7N6PZ2WSDNGCE4` (modal-account-A): 40 epochs, bridge₂ sealed (`a22269d4…`, commitment recorded). It crashed in the old exact-McNemar code (overflow).
- **Evaluation run `fc-01M4612BE585MNKSKT39FY3XPB`** (`--eval-only`): identical sealed bridge₂. B captures and evaluation were recomputed deterministically. No training. Disclosed in the result.

Models: A = Qwen3-4B → (sealed PCS2b bridge) → B = Qwen3-1.7B, which updates the value → bridge₂ → C = a fresh Qwen3-4B. Classification: **CHAIN1_NOT_POSITIVE**.

Test set: 450 states, 4,050 records.

| Criterion (freeze 14) | Value | Pass |
|---|---|---|
| 1. End-to-end fidelity: train-m ≥ 60, held-out ≥ 50 | **99.9% / 46.4%** | ❌ (held-out) |
| 2. A-specificity survives two hops: CHAIN − WRONG-1 ≥ 30, CI > 0, McNemar | **+65.6, CI [63.9, 67.4]**; McNemar about 2,700 vs about 60 | ✅ |
| 3. Hop-2 specificity: CHAIN − WRONG-2 ≥ 20 | **+65.7, CI [63.9, 67.5]** | ✅ |
| 4. A's mistakes pass on (≥ 30 wrong states) | margin +55 but only **16** A-wrong states, below the n-gate | ❌ (n-gate; indicative only) |
| 5. CHAIN − C_restart ≥ 25 | **+53.2, CI [51.2, 55.2]** | ✅ |

**Arms:**
- CHAIN 70.2%, oracle chain 76.1%, token-identity ceiling 99.9%;
- wrong A state at hop 1: about 4.6%; wrong B state at hop 2: about 4.5%;
- zero/random 14–19%, restart 17.0%.

## Audit
1. **A's specific content survives two neural hops and an evolution step.** C, a fresh model that never saw A's context, produces the value derived from *A's* belief, 66 pts above a chain started from a wrong A state. Swapping in the wrong *B* state at hop 2 is equally destructive, so B's evolved state is what carries the content. The chain (70%) comes close to the explicit-text oracle chain (76%).
2. **The single failure is held-out update values** (46.4%). This is the same pattern as PCS7b (48.8%) and X-FAM: bridges trained on m = 1–4 learn partly m-specific mappings. **This is now a cross-experiment finding, and it is the main technical limitation to fix.** Options: train on all m with held-out *programs* instead, or add an m-randomisation objective.
3. **A-mistake transfer:** only 16 A-wrong test states, so the +55 margin is indicative only.

## Provenance probe (Addendum 1; descriptive)
- v_A is decodable from prefix₂ at 87.4% balanced accuracy (chance 10%). v1_A is decodable at 56.9%.
- **The primary lineage probe (A_wrong within (v1_A, m1) strata) found no positive lineage signal.** AUROC was 0.367, *below* the P-only comparator's 0.50. A below-chance AUROC with a within-stratum design probably reflects how strata interact with the fixed effects. It is reported as is and **no lineage claim is made.**

## Allowed claim (descriptive; the pre-registered claim is not made)
"A source model's private state, after being inherited and updated by a second model and passed on through that model's own latent state, drives a third model's answer with +66-point A-specificity across two hops. Generalisation to unseen update values (46%) remains the limitation."
